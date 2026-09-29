from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "things3.py"

spec = importlib.util.spec_from_file_location("things3_local", SCRIPT)
assert spec and spec.loader
things3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(things3)


class UrlTests(unittest.TestCase):
    def test_spaces_are_percent_encoded(self) -> None:
        url = things3.build_url("search", {"query": "Reality RPG"})
        self.assertEqual(url, "things:///search?query=Reality%20RPG")

    def test_unicode_is_percent_encoded(self) -> None:
        url = things3.build_url("add", {"title": "今日主线"})
        self.assertTrue(url.startswith("things:///add?title="))
        self.assertNotIn("今日主线", url)

    def test_boolean_is_lowercase(self) -> None:
        url = things3.build_url("add", {"title": "x", "reveal": True})
        self.assertIn("reveal=true", url)


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_version(self) -> None:
        proc = self.run_cli("--version")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("0.2.0", proc.stdout)

    def test_add_dry_run_has_no_live_dependency(self) -> None:
        proc = self.run_cli(
            "add",
            "--title",
            "Things Skill Test",
            "--when",
            "today",
            "--dry-run",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            proc.stdout.strip(),
            "things:///add?title=Things%20Skill%20Test&when=today",
        )

    def test_show_allowlist(self) -> None:
        good = self.run_cli("show", "today", "--dry-run")
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(good.stdout.strip(), "things:///show?id=today")

        bad = self.run_cli("show", "../../evil", "--dry-run")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("Unsupported built-in list id", bad.stderr)

    def test_live_read_fails_closed_off_macos(self) -> None:
        if sys.platform == "darwin":
            self.skipTest("This assertion is specifically for non-macOS CI.")
        proc = self.run_cli("read", "--source", "project", "--name", "Reality RPG")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("require macOS", proc.stderr)


if __name__ == "__main__":
    unittest.main()
