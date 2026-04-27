# Release

## Snapshot

- Release status: migration-defined release posture
- Target audience: shell users and developers
- Distribution channel(s): GitHub repo clone and packaged `__DIST/<release-name>/` roots
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
- current package outputs land under `__BUILD/<release-name>/` and
  `__DIST/<release-name>/`
- the packaged release artifact shape is now explicit:
  - `App/gosh2.py`
  - `App/gosh.sh`
  - `App/gosh.ps1`
  - `install.sh`
  - `install.ps1`
  - `package.json`
- the repo still has no approved deploy / set-current / release entrypoint
- install scripts remain the practical user-facing release path today, but they now
  consume the packaged layout instead of depending only on the loose repo tree

## Open Release Gaps

- define the future tagged/released distribution story around the current packaged layout
- define whether the repo needs a formal release job or remains manually cut for now
- document the eventual release verification path beyond local build/package/install
