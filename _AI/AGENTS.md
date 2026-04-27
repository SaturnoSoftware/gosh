# Project Instructions

This `_AI` folder is the durable working set for `gosh`.

Use it to keep product, release, testing, CI/CD, architecture, and task context
visible to humans and future AI sessions.

## Organization Context

- Company: Saturno.Software
- Product repo: `gosh`
- Product type: CLI utility
- Current posture: legacy repo being normalized into the Saturno standard

## Core Rule

The assistant may write freely inside `_AI/`.

Keep code, build outputs, and generated artifacts outside `_AI/` unless the task
explicitly requires otherwise.

## First Read For Every Session

Before making non-trivial changes, read:

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

Then inspect the live repo before trusting docs.

## Repo Priorities

- bring `gosh` into Saturno repo standards
- keep the core CLI behavior simple
- make build/package/test/release expectations explicit
- avoid overengineering a small utility

## Current Non-Negotiable Direction

- `gosh` must become buildable through the Saturno `spb` contract
- tests and CI must be added
- documentation must reflect real repo behavior
- changes should improve the repo instead of preserving undocumented legacy drift

## Documentation Rules

- state live facts directly
- name exact files and commands
- separate current reality from future targets
- keep docs current as the repo evolves
