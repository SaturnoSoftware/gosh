# `_AI`

This directory is the durable AI and human working set for `gosh`.

`gosh` is now being brought into the Saturno.Software repo standard.
These docs should stay short, factual, and aligned with the live repo.

## Read Order

1. `_AI/AGENTS.md`
2. `_AI/docs/PRODUCT.md`
3. `_AI/docs/RELEASE.md`
4. `_AI/docs/ECOSYSTEM.md`
5. `_AI/docs/QUESTIONS.md`
6. `_AI/docs/TASKS.md`
7. `_AI/docs/ARCHITECTURE.md`
8. `_AI/docs/CODESTYLE.md`
9. `_AI/docs/TESTING.md`
10. `_AI/docs/CICD.md`
11. `_AI/lessons.md`

## Current Repo Reality

- `gosh` is a cross-shell directory bookmark utility.
- Runtime is centered on `gosh/gosh2.py`.
- Bash and PowerShell wrappers live in `gosh/gosh.sh` and `gosh/gosh.ps1`.
- Legacy install scripts live at the repo root.
- The repo now has the first Saturno build/package contract via:
  - `package.json`
  - `Scripts/build.ps1`
  - `Scripts/package.ps1`

## Current Biggest Gaps

- no automated tests
- no committed CI workflow
- no durable release/process docs existed before this `_AI` pack
- still not fully aligned with the broader Saturno standard
