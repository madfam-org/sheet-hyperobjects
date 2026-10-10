"""Run: python -m unittest discover -s .github/scripts/tests -v"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("check_triple", Path(__file__).resolve().parents[1] / "check_triple.py")
triple = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(triple)


def run(*argv: str) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = triple.main(list(argv))
    return code, buf.getvalue()


class TripleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="triple-"))
        (self.root / "docs").mkdir()
        (self.root / "README.md").write_text("x")

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def cartridge(self, slug: str, main: bool = True, readme: bool = True) -> Path:
        d = self.root / slug
        (d / "docs").mkdir(parents=True)
        (d / "project.json").write_text("{}")
        if main:
            (d / "main.py").write_text("")
        if readme:
            (d / "docs" / "README.md").write_text("x")
        return d

    def test_complete_cartridge_passes(self) -> None:
        self.cartridge("page-turn")
        code, out = run("--root", str(self.root), "--min-cartridges", "1")
        self.assertEqual(code, 0, out)
        self.assertIn("cartridges=1", out)

    def test_zero_cartridges_reported_and_fails_on_minimum(self) -> None:
        code, out = run("--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertIn("cartridges=0", out)
        self.assertEqual(run("--root", str(self.root), "--min-cartridges", "1")[0], 1)

    def test_defects_fail(self) -> None:
        self.cartridge("no-main", main=False)
        self.cartridge("no-readme", readme=False)
        self.cartridge("Bad_Slug")
        (self.cartridge("licensed") / "LICENSE.txt").write_text("x")
        orphan = self.root / "orphan"
        orphan.mkdir()
        (orphan / "main.py").write_text("")
        code, out = run("--root", str(self.root))
        self.assertEqual(code, 1)
        for needle in ("no-main/: project.json without main.py", "no-readme/: project.json without docs/README.md",
                       "Bad_Slug/: slug is not strict kebab", "licensed/LICENSE.txt", "orphan/: main.py without project.json"):
            self.assertIn(needle, out)


if __name__ == "__main__":
    unittest.main()
