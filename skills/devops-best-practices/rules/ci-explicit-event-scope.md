---
title: Scope both pipeline trigger (ref + event) and every step when.event explicitly
impact: HIGH
impactDescription: Missing trigger.ref builds every feature branch; missing step when.event re-runs image builds when trigger.event expands
tags: ci, drone, trigger, event, promote
---

## Scope both pipeline trigger (ref + event) and every step when.event explicitly

Pipeline `trigger` gates whether pipeline runs; step `when` gates which steps participate.

- **Omitting `trigger.ref`** builds and pushes on every feature branch.
- **Omitting step `when.event`** re-runs all image builds and overwrites tags when `trigger.event` adds lightweight events (`promote`).

Enforce both layers:

1. **Top-level `trigger:`** declares `ref:` (`refs/heads/master`, `refs/tags/*`) and `event:` (`push`, `tag`; add `promote` only when promote steps exist).
2. **Every step** declares `when.event`; `promote` steps also scope `when.target`.

```yaml
trigger:
  ref:
    - refs/heads/master
    - refs/tags/*
  event:
    - push
    - tag
    - promote

steps:
  - name: build-api
    when:
      event:
        - push
        - tag                     # promote does not rebuild images

  - name: write-sync-db-marker
    when:
      event:
        - promote
      target:
        - sync-db-pre             # scope promote to explicit target
```
