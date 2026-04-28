# Release

## Snapshot

- Release status: migration-defined release posture
- Target audience: shell users and developers
- Distribution channel(s): GitHub repo clone and packaged `__DIST/<release-name>/` roots
- Install/update path:
  - `install.sh`
  - `install.ps1`
  - installed machine-local root: `~/.saturnosoftware/gosh/`
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
- the install scripts now deploy into the Saturno machine-local app tree:
  - `~/.saturnosoftware/gosh/bin`
  - `~/.saturnosoftware/gosh/config`
  - `~/.saturnosoftware/gosh/data`
- legacy bookmarks under `~/.mateusdigital/config/gosh/gosh-paths.txt` are migrated
  into `~/.saturnosoftware/gosh/data/gosh-paths.txt` on first run
- the repo still has no approved deploy / set-current / release entrypoint
- install scripts remain the practical user-facing release path today, but they now
  consume the packaged layout instead of depending only on the loose repo tree

## Open Release Gaps

- define the future tagged/released distribution story around the current packaged layout
- define whether the repo needs a formal release job or remains manually cut for now
- document the eventual release verification path beyond local build/package/install
