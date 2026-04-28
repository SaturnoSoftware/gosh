# Architecture

## Snapshot

- Status: legacy small CLI under modernization
- Product name: gosh
- Repo type: cross-shell CLI utility
- Runtime/platform:
  - Python core
  - Bash wrapper
  - PowerShell wrapper
- Main entry points:
  - `gosh/gosh2.py`
  - `gosh/gosh.sh`
  - `gosh/gosh.ps1`
  - `install.sh`
  - `install.ps1`
  - `Scripts/build.ps1`
  - `Scripts/package.ps1`
- Deployment target: user shell environment after installation under
  `~/.saturnosoftware/gosh/`
- Release payload shape: package-ready `App/` directory plus root install scripts inside
  `__BUILD/<release-name>/` and `__DIST/<release-name>/`
- Persistence/storage: bookmarks file under
  `~/.saturnosoftware/gosh/data/gosh-paths.txt`
- Machine-local install layout:
  - `~/.saturnosoftware/gosh/bin`
  - `~/.saturnosoftware/gosh/config`
  - `~/.saturnosoftware/gosh/data`
- Logging/debug posture: plain console output only
- Test runner: Python `unittest`
- CI/CD platform: GitHub Actions (`.github/workflows/test.yml`)

## Purpose

- What this system does: stores named directory bookmarks and resolves them from shell
  wrappers.
- Why it exists: to make repeated navigation to frequently used directories faster.
- What the main user flow is:
  1. install `gosh`
  2. add bookmarks
  3. call `gosh <name>` from a shell
  4. shell wrapper changes directory or prints action output

## Repository Map

| Path | Responsibility | Notes |
| --- | --- | --- |
| `gosh/gosh2.py` | Core bookmark logic and CLI parsing | Python runtime center |
| `gosh/gosh.sh` | Bash wrapper | Changes shell directory on success |
| `gosh/gosh.ps1` | PowerShell wrapper | Changes shell directory on success |
| `install.sh` | Bash install path | Installs from packaged `App/` payload or the legacy repo layout |
| `install.ps1` | PowerShell install path | Installs from packaged `App/` payload or the legacy repo layout |
| `Scripts/build.ps1` | Saturno build entrypoint | Stages a package-ready `App/` payload under `__BUILD/` |
| `Scripts/package.ps1` | Saturno package entrypoint | Preserves the package-ready release layout under `__DIST/` |
| `tests/test_gosh_cli.py` | First committed regression surface | Black-box subprocess CLI coverage |
| `tests/test_gosh_release_layout.py` | Release/install contract regression surface | Verifies build/package layout and packaged install flow |
| `.github/workflows/test.yml` | Current CI workflow | Runs tests plus Saturno build/package verification |
