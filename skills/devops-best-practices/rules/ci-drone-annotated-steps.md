---
title: Annotate pipeline header and every step in .drone.yml
impact: MEDIUM
impactDescription: Unannotated pipelines obscure parallel execution, shared-Dockerfile args, trigger conditions, and required Drone secrets
tags: ci, drone, comments, maintainability
---

## Annotate pipeline header and every step in .drone.yml

`.drone.yml` hides conditional triggers (`push`/`tag`/`promote`), shared-Dockerfile `build_args`, and out-of-band Drone secrets. Add concise Chinese comments in two places:

1. **File header**: title (`<Project> CI Pipeline（Drone CI + kaniko）`), purpose, per-step overview, trigger summary.
2. **Before each step**: 1–4 lines covering role, parallelism/`depends_on`, trigger scope (`promote`/tag-only), required Drone secret names, and caveats (`MODULE=` arg, Maven `-s`, etc.).

```yaml
# <Project> CI Pipeline（Drone CI + kaniko）
# ========================================
# 功能：单 pipeline 并行构建并推送各服务镜像至目标容器仓库。
#   - build-api：后端服务，复用 Dockerfile.backend，通过 MODULE 区分模块。
#   - build-frontend：前端构建，与后端并行。
# 触发条件：推送到 master 或打 tag 时触发。

steps:
  # 构建并推送 app-api 镜像（后端 API）；无外部依赖，与其他构建步骤并行。
  # 凭据：Drone secrets registry_username / registry_password。
  - name: build-api
    image: plugins/kaniko:1.13.7
```
