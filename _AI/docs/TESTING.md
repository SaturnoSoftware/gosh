# Testing and Quality

## Current Reality

- committed automated tests now exist in `tests/test_gosh_cli.py`
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

## Next Coverage Targets

- invalid path handling
- fuzzy-name lookup behavior
- update flow
- wrapper behavior in Bash and PowerShell
