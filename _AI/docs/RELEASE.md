# Release

## Snapshot

- Release status: migration-defined release posture
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
- the repo now has documented `spb`-compatible build/package entrypoints:
  - `pwsh -File Scripts/build.ps1 -ProjectRoot . -BuildNumber 0`
  - `pwsh -File Scripts/package.ps1 -ProjectRoot . -BuildNumber 0`
- current package outputs land under:
  - `__BUILD/<release-name>/`
  - `__DIST/<release-name>/`
- the repo still has no approved deploy / set-current / release entrypoint
- install scripts remain the practical user-facing release path today

## Open Release Gaps

- define the real release artifact shape
- define whether releases remain install-script driven or move to a clearer packaged
  flow
- document the actual release verification path
