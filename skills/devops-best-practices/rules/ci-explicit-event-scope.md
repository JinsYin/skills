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
2. **Every step** declares `when.event`; `promote` steps scope `when.target`, and tag-bound prod deploys also scope `when.ref: [refs/tags/*]` (prevents promoting `:latest` branch builds) with `depends_on: [clone]` to skip rebuilds.

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

  - name: deploy-prod
    depends_on: [clone]
    when:
      event:
        - promote
      target:
        - prod                    # scope promote to explicit target
      ref:
        - refs/tags/*             # tag-bound prod deploy only
```

Drone `when:` fields AND-only (no OR per step); `drone/envsubst` omits `${var:+alt}`. Keep tag-only prod promote as one step; for branch promotes without extra build steps, push dual tags (`latest` + short commit SHA) + registry retention rules.
