# CI/CD

## Current Reality

- committed workflow: `.github/workflows/test.yml`
- CI now runs:
  - `python3 -m unittest discover -s tests -v`
  - `pwsh -File ./Scripts/build.ps1 -ProjectRoot $PWD -BuildNumber 0`
  - `pwsh -File ./Scripts/package.ps1 -ProjectRoot $PWD -BuildNumber 0`

## Current Gaps

- no benchmark job yet
- no wrapper-shell integration checks yet
- no release job yet
