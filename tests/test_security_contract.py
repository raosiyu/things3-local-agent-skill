from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "things3.py"
SOURCE = SCRIPT.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class SecurityContractTests(unittest.TestCase):
    def test_no_known_database_or_network_imports(self) -> None:
        forbidden_roots = {
            "sqlite3",
            "requests",
            "httpx",
            "aiohttp",
            "socket",
            "urllib.request",
        }
        imported = set()
        for node in ast.walk(TREE):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        for forbidden in forbidden_roots:
            self.assertNotIn(forbidden, imported)

    def test_no_shell_true_eval_or_exec(self) -> None:
        self.assertNotIn("shell=True", SOURCE)
        names = {
            node.func.id
            for node in ast.walk(TREE)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("eval", names)
        self.assertNotIn("exec", names)

    def test_no_delete_backup_restore_export_subcommands(self) -> None:
        for word in ("delete", "backup", "restore", "export"):
            self.assertNotIn(f'add_parser("{word}"', SOURCE)

    def test_no_auth_token_runtime_parameter(self) -> None:
        self.assertNotIn('"auth-token"', SOURCE)
        self.assertNotIn("'auth-token'", SOURCE)


if __name__ == "__main__":
    unittest.main()
