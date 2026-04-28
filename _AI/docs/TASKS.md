# Tasks

## Current Task

### T-011: Define code-style and script-quality posture

- Mode: Shared
- Owner: Assistant
- Status: Done
- Goal: make the repo's Python/Bash/PowerShell quality rules explicit enough that future
  changes do not weaken the small-CLI contract.
- Why now: the repo now has real tests, wrappers, and a packaged release layout, so the
  next risk is silent drift in script behavior rather than missing infrastructure.
- Scope:
  - strengthen `CODESTYLE.md`
  - tie code-style expectations to the committed verification path
  - make wrapper/session behavior part of the explicit quality posture
- Verification:
  - reviewed `CODESTYLE.md` against `gosh/gosh2.py`, `gosh/gosh.sh`, `gosh/gosh.ps1`,
    and the current test/build/package commands
- Result:
  - the repo now has explicit quality gates for CLI changes, wrapper changes, and
    packaged install-flow changes

### T-008: Expand CLI regression coverage

- Mode: AI owns
- Owner: Assistant
- Status: Done
- Goal: cover the next real regression-prone CLI behaviors beyond help/add/delete.
- Why now: the repo already had its first tests and package layout checks, but key user
  behavior still had no automated protection.
- Scope:
  - cover invalid path handling
  - cover fuzzy-name lookup
  - implement and cover the missing update flow
  - cover wrapper directory mutation in PowerShell and Bash
- Verification:
  - `python3 -m unittest discover -s tests -v`
- Result:
  - CLI regression coverage now protects invalid-path failure, fuzzy lookup, update, and
    wrapper directory-mutation behavior

### T-010: Modernize the install/build/release structure

- Mode: AI owns
- Owner: Assistant
- Status: Done
- Goal: keep the install-script UX while giving `gosh` a clearer packaged release
  layout that no longer depends only on the loose legacy repo tree.
- Why now: `gosh` already had the minimum `spb` build/package entrypoints, but the
  release payload shape was still implicit and too close to the old copy-based layout.
- Scope:
  - stage an explicit `App/` payload during build/package
  - make `install.sh` and `install.ps1` consume the packaged layout
  - add regression coverage for build/package layout and packaged install flow
- Verification:
  - `python3 -m unittest discover -s tests -v`
  - `pwsh -File Scripts/build.ps1 -ProjectRoot . -BuildNumber 0`
  - `pwsh -File Scripts/package.ps1 -ProjectRoot . -BuildNumber 0`
- Result:
  - `gosh` now ships a clearer package-ready release root while preserving the existing
    install-script UX

### T-009: Normalize repo docs after the first tests/CI/benchmark slices

- Mode: AI owns
- Owner: Assistant
- Status: Done
- Goal: make the repo-local product/release/architecture memory match the already-landed
  `spb`, tests, CI, and benchmark posture.
- Why now: the repo state improved in several slices, but parts of the durable `_AI`
  memory still described the older pre-test and pre-CI reality.
- Scope:
  - sync `PRODUCT.md`
  - sync `RELEASE.md`
  - sync `ARCHITECTURE.md`
  - record the current `spb` adoption status in repo-local task memory
- Verification:
  - reviewed repo-local docs against `README.md`, `.github/workflows/test.yml`,
    `Scripts/build.ps1`, `Scripts/package.ps1`, and `tests/test_gosh_cli.py`
- Result:
  - repo-local docs now describe the real committed tests, CI, and `spb` build/package
    entrypoints instead of the earlier legacy-only state

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
| T-006 | Clarify release artifact strategy | Shared | Done | Hybrid decision: packaged `App/` payload with install scripts as the user-facing flow |
| T-007 | Define benchmark posture | Shared | Done | Small CLI benchmark expectations now documented in `TESTING.md` |
| T-008 | Expand CLI regression coverage | AI owns | Done | Covers invalid paths, fuzzy lookup, update flow, and wrapper directory mutation |
| T-010 | Modernize install/build/release structure | AI owns | Done | `App/` payload now stages in `__BUILD/` and `__DIST/`, and install scripts consume it |
| T-011 | Define code-style and script-quality posture | Shared | Done | `CODESTYLE.md` now ties Python/Bash/PowerShell changes to explicit quality gates and verification commands |
