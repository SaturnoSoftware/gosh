# Testing and Quality

## Current Reality

- there are no committed automated tests in the repo today
- there is no documented verification path beyond manual use

## Immediate Goal

- define the first automated test surface
- add the first real regression-safe tests

## Likely First Test Surface

- Python core behavior in `gosh/gosh2.py`

Why:

- it owns the bookmark parsing and command behavior
- it is easier to test than shell directory-changing wrappers
- it gives the repo a real verification base quickly

