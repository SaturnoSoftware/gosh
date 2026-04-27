# Questions

## Active Questions

### Q-001: What should the long-term release shape of `gosh` be?

- Status: Open
- Question: should `gosh` stay install-script driven, or should it also produce a
  clearer packaged release artifact?
- Why it matters: build/package/release standardization depends on the target release
  shape.
- Assumption: keep the current install scripts for now while modernizing the repo
  around them.
- Answer:
- Follow-up:

### Q-002: What is the smallest valuable automated test surface?

- Status: Open
- Question: should the first tests target Python core behavior only, or also wrapper
  integration?
- Why it matters: this decides the first real verification path.
- Assumption: start with the Python core and add wrapper-focused tests after that.
- Answer:
- Follow-up:
