---
title: Build container images with pinned plugins/kaniko
impact: CRITICAL
impactDescription: Daemon-based or unpinned plugins fail on daemonless runners; missing DRONE_OUTPUT crashes Kaniko immediately
tags: ci, drone, kaniko, image-build, build-args
---

## Build container images with pinned plugins/kaniko

Build all Drone container images with `plugins/kaniko` (team default: `plugins/kaniko:1.13.7`). Rootless in-container build needs no `docker.sock` mount or privileged DinD. Never use `plugins/docker` or floating tags.

**Required settings per Kaniko step:**

- `image: *KANIKO_IMAGE` — pin patch version (default `plugins/kaniko:1.13.7`); air-gapped/internal CI: mirror preserving upstream path (`registry.example.com/lib/plugins/kaniko:1.13.7`) + ensure Runner pull access (`ci-build-inside-container`).
- `environment.DRONE_OUTPUT: *DRONE_OUTPUT` (`/tmp/drone-output` in `global-variables:`) — omitting crashes Kaniko with `open : no such file or directory`.
- `settings.context: .` — explicit build context.
- `settings.skip_tls_verify: true` — team default for internal registries; set `false` only if `deploy/README.md` requires verified CA.
- `settings.username` / `settings.password` via `from_secret`; `image`, `registry`, `repo`, `tags`, `dockerfile` via `global-variables:` anchors (`ci-anchor-repeated-values`).
- `settings.build_args` — pass `*BASE_REGISTRY_ARG` (`image-base-registry-arg`), `MODULE=<service>` for shared Dockerfiles, and consumed language mirrors (`*NPM_REGISTRY_ARG`); add OS mirror only if Dockerfile installs OS packages from verified internal mirror (prefer zero OS downloads per `image-tz-explicit`).

**Correct:**

```yaml
- name: build-api
  image: *KANIKO_IMAGE
  environment:
    DRONE_OUTPUT: *DRONE_OUTPUT
  settings:
    registry: *DOCKER_REGISTRY
    repo: *REPO_API
    username:
      from_secret: registry_username
    password:
      from_secret: registry_password
    tags:
      - *DOCKER_TAG
    dockerfile: *DOCKERFILE_BACKEND
    context: .
    build_args:
      - *BASE_REGISTRY_ARG
      - MODULE=app-api
    skip_tls_verify: true
  when:
    event:
      - push
      - tag
```

**Optional semi-offline archive:** when `deploy/README.md` requires file-server/air-gapped delivery, add `tar_path: /drone/src/dist/images/<service>-${DRONE_TAG:-latest}.tar` under `settings:` and consume archives in downstream `depends_on` step (`ci-drone-dag-parallelism`).
