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

## Quality Gates For Changes

- every CLI behavior change in `gosh/gosh2.py` must add or update `unittest` coverage
- every change to the packaged/install flow must keep `Scripts/build.ps1` and
  `Scripts/package.ps1` green
- every Bash wrapper change must preserve the directory-mutation contract instead of
  quietly falling back to print-only behavior
- every PowerShell wrapper change must preserve the same contract: mutate the current
  shell location when the bookmark resolves, and print diagnostics when it does not
- keep the runtime dependency surface stdlib-only unless the repo proves that a new
  dependency buys substantial value

## Script Conventions

- preserve the current small-script style in `gosh2.py`; do not refactor it into
  framework-heavy modules just to look modern
- prefer explicit command branches over dynamic dispatch for this CLI size
- keep shell scripts non-interactive and automation-friendly
- keep release/install scripts compatible with both repo-root execution and packaged
  `App/` execution
- when touching legacy Python code, improve correctness and tests first; stylistic
  cleanups are secondary unless they directly clarify the changed path

## Verification Discipline

- run `python3 -m unittest discover -s tests -v` after Python or wrapper changes
- run `pwsh -File Scripts/build.ps1 -ProjectRoot . -BuildNumber 0` after build/package
  or install-layout changes
- run `pwsh -File Scripts/package.ps1 -ProjectRoot . -BuildNumber 0` when package or
  install flow changes
