# Product Brief

## Identity

- Product name: gosh
- Working codename: gosh
- Company: Saturno.Software / mateus.digital
- Product type: CLI utility
- Current stage: Existing legacy repo under modernization
- Primary platform: Bash and PowerShell shells with a Python runtime core
- Repository status: Existing codebase
- Client work: No

## One-Sentence Pitch

- Pitch: `gosh` is a small bookmark utility that lets users jump quickly to saved
  directories from Bash or PowerShell.

## Problem

- Problem being solved: moving repeatedly through long filesystem paths is slow and
  noisy in shell workflows.
- Why this matters now: the product already exists, but it sits outside the Saturno
  build/test/release standard and needs modernization.
- What is painful today: wrapper-focused regression coverage is still shallow, the repo
  still needs a clearer long-term release/deploy posture, and modernization work must
  keep the small-tool UX simple.
- Why existing alternatives are not enough: shell aliases and ad-hoc scripts do not
  provide the same bookmark-oriented workflow or cross-shell wrapper behavior.

## Users

- Primary user: shell users who revisit the same directories often
- Secondary user: developers using Bash or PowerShell regularly
- Internal users/stakeholders: Saturno maintainers modernizing and maintaining the tool
- Non-users: people who do not work in shells regularly

## Outcome

- Core user outcome: type a short bookmark name and jump directly to a saved path.
- Business/product outcome: keep a small CLI useful while bringing it into Saturno's
  quality and maintenance standards.
- What success looks like in v1:
  - build/package path is standardized
  - repo has durable docs
  - tests and CI exist
  - install/release behavior is explicit and reproducible
- What is explicitly out of scope:
  - turning `gosh` into a large shell framework
  - adding unnecessary architecture around a small utility
- What would make this fail even if technically finished:
  - modernization adds complexity without improving reliability
  - the repo remains undocumented or untested
