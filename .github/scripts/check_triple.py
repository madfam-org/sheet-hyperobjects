#!/usr/bin/env python3
"""The cartridge triple, the slug grammar and the no-stray-licence rule.

* every root directory holding a `project.json` has `main.py` and `docs/README.md`;
* every root directory holding a `main.py` has a `project.json` (no orphan generators);
* every cartridge slug matches `^[a-z0-9]+(-[a-z0-9]+)*$` and is 2-80 characters;
* no `LICENSE`, `LICENCE` or `COPYING` file exists at any depth inside a cartridge.

Read-proof: prints how many directories and cartridges it read. Zero cartridges is reported, and
fails with `--min-cartridges N` (N > 0); the root files are never mistaken for a cartridge.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NOT_CARTRIDGES = {".git", ".github", "docs", "scripts"}
LICENCE_NAMES = {"LICENSE", "LICENCE", "COPYING"}


def check(root: Path) -> tuple[list[str], int, int]:
    errors: list[str] = []
    dirs = sorted(p for p in root.iterdir() if p.is_dir() and p.name not in NOT_CARTRIDGES and not p.name.startswith("."))
    cartridges = 0
    for d in dirs:
        has_manifest, has_main = (d / "project.json").is_file(), (d / "main.py").is_file()
        if not has_manifest:
            if has_main:
                errors.append(f"{d.name}/: main.py without project.json (orphan generator)")
            continue
        cartridges += 1
        if not has_main:
            errors.append(f"{d.name}/: project.json without main.py")
        if not (d / "docs" / "README.md").is_file():
            errors.append(f"{d.name}/: project.json without docs/README.md")
        if not (SLUG.match(d.name) and 2 <= len(d.name) <= 80):
            errors.append(f"{d.name}/: slug is not strict kebab case (^[a-z0-9]+(-[a-z0-9]+)*$, 2-80 chars)")
        for f in sorted(d.rglob("*")):
            if f.is_file() and f.name.split(".")[0].upper() in LICENCE_NAMES:
                errors.append(f"{f.relative_to(root)}: no per-cartridge licence file (the root LICENSE covers it)")
    return errors, len(dirs), cartridges


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--min-cartridges", type=int, default=0)
    args = ap.parse_args(argv)
    errors, dirs, cartridges = check(Path(args.root).resolve())
    if cartridges < args.min_cartridges:
        errors.append(f"cartridges={cartridges} < required {args.min_cartridges}")
    print(f"triple: dirs={dirs} cartridges={cartridges} errors={len(errors)}")
    for err in errors:
        print(f"  FAIL {err}")
    print("triple: " + ("FAIL" if errors else "OK"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
