---
title: Run independent build steps in parallel and wire downstream steps with depends_on
impact: HIGH
impactDescription: Adding depends_on to any step switches the entire Drone pipeline from sequential to DAG parallel mode, causing silent race conditions on steps missing dependencies
tags: ci, drone, dag, depends_on, parallelism
---

## Run independent build steps in parallel and wire downstream steps with depends_on

Drone switches execution mode implicitly across entire pipeline:

- **Zero steps define `depends_on`** → all steps run **sequentially** in file order.
- **Any step defines `depends_on`** → entire pipeline enters **DAG mode**; every step without `depends_on` launches immediately in parallel after implicit `clone`.

Rules:

1. **With fan-in step** (e.g. archive upload, manifest check): independent image builds (`build-<module>`) omit `depends_on` to run in parallel; fan-in step lists every upstream step in `depends_on`.
2. **Without fan-in step**: add `depends_on: [clone]` on independent builds to enable DAG parallelism instead of sequential execution.
3. **Mode-switch audit**: when adding first `depends_on` to sequential pipeline, audit remaining steps—every step reading prior workspace output must declare its own `depends_on`.

**Example (semi-offline archive upload waiting on parallel Kaniko builds):**

```yaml
steps:
  - name: build-api
    image: plugins/kaniko:1.13.7
    settings:
      tar_path: /drone/src/dist/images/app-api-${DRONE_TAG:-latest}.tar
      # ...other kaniko settings
    when:
      event: [push, tag]

  - name: build-frontend
    image: plugins/kaniko:1.13.7
    settings:
      tar_path: /drone/src/dist/images/app-frontend-${DRONE_TAG:-latest}.tar
      # ...other kaniko settings
    when:
      event: [push, tag]

  # 汇总所有镜像归档与 deploy 产物并上传文件服务；依赖全部镜像构建完成
  - name: upload-artifacts
    image: python:3.13-alpine
    environment:
      FILE_BROWSER_URL: *FILE_BROWSER_URL
      FILE_BROWSER_USERNAME:
        from_secret: file_browser_username
      FILE_BROWSER_PASSWORD:
        from_secret: file_browser_password
    commands:
      - python3 deploy/scripts/upload-artifacts.py --directory dist/images
    depends_on:
      - build-api
      - build-frontend
    when:
      event: [push, tag]
```
