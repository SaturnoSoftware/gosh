# Tasks

## Current Task

### T-005: Add the first CI workflow

- Mode: AI owns
- Owner: Assistant
- Status: Done
- Goal: run the real first `gosh` verification path in automation.
- Why now: once the first tests existed, the repo needed CI immediately instead of
  staying a local-only quality story.
- Scope:
  - add `.github/workflows/test.yml`
  - run the Python CLI tests
  - run the `spb` build/package entrypoints
- Verification:
  - `python3 -m unittest discover -s tests -v`
  - `pwsh -File ./Scripts/build.ps1 -ProjectRoot $PWD -BuildNumber 0`
  - `pwsh -File ./Scripts/package.ps1 -ProjectRoot $PWD -BuildNumber 0`
- Result:
  - first CI workflow committed
  - first regression-safe verification path green locally

### T-004: Add the first automated tests

- Mode: AI owns
- Owner: Assistant
- Status: Done
- Goal: create the first regression-safe test surface for `gosh`.
- Why now: the repo had no automated tests at all.
- Scope:
  - add committed tests under `tests/`
  - start with the Python CLI behavior that can be exercised without shell-session
    mutation
- Verification:
  - `python3 -m unittest discover -s tests -v`
- Result:
  - black-box subprocess tests now cover help, add/print, and delete flows

### T-003: Define the first automated test strategy

- Mode: Shared
- Owner: Assistant
- Status: Done
- Goal: choose the smallest valuable automated test surface.
- Why now: a small repo still needs a real test base, but the first slice should not
  overengineer wrapper/session behavior.
- Decision:
  - use black-box subprocess tests around `gosh/gosh2.py`
  - isolate bookmark storage through per-test `HOME`
  - defer shell-wrapper directory-mutation tests to later slices

### T-001: Create the first Saturno build/package contract

- Mode: AI owns
- Owner: Assistant
- Status: Done
- Goal: make `gosh` buildable and packageable through the minimum Saturno `spb`
  contract.
- Why now: the repo had no shared Saturno build/package surface at all.
- Scope:
  - add `package.json`
  - add `Scripts/build.ps1`
  - add `Scripts/package.ps1`
  - ignore `__BUILD/` and `__DIST/`
  - document the new build/package entrypoints in `README.md`
- Verification:
  - `pwsh -File Scripts/build.ps1 -ProjectRoot /mnt/d/Projects/AmazingCow/saturnosoftware/repos/gosh -BuildNumber 0`
  - `pwsh -File Scripts/package.ps1 -ProjectRoot /mnt/d/Projects/AmazingCow/saturnosoftware/repos/gosh -BuildNumber 0`
- Result:
  - `__BUILD/gosh-5.0.0-0/` created
  - `__DIST/gosh-5.0.0-0/` created

## Backlog

| ID | Task | Mode | Status | Notes |
| --- | --- | --- | --- | --- |
| T-002 | Create the `_AI` working set | AI owns | Done | Seed repo-specific docs from live code |
| T-003 | Define the first automated test strategy | Shared | Done | Black-box subprocess tests around `gosh2.py` with isolated `HOME` |
| T-004 | Add the first automated tests | AI owns | Done | `unittest` CLI coverage for help, add/print, and delete flows |
| T-005 | Add CI workflow | AI owns | Done | GitHub Actions now runs tests plus the `spb` build/package contract |
| T-006 | Clarify release artifact strategy | Shared | Open | Install-script only versus clearer packaged flow |
| T-007 | Define benchmark posture | Shared | Done | Small CLI benchmark expectations now documented in `TESTING.md` |
| T-008 | Expand CLI regression coverage | AI owns | Open | Cover invalid paths, fuzzy lookup, update flow, and wrapper behavior |
