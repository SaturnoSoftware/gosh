# Release

## Snapshot

- Release status: legacy/manual release posture
- Target audience: shell users and developers
- Distribution channel(s): GitHub repo clone and local install scripts
- Install/update path:
  - `install.sh`
  - `install.ps1`
- License: GPLv3
- Pricing model: free software
- Support stance: maintainer-driven

## Current Reality

- there is no standardized CI release flow yet
- there is no documented packaged release process beyond the install scripts
- the repo now has `spb`-compatible build/package entrypoints, but not a full release
  pipeline

## Open Release Gaps

- define the real release artifact shape
- define whether releases remain install-script driven or move to a clearer packaged
  flow
- document the actual release verification path
