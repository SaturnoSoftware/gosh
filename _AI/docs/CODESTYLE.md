# Code Style

## Tooling

| Area | Choice | Command/Notes |
| --- | --- | --- |
| Python runtime | `python3` | Core CLI runtime |
| Bash wrapper | `gosh/gosh.sh` | Shell integration |
| PowerShell wrapper | `gosh/gosh.ps1` | Shell integration |
| Build | `Scripts/build.ps1` | Saturno build entrypoint |
| Package | `Scripts/package.ps1` | Saturno package entrypoint |
| Test | `python3 -m unittest discover -s tests -v` | First committed regression surface |
| CI | `.github/workflows/test.yml` | Runs tests plus build/package contract |

## Current Style Priorities

- keep the utility small
- prefer direct and explicit script logic
- do not add architecture that a small CLI does not need
- make shell/Python behavior easy to reason about
- modernize the repo without breaking the basic user workflow
- prefer Python stdlib testing before adding dependencies for a small utility
