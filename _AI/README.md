# `_AI`

This directory is the durable AI and human working set for `gosh`.

`gosh` now has the baseline Saturno wrapper, test, and CI posture in place.
These docs should stay short, factual, and aligned with the live repo and master policy.

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

- no benchmark job yet
- no wrapper-shell integration checks in CI yet
- no release automation yet
- repo-local `_AI/` must stay synced with `_AI_MASTER/` when Saturno-wide policy changes

## Saturno Alignment

- The local source of truth for `gosh` is this `_AI/` folder and the live repo.
- When work touches Saturno-wide policy, `_AI` structure, `spb`, shared tooling, or
  cross-repo quality rules, also read `_AI_MASTER/README.md` and the relevant
  `_AI_MASTER/docs/*` files from the Saturno master checkout.
- `_AI_DEFAULT` is the reusable structure source, not the active truth for this repo.

## Sync Workflow

1. Start with the local `_AI/` docs for the concrete `gosh` reality.
2. Check `_AI_MASTER/` before changing Saturno-wide process, wrapper expectations, or
   reusable cross-repo behavior.
3. If local repo evidence invalidates a master assumption, update `_AI_MASTER/` in the same
   slice.
4. Keep this README and the current docs aligned with the committed tests, CI, and release
   shape.
