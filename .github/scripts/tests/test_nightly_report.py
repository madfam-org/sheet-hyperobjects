"""Run: python -m unittest discover -s .github/scripts/tests -v

The nightly's verdict: each of its independent conditions turns a night red on its own, and a missing input is red.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location("nightly_report", Path(__file__).resolve().parents[1] / "nightly_report.py")
nr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(nr)


def row(slug: str, documents: int = 2, runs: int | None = None, rc: int = 0, verify_errors: int = 0) -> dict:
    return {"slug": slug, "rc": rc, "runs": documents if runs is None else runs, "documents": documents,
            "verify_errors": verify_errors}


def spec_log(files: list[str], failing: tuple[str, ...] = ()) -> str:
    lines = [f"  FAIL {f}: rule 3 broken" if f in failing else f"  ok {f} (sheet-document)" for f in files]
    lines.append(f"pliego-spec check: contract=sheet-document files={len(files)} failures={len(failing)} "
                 "sheets=1 vertices=4 edges=4 faces=1 joins=0 geometry=NOT verified")
    return "\n".join(lines) + "\n"


SCOPE = ["alpha", "beta"]
DOCS = ["c/alpha/alpha.a.fold", "c/alpha/alpha.b.fold", "c/beta/beta.a.fold", "c/beta/beta.b.fold"]


def green_inputs():
    return SCOPE, {"rows": [row("alpha"), row("beta")]}, spec_log(DOCS), "success"


class VerdictTest(unittest.TestCase):
    def test_green_when_every_condition_holds(self):
        result = nr.verdict(*green_inputs())
        self.assertTrue(result["green"], result["problems"])
        self.assertEqual(result["counts"]["documents"], 4)
        self.assertEqual(result["counts"]["spec_files"], 4)

    def test_sweep_job_not_success_is_red(self):
        scope, corpus, log, _ = green_inputs()
        result = nr.verdict(scope, corpus, log, "failure")
        self.assertFalse(result["green"])
        self.assertIn("`failure`", result["problems"][0])

    def test_incomplete_corpus_is_red_and_names_the_cartridge(self):
        scope, _, _, ok = green_inputs()
        log = spec_log(DOCS[:2])
        result = nr.verdict(scope, {"rows": [row("alpha")]}, log, ok)
        self.assertFalse(result["green"])
        self.assertTrue(any(p.startswith("NEVER BUILT beta") for p in result["problems"]), result["problems"])

    def test_cartridge_row_with_a_failure_is_red(self):
        for bad in (row("beta", rc=1), row("beta", verify_errors=3), row("beta", documents=1, runs=2),
                    row("beta", documents=0, runs=0), row("beta", rc=-1)):
            with self.subTest(bad=bad):
                docs = DOCS[:2] + DOCS[2:2 + bad["documents"]]
                result = nr.verdict(SCOPE, {"rows": [row("alpha"), bad]}, spec_log(docs), "success")
                self.assertFalse(result["green"])
                self.assertTrue(any(p.startswith("FAIL beta:") for p in result["problems"]), result["problems"])

    def test_spec_failure_row_is_red_even_if_the_summary_was_lost(self):
        log = spec_log(DOCS, failing=(DOCS[3],))
        result = nr.verdict(SCOPE, {"rows": [row("alpha"), row("beta")]}, log, "success")
        self.assertFalse(result["green"])
        self.assertIn(f"FAIL {DOCS[3]}: pliego-spec check sheet-document", result["problems"])
        no_summary = "\n".join(line for line in log.splitlines() if not line.startswith("pliego-spec check:"))
        result = nr.verdict(SCOPE, {"rows": [row("alpha"), row("beta")]}, no_summary, "success")
        self.assertFalse(result["green"])
        self.assertTrue(any("0 sheet-document summary lines" in p for p in result["problems"]))

    def test_spec_checked_fewer_files_than_built_is_red(self):
        result = nr.verdict(SCOPE, {"rows": [row("alpha"), row("beta")]}, spec_log(DOCS[:3]), "success")
        self.assertFalse(result["green"])
        self.assertTrue(any("files=3" in p and "documents=4" in p for p in result["problems"]), result["problems"])

    def test_summary_without_rows_is_red(self):
        log = spec_log(DOCS).splitlines()[-1] + "\n"
        result = nr.verdict(SCOPE, {"rows": [row("alpha"), row("beta")]}, log, "success")
        self.assertFalse(result["green"])
        self.assertTrue(any(p.startswith("pliego-spec rows: ok=0") for p in result["problems"]), result["problems"])

    def test_missing_inputs_are_red_never_silent(self):
        result = nr.verdict(None, None, None, "success")
        self.assertFalse(result["green"])
        self.assertEqual(len(result["problems"]), 3)
        result = nr.verdict([], {"rows": []}, "", "success")
        self.assertFalse(result["green"])


class MainTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="nightly-"))
        scope, corpus, log, _ = green_inputs()
        (self.dir / "scope.txt").write_text("\n".join(scope) + "\n")
        (self.dir / "corpus.json").write_text(json.dumps(corpus))
        (self.dir / "spec.log").write_text(log)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_main(self, *extra: str) -> tuple[int, str]:
        argv = ["--scope", str(self.dir / "scope.txt"), "--corpus", str(self.dir / "corpus.json"),
                "--spec-log", str(self.dir / "spec.log"), "--sweep-result", "success", *extra]
        buf = io.StringIO()
        env = {k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_STEP_SUMMARY")}
        with mock.patch.dict(os.environ, env, clear=True), contextlib.redirect_stdout(buf):
            code = nr.main(argv)
        return code, buf.getvalue()

    def test_exit_code_is_the_verdict(self):
        code, out = self.run_main("--no-issue")
        self.assertEqual(code, 0, out)
        self.assertIn("verdict=green", out)
        (self.dir / "corpus.json").unlink()
        code, out = self.run_main("--no-issue")
        self.assertEqual(code, 1)
        self.assertIn("verdict=red", out)
        self.assertIn("::error title=nightly render sweep::corpus.json is missing", out)

    def test_api_failure_never_changes_the_verdict(self):
        with mock.patch.object(nr, "report", side_effect=nr.urllib.error.URLError("down")), \
                mock.patch.dict(os.environ, {"GH_TOKEN": "x"}):
            buf = io.StringIO()
            argv = ["--scope", str(self.dir / "scope.txt"), "--corpus", str(self.dir / "corpus.json"),
                    "--spec-log", str(self.dir / "spec.log"), "--sweep-result", "success", "--repo", "o/r"]
            with contextlib.redirect_stdout(buf):
                code = nr.main(argv)
        self.assertEqual(code, 0)
        self.assertIn("could not be written", buf.getvalue())


class IssueTest(unittest.TestCase):
    """The issue path against a fake API: red opens or rewrites, green closes."""

    def fake(self, open_issue):
        calls = []

        def call(_self, method, path, payload=None):
            calls.append((method, path, payload))
            if method == "GET" and "/issues?" in path:
                return [open_issue] if open_issue else []
            if method == "GET" and "/labels/" in path:
                return {"name": nr.LABEL}
            if method == "POST" and path.endswith("/issues"):
                return {"number": 7}
            return {}
        return calls, call

    def test_red_opens_one_issue_with_the_label(self):
        calls, call = self.fake(None)
        red = nr.verdict(SCOPE, None, None, "failure")
        with mock.patch.object(nr.GitHub, "call", call), contextlib.redirect_stdout(io.StringIO()):
            nr.report(red, "o/r", "t", "https://run", "2026-10-18")
        made = [c for c in calls if c[0] == "POST" and c[1] == "/repos/o/r/issues"]
        self.assertEqual(len(made), 1)
        self.assertEqual(made[0][2]["labels"], [nr.LABEL])

    def test_red_with_an_open_issue_rewrites_it(self):
        calls, call = self.fake({"number": 5})
        red = nr.verdict(SCOPE, None, None, "failure")
        with mock.patch.object(nr.GitHub, "call", call), contextlib.redirect_stdout(io.StringIO()):
            nr.report(red, "o/r", "t", "", "2026-10-18")
        self.assertIn(("PATCH", "/repos/o/r/issues/5"), [(c[0], c[1]) for c in calls])
        self.assertFalse(any(c[1] == "/repos/o/r/issues" for c in calls))

    def test_green_closes_the_open_issue(self):
        calls, call = self.fake({"number": 5})
        with mock.patch.object(nr.GitHub, "call", call), contextlib.redirect_stdout(io.StringIO()):
            nr.report(nr.verdict(*green_inputs()), "o/r", "t", "", "2026-10-18")
        self.assertIn(("PATCH", "/repos/o/r/issues/5", {"state": "closed"}), calls)


if __name__ == "__main__":
    unittest.main()
