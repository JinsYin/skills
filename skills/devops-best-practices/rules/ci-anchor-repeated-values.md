---
title: Centralize repeated values in top-level global-variables YAML anchors
impact: MEDIUM
impactDescription: Scattered registry, repo, Dockerfile, tag, or mirror copies drift silently and push to stale targets without failing CI
tags: ci, drone, yaml, anchors, dry
---

## Centralize repeated values in top-level global-variables YAML anchors

Repeating registry host, tag strategy, Dockerfile path, or mirror `build_args` across steps causes silent partial edits—missed steps still succeed while pushing to stale registries or unreachable mirrors.

Declare all YAML anchors under one top-level `global-variables:` mapping right after `platform:`, with brief purpose comments. Use `global-variables:` instead of top-level `x-*` keys or anchors scattered inside `steps:`.

**Centralize values changing together:**

- Registry and image repos: `DOCKER_REGISTRY`, `REPO_<SERVICE>`
- Shared Dockerfile paths: `DOCKERFILE_<ROLE>`
- Tag strategy: `DOCKER_TAG` (`${DRONE_TAG:-latest}`)
- Mirror `build_args`: `BASE_REGISTRY_ARG` + consumed language mirrors (`NPM_REGISTRY_ARG`, Maven); add OS mirror (`ALPINE_MIRROR_ARG`) only if Dockerfile installs OS packages from verified internal mirror — omit empty `${ALPINE_MIRROR:-}` (air-gapped CI hits public `dl-cdn.alpinelinux.org` and times out)
- Kaniko output path: `DRONE_OUTPUT` (`/tmp/drone-output`)
- Step tool images: `KANIKO_IMAGE`, `DEPLOY_IMAGE` — full image refs; YAML anchors cannot concat strings and Drone `envsubst` expands built-in `DRONE_*` metadata only (ignores custom vars, `global-variables:`, secrets, `DRONE_RUNNER_ENVIRON`)
- Overridable external service endpoints/paths via `${VAR:-default}` when needed

Keep single-use per-service args (`MODULE=app-api`) inline in step.

```yaml
# 全局变量定义（YAML anchor，供各步骤复用，避免硬编码重复）
global-variables:
  DOCKER_REGISTRY:     &DOCKER_REGISTRY     registry.example.com
  REPO_API:            &REPO_API            registry.example.com/org/app-api
  DOCKERFILE_BACKEND:  &DOCKERFILE_BACKEND  deploy/docker/Dockerfile.backend
  # tag 策略：push 落 latest（预发），打 tag 落版本号（生产）
  DOCKER_TAG:          &DOCKER_TAG          ${DRONE_TAG:-latest}
  # 基础镜像与语言包源：CI 走内网源（构建期默认零 OS 下包）
  BASE_REGISTRY_ARG:   &BASE_REGISTRY_ARG   'BASE_REGISTRY=registry.example.com/lib/'
  NPM_REGISTRY_ARG:    &NPM_REGISTRY_ARG    'NPM_REGISTRY=https://npm.example.com'
  # kaniko 插件输出文件路径（修复 "open : no such file or directory" 错误）
  DRONE_OUTPUT:        &DRONE_OUTPUT        /tmp/drone-output
  # 工具镜像：留空前缀即走官方源；走私有仓库前缀时须确保镜像公开或配置 Runner 拉取凭据
  KANIKO_IMAGE:        &KANIKO_IMAGE        registry.example.com/lib/plugins/kaniko:1.13.7

steps:
  - name: build-api
    image: *KANIKO_IMAGE
    environment:
      DRONE_OUTPUT: *DRONE_OUTPUT
    settings:
      registry: *DOCKER_REGISTRY
      repo: *REPO_API
      dockerfile: *DOCKERFILE_BACKEND
      tags:
        - *DOCKER_TAG
      build_args:
        - *BASE_REGISTRY_ARG
        - MODULE=app-api
```
