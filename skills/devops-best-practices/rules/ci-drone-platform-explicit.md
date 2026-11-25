---
title: Declare top-level platform explicitly in .drone.yml
impact: HIGH
impactDescription: Omitting platform defaults Drone to linux/amd64, stalling on ARM64 runners or building wrong-arch images that crash with exec format error
tags: ci, drone, platform, arch, arm64
---

## Declare top-level platform explicitly in .drone.yml

Omitting `platform` defaults Drone to `linux/amd64`. On ARM64 runners, builds stall unscheduled or emit wrong-arch images that pass CI and crash on Kubernetes startup with `exec format error`.

Declare top-level `platform` right after `name: default`. Team default: `linux/arm64`; override `arch` only per `deploy/README.md`.

```yaml
kind: pipeline
type: docker
name: default

platform:
  os: linux
  arch: arm64
```
