import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GOSH_SCRIPT = REPO_ROOT / "gosh" / "gosh2.py"


class GoshCliTests(unittest.TestCase):
    def run_gosh(self, home_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(home_dir)

        return subprocess.run(
            [sys.executable, str(GOSH_SCRIPT), *args],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def read_bookmarks_file(self, home_dir: Path) -> str:
        bookmarks_path = home_dir / ".mateusdigital" / "config" / "gosh" / "gosh-paths.txt"
        if not bookmarks_path.exists():
            return ""
        return bookmarks_path.read_text(encoding="utf-8")

    def test_help_prints_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            result = self.run_gosh(Path(temp_home), "--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)
        self.assertIn("gosh -a <name> <path>", result.stdout)

    def test_add_and_print_bookmark(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            add_result = self.run_gosh(home_path, "--add", "work", str(target_path))
            print_result = self.run_gosh(home_path, "--print", "work")
            bookmarks_file = self.read_bookmarks_file(home_path)

        self.assertEqual(add_result.returncode, 0)
        self.assertIn("Bookmark added:", add_result.stdout)
        self.assertIn("work", add_result.stdout)

        self.assertEqual(print_result.returncode, 0)
        self.assertEqual(print_result.stdout.strip(), target_path.resolve().as_posix())

        self.assertIn("work;", bookmarks_file)
        self.assertIn(";1", bookmarks_file)

    def test_delete_existing_bookmark(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "trash", str(target_path))
            delete_result = self.run_gosh(home_path, "--delete", "trash")
            list_result = self.run_gosh(home_path, "--list")

        self.assertEqual(delete_result.returncode, 0)
        self.assertIn("Bookmark deleted:", delete_result.stdout)
        self.assertIn("(trash)", delete_result.stdout)
        self.assertIn("No bookmarks yet", list_result.stdout)


if __name__ == "__main__":
    unittest.main()
