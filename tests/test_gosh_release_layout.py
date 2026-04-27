import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
BUILD_NUMBER = 41
RELEASE_NAME = f"{PACKAGE_JSON['name']}-{PACKAGE_JSON['version']}-{BUILD_NUMBER}"
BUILD_DIR = REPO_ROOT / "__BUILD" / RELEASE_NAME
DIST_DIR = REPO_ROOT / "__DIST" / RELEASE_NAME


class GoshReleaseLayoutTests(unittest.TestCase):
    def tearDown(self) -> None:
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        shutil.rmtree(DIST_DIR, ignore_errors=True)

    def run_pwsh(self, script_path: Path, working_directory: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        command = [
            "pwsh",
            "-NoLogo",
            "-NoProfile",
            "-File",
            str(script_path),
            "-ProjectRoot",
            str(REPO_ROOT),
            "-BuildNumber",
            str(BUILD_NUMBER),
        ]
        return subprocess.run(
            command,
            cwd=working_directory or REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def build_release(self) -> subprocess.CompletedProcess[str]:
        return self.run_pwsh(REPO_ROOT / "Scripts" / "build.ps1")

    def package_release(self) -> subprocess.CompletedProcess[str]:
        build_result = self.build_release()
        self.assertEqual(build_result.returncode, 0, build_result.stderr)

        package_result = self.run_pwsh(REPO_ROOT / "Scripts" / "package.ps1")
        self.assertEqual(package_result.returncode, 0, package_result.stderr)
        return package_result

    def test_build_stages_package_ready_app_layout(self) -> None:
        result = self.build_release()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((BUILD_DIR / "App" / "gosh2.py").is_file())
        self.assertTrue((BUILD_DIR / "App" / "gosh.sh").is_file())
        self.assertTrue((BUILD_DIR / "App" / "gosh.ps1").is_file())
        self.assertTrue((BUILD_DIR / "install.sh").is_file())
        self.assertTrue((BUILD_DIR / "install.ps1").is_file())

    def test_package_preserves_release_layout(self) -> None:
        self.package_release()

        self.assertTrue((DIST_DIR / "App" / "gosh2.py").is_file())
        self.assertTrue((DIST_DIR / "App" / "gosh.sh").is_file())
        self.assertTrue((DIST_DIR / "App" / "gosh.ps1").is_file())
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
                    "pwsh",
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

            install_root = Path(temp_home) / ".mateusdigital" / "bin"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((install_root / "gosh.ps1").is_file())
            self.assertTrue((install_root / "gosh_" / "gosh2.py").is_file())

    @unittest.skipUnless(shutil.which("bash") and os.name != "nt", "bash install test requires Unix-like bash")
    def test_packaged_bash_install_uses_dist_layout(self) -> None:
        self.package_release()

        with tempfile.TemporaryDirectory() as temp_home:
            env = os.environ.copy()
            env["HOME"] = temp_home
            env["USERPROFILE"] = temp_home

            result = subprocess.run(
                ["bash", "./install.sh"],
                cwd=DIST_DIR,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            install_root = Path(temp_home) / ".mateusdigital" / "bin"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((install_root / "gosh.sh").is_file())
            self.assertTrue((install_root / "gosh_" / "gosh2.py").is_file())


if __name__ == "__main__":
    unittest.main()
