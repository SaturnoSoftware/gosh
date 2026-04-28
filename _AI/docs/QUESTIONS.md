# Questions

## Active Questions

### Q-001: What should the long-term release shape of `gosh` be?

- Status: Resolved
- Question: should `gosh` stay install-script driven, or should it also produce a
  clearer packaged release artifact?
- Why it matters: build/package/release standardization depends on the target release
  shape.
- Assumption:
- Answer: keep the install scripts as the user-facing flow, but give the repo an explicit
  packaged release artifact with an `App/` payload staged under `__BUILD/` and `__DIST/`.
- Follow-up: keep future release work compatible with both the packaged layout and the
  existing install-script UX unless the product intentionally changes that contract.

### Q-002: What is the smallest valuable automated test surface?

- Status: Resolved
- Question: should the first tests target Python core behavior only, or also wrapper
  integration?
- Why it matters: this decides the first real verification path.
- Assumption:
- Answer: start with black-box subprocess tests around `gosh/gosh2.py`, isolating
  bookmark storage through per-test `HOME`; add wrapper-focused tests later.
- Follow-up: expand coverage to wrapper behavior and error-path flows.
