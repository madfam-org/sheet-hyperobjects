#!/usr/bin/env python3
"""The nightly render sweep's verdict, and the one tracking issue that carries a red night to a human.

The nightly (.github/workflows/nightly.yml) builds every cartridge's sheet documents in every mode and preset with
the Pliego kernel at PLIEGO_PIN (Pliego's scripts/qa/sim_corpus.py, which writes `corpus.json`), then runs
`pliego-spec check sheet-document` at SPEC_PIN over every document it built. This script reads what those two
steps WROTE, not what their jobs concluded, and decides. Green needs ALL of:

1. the sweep job finished `success`;
2. completeness: every cartridge in the scope (every `*/project.json` on the ref) has a corpus row;
3. every corpus row is clean: rc 0, verify errors 0, documents == kernel runs, and at least one document;
4. the pliego-spec summary line is present, reports `failures=0`, and its `files` equals the corpus documents;
5. the spec log has one `ok` row per checked file and no `FAIL` or `ERROR` row.

They are independent on purpose: a verdict with one point of failure is how a sweep goes green while its own log
says red (the solid commons' run 34023334942). A missing or unreadable input is red, never "nothing to report".

Then, with a token: a red night opens the issue labelled `nightly-render` (or rewrites its body and adds a comment
when one is open); a green night closes it with a comment. The exit code is the verdict (1 red, 0 green). A failing
GitHub API call prints a `::warning::` and never changes the exit code: the alert path must not turn a green sweep
red, and a red sweep stays red in the run whether or not the issue could be written.

    python3 .github/scripts/nightly_report.py --scope scope.txt --corpus corpus.json --spec-log spec.log \
        --sweep-result success [--repo owner/name --run-url URL]     (GH_TOKEN in the environment)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LABEL = "nightly-render"
TITLE = "Nightly render sweep is red"
SUMMARY = re.compile(r"^pliego-spec check: contract=sheet-document files=(\d+) failures=(\d+)\b")
OK_ROW = re.compile(r"^\s+ok \S+ \(sheet-document\)$")
BAD_ROW = re.compile(r"^\s+(FAIL|ERROR) (\S+?):")
MAX_LISTED = 40


def read_scope(path: str) -> list[str] | None:
    try:
        return sorted({s.strip() for s in Path(path).read_text(encoding="utf-8").splitlines() if s.strip()})
    except OSError:
        return None


def read_corpus(path: str) -> dict | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) and isinstance(data.get("rows"), list) else None


def read_text(path: str) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def verdict(scope: list[str] | None, corpus: dict | None, spec_log: str | None, sweep_result: str) -> dict:
    """Every problem found, and the counts. Green iff `problems` is empty."""
    problems: list[str] = []
    counts = {"scope": len(scope or []), "cartridges": 0, "documents": 0, "spec_files": None, "spec_failures": None}
    if sweep_result != "success":
        problems.append(f"the sweep job finished `{sweep_result or 'unknown'}`, not `success`")
    if not scope:
        problems.append("the scope list is missing or empty: completeness cannot be checked")
    if corpus is None:
        problems.append("corpus.json is missing or unreadable: no cartridge was proven built")
        rows = []
    else:
        rows = [r for r in corpus["rows"] if isinstance(r, dict)]
    counts["cartridges"] = len(rows)
    counts["documents"] = sum(int(r.get("documents") or 0) for r in rows)
    seen = {str(r.get("slug")) for r in rows}
    for slug in sorted(set(scope or []) - seen):
        problems.append(f"NEVER BUILT {slug}: in the scope, no corpus row")
    for r in sorted(rows, key=lambda r: str(r.get("slug"))):
        slug, docs, runs = r.get("slug"), int(r.get("documents") or 0), int(r.get("runs") or 0)
        why = []
        if r.get("rc") != 0:
            why.append(f"rc={r.get('rc')}")
        if int(r.get("verify_errors") or 0):
            why.append(f"verify-errors={r.get('verify_errors')}")
        if docs != runs:
            why.append(f"documents={docs} runs={runs}")
        if docs == 0:
            why.append("no documents")
        if why:
            problems.append(f"FAIL {slug}: {' '.join(why)} (see {slug}.log in the artifact)")
    if spec_log is None:
        problems.append("the pliego-spec log is missing: no document was checked against the keystone")
    else:
        summary = [SUMMARY.match(line) for line in spec_log.splitlines()]
        summary = [m for m in summary if m]
        ok_rows = sum(1 for line in spec_log.splitlines() if OK_ROW.match(line))
        bad_files = sorted({m.group(2) for m in map(BAD_ROW.match, spec_log.splitlines()) if m})
        if len(summary) != 1:
            problems.append(f"the pliego-spec log has {len(summary)} sheet-document summary lines, expected 1")
        else:
            files, failures = int(summary[0].group(1)), int(summary[0].group(2))
            counts["spec_files"], counts["spec_failures"] = files, failures
            if failures:
                problems.append(f"pliego-spec: failures={failures} of files={files}")
            if files != counts["documents"]:
                problems.append(f"pliego-spec checked files={files}, the corpus built documents={counts['documents']}")
            if ok_rows + len(bad_files) != files:
                problems.append(f"pliego-spec rows: ok={ok_rows} failing={len(bad_files)}, summary files={files}")
        for f in bad_files:
            problems.append(f"FAIL {f}: pliego-spec check sheet-document")
    return {"green": not problems, "problems": problems, "counts": counts}


def summary_markdown(result: dict, run_url: str, date: str) -> str:
    c = result["counts"]
    head = "green" if result["green"] else "RED"
    lines = [f"### Nightly render sweep: {head} ({date})", "",
             f"`scope={c['scope']} cartridges={c['cartridges']} documents={c['documents']} "
             f"spec-files={c['spec_files']} spec-failures={c['spec_failures']} problems={len(result['problems'])}`", ""]
    for p in result["problems"][:MAX_LISTED]:
        lines.append(f"- {p}")
    if len(result["problems"]) > MAX_LISTED:
        lines.append(f"- … and {len(result['problems']) - MAX_LISTED} more (the run log lists every one)")
    if run_url:
        lines += ["", f"Run: {run_url}"]
    return "\n".join(lines) + "\n"


class GitHub:
    def __init__(self, repo: str, token: str):
        self.repo, self.token = repo, token

    def call(self, method: str, path: str, payload: dict | None = None):
        req = urllib.request.Request(
            f"https://api.github.com{path}", method=method,
            data=None if payload is None else json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "sheet-hyperobjects-nightly"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
        return json.loads(body) if body else None

    def ensure_label(self) -> None:
        try:
            self.call("GET", f"/repos/{self.repo}/labels/{LABEL}")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            self.call("POST", f"/repos/{self.repo}/labels",
                      {"name": LABEL, "color": "B60205", "description": "The nightly render sweep is red"})

    def open_issue(self) -> dict | None:
        found = self.call("GET", f"/repos/{self.repo}/issues?state=open&labels={LABEL}&per_page=1")
        return found[0] if found else None


def report(result: dict, repo: str, token: str, run_url: str, date: str) -> None:
    """Open, update or close the tracking issue. Raises on API failure; the caller only warns."""
    api = GitHub(repo, token)
    issue = api.open_issue()
    body = summary_markdown(result, run_url, date)
    if result["green"]:
        if issue:
            api.call("POST", f"/repos/{repo}/issues/{issue['number']}/comments",
                     {"body": f"Green again on {date}: every cartridge built and every document passed.\n\n{body}"})
            api.call("PATCH", f"/repos/{repo}/issues/{issue['number']}", {"state": "closed"})
            print(f"nightly-report: closed #{issue['number']}")
        else:
            print("nightly-report: green, no open tracking issue")
        return
    intro = ("The nightly render sweep (.github/workflows/nightly.yml) is red. This issue is rewritten on every red "
             "night and closed by the next green one.\n\n")
    if issue:
        api.call("PATCH", f"/repos/{repo}/issues/{issue['number']}", {"body": intro + body})
        api.call("POST", f"/repos/{repo}/issues/{issue['number']}/comments",
                 {"body": f"Still red on {date}: {len(result['problems'])} problem(s). {run_url}".strip()})
        print(f"nightly-report: updated #{issue['number']}")
    else:
        api.ensure_label()
        made = api.call("POST", f"/repos/{repo}/issues", {"title": TITLE, "body": intro + body, "labels": [LABEL]})
        print(f"nightly-report: opened #{made['number']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scope", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--spec-log", required=True)
    ap.add_argument("--sweep-result", required=True)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    ap.add_argument("--run-url", default="")
    ap.add_argument("--no-issue", action="store_true", help="decide and print only; never touch the issue")
    a = ap.parse_args(argv)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = verdict(read_scope(a.scope), read_corpus(a.corpus), read_text(a.spec_log), a.sweep_result)
    text = summary_markdown(result, a.run_url, date)
    print(text, end="")
    for p in result["problems"]:
        print(f"::error title=nightly render sweep::{p}")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text)
    token = os.environ.get("GH_TOKEN", "")
    if a.no_issue:
        print("nightly-report: --no-issue, the tracking issue was not touched")
    elif not (token and a.repo):
        print("::warning::nightly-report: no GH_TOKEN or repository, the tracking issue was not touched")
    else:
        try:
            report(result, a.repo, token, a.run_url, date)
        except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError) as exc:
            print(f"::warning::nightly-report: the tracking issue could not be written ({exc}); the verdict stands")
    print(f"nightly-report: verdict={'green' if result['green'] else 'red'} problems={len(result['problems'])}")
    return 0 if result["green"] else 1


if __name__ == "__main__":
    sys.exit(main())
