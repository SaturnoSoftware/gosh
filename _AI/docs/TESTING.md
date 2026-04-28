# Testing and Quality

## Current Reality

- committed automated tests now exist in `tests/test_gosh_cli.py`
- committed release/install contract tests now exist in `tests/test_gosh_release_layout.py`
- the first test surface is black-box subprocess testing against `gosh/gosh2.py`
- tests isolate bookmark storage by overriding `HOME` per test process

## Current Verification Path

- `python3 -m unittest discover -s tests -v`
- `pwsh -File Scripts/build.ps1 -ProjectRoot . -BuildNumber 0`
- `pwsh -File Scripts/package.ps1 -ProjectRoot . -BuildNumber 0`

## Why This First Surface

- it exercises the real CLI behavior without needing shell-session directory mutation
- it keeps the current legacy script structure testable before deeper refactors
- it avoids adding third-party test dependencies just to start getting coverage

## Current Covered Behavior

- help output
- add bookmark flow
- print bookmark flow
- bookmark count increment on successful print
- delete bookmark flow
- invalid path rejection
- fuzzy-name lookup
- update flow
- package-ready `App/` layout in `__BUILD/<release-name>/`
- package-ready release layout preserved in `__DIST/<release-name>/`
- packaged PowerShell install flow
- packaged Bash install flow on Unix-like environments
- wrapper directory mutation in PowerShell and Bash where those shells are available
- legacy bookmark migration into the Saturno data root

## Next Coverage Targets

- version and help output consistency
- edge cases around malformed bookmark file lines
- conflict resolution when multiple bookmark names fuzzy-match similarly

## Benchmark Posture

`gosh` is a small CLI, so its benchmark posture should stay narrow and practical.

What matters:

- startup overhead of the Python CLI for common commands
- latency of common bookmark operations on a modest bookmark file
- avoiding accidental regressions from future refactors

What does not matter yet:

- synthetic micro-benchmarks that do not reflect real CLI usage
- dashboarding or historical benchmark infrastructure before the repo has a wider
  automated surface

First meaningful future benchmark targets:

1. `--list` on a representative bookmark file
2. `--print <name>` on a representative bookmark file
3. `--add <name> <path>` on a representative bookmark file
