# Ecosystem

## Current Shared-Library Position

- `gosh` is not a `.NET` repo, so `Rings` is not directly relevant to its runtime
  implementation.
- `gosh` should still follow Saturno-wide repo standards for:
  - `_AI`
  - `spb`
  - testing
  - CI/CD
  - release clarity

## Reuse Direction

- keep shell/Python utility code local unless a real reusable boundary appears
- if Saturno later grows more small shell/CLI utilities, revisit whether some helper
  layer should exist

