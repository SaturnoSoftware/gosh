import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GOSH_SCRIPT = REPO_ROOT / "gosh" / "gosh2.py"
GOSH_BASH_WRAPPER = REPO_ROOT / "gosh" / "gosh.sh"
GOSH_POWERSHELL_WRAPPER = REPO_ROOT / "gosh" / "gosh.ps1"


class GoshCliTests(unittest.TestCase):
    def run_gosh(self, home_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(home_dir)
        env["USERPROFILE"] = str(home_dir)

        return subprocess.run(
            [sys.executable, str(GOSH_SCRIPT), *args],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def read_bookmarks_file(self, home_dir: Path) -> str:
        bookmarks_path = home_dir / ".saturnosoftware" / "gosh" / "data" / "gosh-paths.txt"
        if not bookmarks_path.exists():
            return ""
        return bookmarks_path.read_text(encoding="utf-8")

    def write_legacy_bookmarks_file(self, home_dir: Path, content: str) -> Path:
        bookmarks_path = home_dir / ".mateusdigital" / "config" / "gosh" / "gosh-paths.txt"
        bookmarks_path.parent.mkdir(parents=True, exist_ok=True)
        bookmarks_path.write_text(content, encoding="utf-8")
        return bookmarks_path

    def run_powershell_wrapper(self, home_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(home_dir)
        env["USERPROFILE"] = str(home_dir)

        quoted_args = " ".join("'" + arg.replace("'", "''") + "'" for arg in args)
        command = f"& '{GOSH_POWERSHELL_WRAPPER}' {quoted_args}; (Get-Location).Path"

        return subprocess.run(
            ["pwsh", "-NoProfile", "-Command", command],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_bash_wrapper(self, home_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(home_dir)
        command_args = " ".join(shlex.quote(arg) for arg in args)
        command = f". ./gosh/gosh.sh && gosh {command_args} && pwd"

        return subprocess.run(
            ["bash", "-lc", command],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

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
        printed_path = print_result.stdout.strip().replace("\\", "/").lower()
        self.assertTrue(os.path.isabs(print_result.stdout.strip()))
        self.assertTrue(printed_path.endswith(f"/{target_path.resolve().name.lower()}"))

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

    def test_add_rejects_invalid_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)
            invalid_path = home_path / "missing-dir"

            add_result = self.run_gosh(home_path, "--add", "broken", str(invalid_path))
            bookmarks_file = self.read_bookmarks_file(home_path)

        self.assertEqual(add_result.returncode, 1)
        self.assertIn("[FATAL] Path (", add_result.stdout)
        self.assertIn("is not a valid directory", add_result.stdout)
        self.assertEqual(bookmarks_file, "")

    def test_print_supports_fuzzy_name_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "workspace", str(target_path))
            print_result = self.run_gosh(home_path, "--print", "wrkspace")

            self.assertEqual(print_result.returncode, 0)
            self.assertTrue(os.path.samefile(print_result.stdout.strip(), target_path.resolve()))

    def test_update_changes_bookmark_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as original_dir, tempfile.TemporaryDirectory() as updated_dir:
            home_path = Path(temp_home)
            original_path = Path(original_dir)
            updated_path = Path(updated_dir)

            self.run_gosh(home_path, "--add", "notes", str(original_path))
            update_result = self.run_gosh(home_path, "--update", "notes", str(updated_path))
            print_result = self.run_gosh(home_path, "--print", "notes")
            bookmarks_file = self.read_bookmarks_file(home_path)

            self.assertEqual(update_result.returncode, 0)
            self.assertIn("Bookmark updated:", update_result.stdout)
            self.assertTrue(os.path.samefile(print_result.stdout.strip(), updated_path.resolve()))
            stored_path = bookmarks_file.strip().split(";")[1]
            self.assertTrue(os.path.samefile(stored_path, updated_path.resolve()))

    def test_legacy_bookmarks_file_is_migrated_to_saturno_data_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir).resolve().as_posix()
            legacy_path = self.write_legacy_bookmarks_file(home_path, f"legacy;{target_path};0\n")

            list_result = self.run_gosh(home_path, "--list")
            bookmarks_file = home_path / ".saturnosoftware" / "gosh" / "data" / "gosh-paths.txt"
            migrated_content = bookmarks_file.read_text(encoding="utf-8")
            legacy_exists = legacy_path.exists()

        self.assertEqual(list_result.returncode, 0)
        self.assertIn("legacy", list_result.stdout)
        self.assertFalse(legacy_exists)
        self.assertEqual(migrated_content, f"legacy;{target_path};0\n")

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell is required for wrapper tests")
    def test_powershell_wrapper_changes_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "shell", str(target_path))
            wrapper_result = self.run_powershell_wrapper(home_path, "shell")

            self.assertEqual(wrapper_result.returncode, 0)
            self.assertTrue(os.path.samefile(wrapper_result.stdout.strip(), target_path.resolve()))

    @unittest.skipUnless(shutil.which("bash"), "Bash is required for wrapper tests")
    def test_bash_wrapper_changes_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "shell", str(target_path))
            wrapper_result = self.run_bash_wrapper(home_path, "shell")

            self.assertEqual(wrapper_result.returncode, 0)
            output_lines = [line.strip() for line in wrapper_result.stdout.splitlines() if line.strip()]
            self.assertGreaterEqual(len(output_lines), 1)
            if output_lines[0].startswith("[gosh] "):
                self.assertEqual(output_lines[0].replace("[gosh] ", "", 1), output_lines[-1])
            self.assertTrue(output_lines[-1].replace("\\", "/").lower().endswith(target_path.name.lower()))


if __name__ == "__main__":
    unittest.main()
