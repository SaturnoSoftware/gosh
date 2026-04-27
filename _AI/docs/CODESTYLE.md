# Code Style

## Tooling

| Area | Choice | Command/Notes |
| --- | --- | --- |
| Python runtime | `python3` | Core CLI runtime |
| Bash wrapper | `gosh/gosh.sh` | Shell integration |
| PowerShell wrapper | `gosh/gosh.ps1` | Shell integration |
| Build | `Scripts/build.ps1` | Saturno build entrypoint |
| Package | `Scripts/package.ps1` | Saturno package entrypoint |
| Test | Not defined yet | Must be added |
| CI | Not defined yet | Must be added |

## Current Style Priorities

- keep the utility small
- prefer direct and explicit script logic
- do not add architecture that a small CLI does not need
- make shell/Python behavior easy to reason about
- modernize the repo without breaking the basic user workflow

