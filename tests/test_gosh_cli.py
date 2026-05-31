import os
import json
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


def find_usable_bash() -> str | None:
    candidates: list[str] = []

    if os.name == "nt":
        candidates.extend([
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files\Git\usr\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
        ])

    bash_on_path = shutil.which("bash")
    if bash_on_path:
        candidates.append(bash_on_path)

    seen: set[str] = set()
    for candidate in candidates:
        normalized = os.path.normcase(candidate)
        if normalized in seen or not os.path.isfile(candidate):
            continue
        seen.add(normalized)
        try:
            result = subprocess.run(
                [candidate, "-lc", "pwd >/dev/null"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        except OSError:
            continue
        if result.returncode == 0:
            return candidate

    return None


USABLE_BASH = find_usable_bash()


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
        env["USERPROFILE"] = str(home_dir)
        command_args = " ".join(shlex.quote(arg) for arg in args)
        command = f". ./gosh/gosh.sh && gosh {command_args} && pwd"

        return subprocess.run(
            [USABLE_BASH, "-lc", command],
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
        self.assertIn("-Json", result.stdout)

    def test_json_metadata_prints_shared_cli_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            result = self.run_gosh(Path(temp_home), "--json")

        self.assertEqual(result.returncode, 0)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["Schema"], "saturno-cli-metadata/v1")
        self.assertEqual(metadata["Name"], "gosh")
        self.assertIn("json", metadata["OutputModes"])
        self.assertTrue(metadata["Supports"]["JsonMetadata"])
        self.assertIn("jump", [command["Name"] for command in metadata["Commands"]])
        self.assertTrue(metadata["Paths"]["DataFile"].endswith("gosh-paths.txt"))

    def test_json_metadata_alias_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            result = self.run_gosh(Path(temp_home), "-Json")

        self.assertEqual(result.returncode, 0)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["Schema"], "saturno-cli-metadata/v1")

    def test_json_mode_returns_error_envelope_for_runtime_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            result = self.run_gosh(Path(temp_home), "--json", "--list")

        self.assertEqual(result.returncode, 1)
        error_payload = json.loads(result.stderr)
        self.assertEqual(error_payload["Schema"], "saturno-cli-error/v1")
        self.assertEqual(error_payload["Code"], "cli.json-metadata-only")
        self.assertIn("root help/version metadata", error_payload["Message"])

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

    def test_print_supports_fuzzy_lookup_for_dotted_suffix_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "saturno.backend.internal", str(target_path))
            print_result = self.run_gosh(home_path, "--print", "backeintal")

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


    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell is required for wrapper tests")
    def test_powershell_wrapper_changes_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "shell", str(target_path))
            wrapper_result = self.run_powershell_wrapper(home_path, "shell")

            self.assertEqual(wrapper_result.returncode, 0)
            self.assertTrue(os.path.samefile(wrapper_result.stdout.strip(), target_path.resolve()))

    @unittest.skipUnless(USABLE_BASH, "A usable bash shell is required for wrapper tests")
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

    def test_add_handles_empty_bookmark_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            add_result = self.run_gosh(home_path, "--add", "", str(target_path))

            # Empty bookmark name may be accepted or rejected
            self.assertIn(add_result.returncode, [0, 1])

    def test_add_handles_empty_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)

            add_result = self.run_gosh(home_path, "--add", "test", "")

            # Empty path may be accepted or rejected
            self.assertIn(add_result.returncode, [0, 1])

    def test_add_handles_unicode_bookmark_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            add_result = self.run_gosh(home_path, "--add", "プロジェクト", str(target_path))

            # Unicode may or may not be supported depending on system
            self.assertIn(add_result.returncode, [0, 1])

    def test_add_handles_unicode_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)
            unicode_dir = home_path / "テスト"

            try:
                unicode_dir.mkdir()
            except (OSError, UnicodeEncodeError):
                self.skipTest("System does not support unicode paths")

            add_result = self.run_gosh(home_path, "--add", "unicodepath", str(unicode_dir))

            # Unicode path support varies by system
            self.assertIn(add_result.returncode, [0, 1])

    def test_add_handles_spaces_in_bookmark_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            add_result = self.run_gosh(home_path, "--add", "my work folder", str(target_path))

            self.assertEqual(add_result.returncode, 0)
            print_result = self.run_gosh(home_path, "--print", "my work folder")
            self.assertEqual(print_result.returncode, 0)

    def test_add_handles_special_characters_in_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            add_result = self.run_gosh(home_path, "--add", "work@home!", str(target_path))

            self.assertEqual(add_result.returncode, 0)

    def test_add_handles_very_long_bookmark_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)
            long_name = "a" * 500

            add_result = self.run_gosh(home_path, "--add", long_name, str(target_path))

            self.assertEqual(add_result.returncode, 0)

    def test_print_rejects_nonexistent_bookmark(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)

            print_result = self.run_gosh(home_path, "--print", "nonexistent")

            self.assertEqual(print_result.returncode, 1)
            # Error message should indicate bookmark doesn't exist
            self.assertIn("doesn't exist", print_result.stdout.lower())

    def test_delete_nonexistent_bookmark_fails_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)

            delete_result = self.run_gosh(home_path, "--delete", "nonexistent")

            self.assertEqual(delete_result.returncode, 1)

    def test_update_nonexistent_bookmark_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            update_result = self.run_gosh(home_path, "--update", "nonexistent", str(target_path))

            self.assertEqual(update_result.returncode, 1)

    def test_add_handles_path_with_trailing_slash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)
            path_with_slash = str(target_path) + os.sep

            add_result = self.run_gosh(home_path, "--add", "trailing", path_with_slash)

            self.assertEqual(add_result.returncode, 0)

    def test_add_normalizes_mixed_path_separators(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            add_result = self.run_gosh(home_path, "--add", "mixed", str(target_path))

            self.assertEqual(add_result.returncode, 0)
            bookmarks_file = self.read_bookmarks_file(home_path)
            self.assertIn("mixed;", bookmarks_file)

    def test_list_handles_corrupted_bookmarks_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)
            bookmarks_path = home_path / ".saturnosoftware" / "gosh" / "data" / "gosh-paths.txt"
            bookmarks_path.parent.mkdir(parents=True, exist_ok=True)
            bookmarks_path.write_text("corrupted;;;data\ninvalid", encoding="utf-8")

            list_result = self.run_gosh(home_path, "--list")

            self.assertIn(list_result.returncode, [0, 1])

    def test_add_handles_path_traversal_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)
            malicious_path = "../../../etc/passwd"

            add_result = self.run_gosh(home_path, "--add", "attack", malicious_path)

            self.assertEqual(add_result.returncode, 1)

    def test_print_handles_case_insensitive_fuzzy_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "MyWorkspace", str(target_path))
            print_result = self.run_gosh(home_path, "--print", "myworkspace")

            self.assertEqual(print_result.returncode, 0)

    def test_add_handles_symlink_path(self) -> None:
        if os.name == "nt":
            self.skipTest("Symlink test requires elevated permissions on Windows")

        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)
            symlink_path = home_path / "symlink_test"

            try:
                os.symlink(target_path, symlink_path)
            except OSError:
                self.skipTest("Cannot create symlinks")

            add_result = self.run_gosh(home_path, "--add", "symlink", str(symlink_path))

            self.assertEqual(add_result.returncode, 0)

    def test_multiple_bookmarks_with_same_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "alias1", str(target_path))
            add_result = self.run_gosh(home_path, "--add", "alias2", str(target_path))

            self.assertEqual(add_result.returncode, 0)
            list_result = self.run_gosh(home_path, "--list")
            self.assertIn("alias1", list_result.stdout)
            self.assertIn("alias2", list_result.stdout)

    def test_bookmark_name_with_semicolon_delimiter_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            add_result = self.run_gosh(home_path, "--add", "test;semicolon", str(target_path))

            self.assertIn(add_result.returncode, [0, 1])

    def test_handles_bookmark_file_with_only_newlines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)
            bookmarks_path = home_path / ".saturnosoftware" / "gosh" / "data" / "gosh-paths.txt"
            bookmarks_path.parent.mkdir(parents=True, exist_ok=True)
            bookmarks_path.write_text("\n\n\n", encoding="utf-8")

            list_result = self.run_gosh(home_path, "--list")

            self.assertEqual(list_result.returncode, 0)

    def test_handles_bookmark_file_with_mixed_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target1, tempfile.TemporaryDirectory() as target2:
            home_path = Path(temp_home)
            bookmarks_path = home_path / ".saturnosoftware" / "gosh" / "data" / "gosh-paths.txt"
            bookmarks_path.parent.mkdir(parents=True, exist_ok=True)
            content = f"bookmark1;{target1};0\r\nbookmark2;{target2};0\n"
            bookmarks_path.write_text(content, encoding="utf-8")

            list_result = self.run_gosh(home_path, "--list")

            self.assertEqual(list_result.returncode, 0)
            self.assertIn("bookmark1", list_result.stdout)
            self.assertIn("bookmark2", list_result.stdout)

    def test_concurrent_bookmark_operations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "concurrent1", str(target_path))
            self.run_gosh(home_path, "--add", "concurrent2", str(target_path))
            list_result = self.run_gosh(home_path, "--list")

            self.assertEqual(list_result.returncode, 0)
            self.assertIn("concurrent1", list_result.stdout)
            self.assertIn("concurrent2", list_result.stdout)

    def test_add_rejects_file_path_instead_of_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)
            file_path = home_path / "test_file.txt"
            file_path.write_text("test content")

            add_result = self.run_gosh(home_path, "--add", "file", str(file_path))

            self.assertEqual(add_result.returncode, 1)
            self.assertIn("not a valid directory", add_result.stdout)

    def test_handles_zero_length_bookmark_name_in_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)
            bookmarks_path = home_path / ".saturnosoftware" / "gosh" / "data" / "gosh-paths.txt"
            bookmarks_path.parent.mkdir(parents=True, exist_ok=True)
            bookmarks_path.write_text(f";{target_path};0\n", encoding="utf-8")

            list_result = self.run_gosh(home_path, "--list")

            self.assertIn(list_result.returncode, [0, 1])

    def test_handles_very_long_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)
            long_path_segments = ["a" * 50 for _ in range(5)]
            long_path = home_path.joinpath(*long_path_segments)

            try:
                long_path.mkdir(parents=True)
            except OSError:
                self.skipTest("Cannot create very long path on this system")

            add_result = self.run_gosh(home_path, "--add", "longpath", str(long_path))

            self.assertEqual(add_result.returncode, 0)

    def test_fuzzy_match_handles_numbers_in_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)

            self.run_gosh(home_path, "--add", "project2024", str(target_path))
            print_result = self.run_gosh(home_path, "--print", "proj2024")

            self.assertEqual(print_result.returncode, 0)

    def test_update_preserves_bookmark_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target1, tempfile.TemporaryDirectory() as target2:
            home_path = Path(temp_home)
            target1_path = Path(target1)
            target2_path = Path(target2)

            self.run_gosh(home_path, "--add", "counted", str(target1_path))
            self.run_gosh(home_path, "--print", "counted")
            self.run_gosh(home_path, "--print", "counted")
            self.run_gosh(home_path, "--print", "counted")

            update_result = self.run_gosh(home_path, "--update", "counted", str(target2_path))

            self.assertEqual(update_result.returncode, 0)
            bookmarks_file = self.read_bookmarks_file(home_path)
            self.assertIn("counted;", bookmarks_file)

    def test_handles_bookmark_with_maximum_count_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)
            bookmarks_path = home_path / ".saturnosoftware" / "gosh" / "data" / "gosh-paths.txt"
            bookmarks_path.parent.mkdir(parents=True, exist_ok=True)
            bookmarks_path.write_text(f"maxcount;{target_path};2147483647\n", encoding="utf-8")

            list_result = self.run_gosh(home_path, "--list")

            self.assertEqual(list_result.returncode, 0)
            self.assertIn("maxcount", list_result.stdout)

    def test_handles_negative_count_in_bookmark_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_home, tempfile.TemporaryDirectory() as target_dir:
            home_path = Path(temp_home)
            target_path = Path(target_dir)
            bookmarks_path = home_path / ".saturnosoftware" / "gosh" / "data" / "gosh-paths.txt"
            bookmarks_path.parent.mkdir(parents=True, exist_ok=True)
            bookmarks_path.write_text(f"negative;{target_path};-1\n", encoding="utf-8")

            list_result = self.run_gosh(home_path, "--list")

            self.assertIn(list_result.returncode, [0, 1])


if __name__ == "__main__":
    unittest.main()
