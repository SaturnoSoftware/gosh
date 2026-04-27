# Tasks

## Current Task

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
| T-003 | Define the first automated test strategy | Shared | Open | Decide Python-core-first versus wrapper coverage |
| T-004 | Add the first automated tests | AI owns | Open | Start with the smallest reliable surface |
| T-005 | Add CI workflow | AI owns | Open | Run the real verification path |
| T-006 | Clarify release artifact strategy | Shared | Open | Install-script only versus clearer packaged flow |
| T-007 | Define benchmark posture | Shared | Open | Small CLI benchmark expectations |

