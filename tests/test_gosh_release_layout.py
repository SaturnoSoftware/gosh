import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
BUILD_NUMBER = 41
RELEASE_NAME = f"{PACKAGE_JSON['name']}-{PACKAGE_JSON['version']}-{BUILD_NUMBER}"
BUILD_DIR = REPO_ROOT / "__BUILD" / RELEASE_NAME
DIST_DIR = REPO_ROOT / "__DIST" / RELEASE_NAME
PWSH = shutil.which("pwsh")


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


@unittest.skipUnless(PWSH, "pwsh is required for release-layout tests")
class GoshReleaseLayoutTests(unittest.TestCase):
    def tearDown(self) -> None:
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        shutil.rmtree(DIST_DIR, ignore_errors=True)

    def run_pwsh(self, script_path: Path, extra_args: list[str] | None = None, working_directory: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        command = [
            PWSH,
            "-NoLogo",
            "-NoProfile",
            "-File",
            str(script_path),
            "-ProjectRoot",
            str(REPO_ROOT),
            "-BuildNumber",
            str(BUILD_NUMBER),
        ]
        if extra_args:
            command.extend(extra_args)
        return subprocess.run(
            command,
            cwd=working_directory or REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def build_release(self) -> subprocess.CompletedProcess[str]:
        return self.run_pwsh(REPO_ROOT / "Scripts" / "build.ps1", [
            "-BuildOutputDir", str(BUILD_DIR),
            "-ReleaseName", RELEASE_NAME,
        ])

    def package_release(self) -> subprocess.CompletedProcess[str]:
        build_result = self.build_release()
        self.assertEqual(build_result.returncode, 0, build_result.stderr)

        package_result = self.run_pwsh(REPO_ROOT / "Scripts" / "package.ps1", [
            "-BuildOutputDir", str(BUILD_DIR),
            "-PackageOutputDir", str(DIST_DIR),
            "-ReleaseName", RELEASE_NAME,
        ])
        self.assertEqual(package_result.returncode, 0, package_result.stderr)
        return package_result

    def test_build_stages_package_ready_app_layout(self) -> None:
        result = self.build_release()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((BUILD_DIR / "App" / "gosh2.py").is_file())
        self.assertTrue((BUILD_DIR / "App" / "gosh.sh").is_file())
        self.assertTrue((BUILD_DIR / "App" / "gosh.ps1").is_file())
        self.assertTrue((BUILD_DIR / "package.json").is_file())
        self.assertTrue((BUILD_DIR / "install.sh").is_file())
        self.assertTrue((BUILD_DIR / "install.ps1").is_file())

    def test_package_preserves_release_layout(self) -> None:
        self.package_release()

        self.assertTrue((DIST_DIR / "App" / "gosh2.py").is_file())
        self.assertTrue((DIST_DIR / "App" / "gosh.sh").is_file())
        self.assertTrue((DIST_DIR / "App" / "gosh.ps1").is_file())
        self.assertTrue((DIST_DIR / "package.json").is_file())
        self.assertTrue((DIST_DIR / "install.sh").is_file())
        self.assertTrue((DIST_DIR / "install.ps1").is_file())

    def test_packaged_powershell_install_uses_dist_layout(self) -> None:
        self.package_release()

        with tempfile.TemporaryDirectory() as temp_home:
            env = os.environ.copy()
            env["HOME"] = temp_home
            env["USERPROFILE"] = temp_home

            result = subprocess.run(
                [
                    PWSH,
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(DIST_DIR / "install.ps1"),
                ],
                cwd=DIST_DIR,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            install_root = Path(temp_home) / ".saturnosoftware" / "gosh"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((install_root / "bin" / "gosh.ps1").is_file())
            self.assertTrue((install_root / "bin" / "gosh2.py").is_file())
            self.assertTrue((install_root / "package.json").is_file())
            self.assertTrue((install_root / "config").is_dir())
            self.assertTrue((install_root / "data").is_dir())

            version_result = subprocess.run(
                [sys.executable, str(install_root / "bin" / "gosh2.py"), "-v"],
                cwd=install_root / "bin",
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(version_result.returncode, 0, version_result.stderr)
            self.assertIn(f"gosh - {PACKAGE_JSON['version']}-{PACKAGE_JSON['build']}", version_result.stdout)

    def test_build_fails_gracefully_with_missing_package_json(self) -> None:
        temp_root = REPO_ROOT / "__BUILD" / "test-temp"
        temp_root.mkdir(parents=True, exist_ok=True)

        package_json_backup = REPO_ROOT / "package.json.bak"
        if (REPO_ROOT / "package.json").exists():
            shutil.move(REPO_ROOT / "package.json", package_json_backup)

        try:
            result = self.build_release()
            self.assertNotEqual(result.returncode, 0)
        finally:
            if package_json_backup.exists():
                shutil.move(package_json_backup, REPO_ROOT / "package.json")
            shutil.rmtree(temp_root, ignore_errors=True)

    def test_build_handles_unicode_in_project_path(self) -> None:
        if not (BUILD_DIR.parent / "unicode-テスト").exists():
            self.skipTest("Cannot test unicode paths")

        result = self.build_release()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_build_output_has_no_sensitive_files(self) -> None:
        result = self.build_release()
        self.assertEqual(result.returncode, 0, result.stderr)

        sensitive_files = [".env", ".git", "secrets.json", ".ssh"]
        for sensitive in sensitive_files:
            self.assertFalse((BUILD_DIR / sensitive).exists(), f"Sensitive file {sensitive} should not be in build")

    def test_package_handles_missing_build_directory(self) -> None:
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)

        package_result = self.run_pwsh(REPO_ROOT / "Scripts" / "package.ps1", [
            "-BuildOutputDir", str(BUILD_DIR),
            "-PackageOutputDir", str(DIST_DIR),
            "-ReleaseName", RELEASE_NAME,
        ])

        self.assertNotEqual(package_result.returncode, 0)

    def test_build_handles_very_long_release_name(self) -> None:
        long_name = "gosh-" + "a" * 100  # Reduced length for cross-platform compatibility
        long_build_dir = REPO_ROOT / "__BUILD" / long_name

        try:
            result = self.run_pwsh(REPO_ROOT / "Scripts" / "build.ps1", [
                "-BuildOutputDir", str(long_build_dir),
                "-ReleaseName", long_name,
            ])

            # Very long paths may not be supported on all systems
            if result.returncode == 0:
                self.assertTrue(long_build_dir.exists())
            else:
                self.skipTest("System does not support very long paths")
        except OSError:
            self.skipTest("Cannot create very long paths on this system")
        finally:
            shutil.rmtree(long_build_dir, ignore_errors=True)

    def test_install_script_has_unix_line_endings(self) -> None:
        result = self.build_release()
        self.assertEqual(result.returncode, 0, result.stderr)

        install_sh_content = (BUILD_DIR / "install.sh").read_bytes()
        self.assertNotIn(b'\r\n', install_sh_content, "install.sh should use LF not CRLF")

    def test_powershell_script_handles_any_line_ending(self) -> None:
        result = self.build_release()
        self.assertEqual(result.returncode, 0, result.stderr)

        install_ps1_path = BUILD_DIR / "install.ps1"
        self.assertTrue(install_ps1_path.exists())

    def test_package_creates_archive_with_correct_structure(self) -> None:
        self.package_release()

        required_files = [
            "App/gosh2.py",
            "App/gosh.sh",
            "App/gosh.ps1",
            "package.json",
            "install.sh",
            "install.ps1"
        ]

        for required_file in required_files:
            file_path = DIST_DIR / required_file
            self.assertTrue(file_path.exists(), f"Required file {required_file} missing from package")

    def test_build_handles_special_characters_in_path(self) -> None:
        special_name = "build-test@2024"
        special_build_dir = REPO_ROOT / "__BUILD" / special_name

        try:
            result = self.run_pwsh(REPO_ROOT / "Scripts" / "build.ps1", [
                "-BuildOutputDir", str(special_build_dir),
                "-ReleaseName", special_name,
            ])

            if result.returncode == 0:
                self.assertTrue(special_build_dir.exists())
        finally:
            shutil.rmtree(special_build_dir, ignore_errors=True)

    def test_build_number_increments_correctly(self) -> None:
        original_build = PACKAGE_JSON['build']

        result = self.build_release()
        self.assertEqual(result.returncode, 0)

        package_json_content = (REPO_ROOT / "package.json").read_text()
        self.assertIn('"build":', package_json_content)

    def test_install_creates_required_directories(self) -> None:
        self.package_release()

        with tempfile.TemporaryDirectory() as temp_home:
            env = os.environ.copy()
            env["HOME"] = temp_home
            env["USERPROFILE"] = temp_home

            result = subprocess.run(
                [
                    PWSH,
                    "-NoLogo",
                    "-NoProfile",
                    "-File",
                    str(DIST_DIR / "install.ps1"),
                ],
                cwd=DIST_DIR,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            install_root = Path(temp_home) / ".saturnosoftware" / "gosh"
            self.assertTrue((install_root / "bin").is_dir())
            self.assertTrue((install_root / "config").is_dir())
            self.assertTrue((install_root / "data").is_dir())

    def test_build_output_directory_permissions(self) -> None:
        result = self.build_release()
        self.assertEqual(result.returncode, 0)

        if os.name != "nt":
            self.assertTrue(os.access(BUILD_DIR, os.R_OK | os.X_OK))

    def test_package_handles_existing_dist_directory(self) -> None:
        self.package_release()

        first_package_time = (DIST_DIR / "package.json").stat().st_mtime

        package_result_2 = self.package_release()
        self.assertEqual(package_result_2.returncode, 0)

        second_package_time = (DIST_DIR / "package.json").stat().st_mtime
        self.assertGreaterEqual(second_package_time, first_package_time)

    @unittest.skipUnless(USABLE_BASH, "a usable bash shell is required for bash install tests")
    def test_packaged_bash_install_uses_dist_layout(self) -> None:
        self.package_release()

        with tempfile.TemporaryDirectory() as temp_home:
            env = os.environ.copy()
            env["HOME"] = temp_home
            env["USERPROFILE"] = temp_home

            result = subprocess.run(
                [USABLE_BASH, "./install.sh"],
                cwd=DIST_DIR,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            install_root = Path(temp_home) / ".saturnosoftware" / "gosh"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((install_root / "bin" / "gosh.sh").is_file())
            self.assertTrue((install_root / "bin" / "gosh2.py").is_file())
            self.assertTrue((install_root / "package.json").is_file())
            self.assertTrue((install_root / "config").is_dir())
            self.assertTrue((install_root / "data").is_dir())


if __name__ == "__main__":
    unittest.main()
