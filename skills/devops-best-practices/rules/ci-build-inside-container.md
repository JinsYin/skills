---
title: 构建在指定镜像内进行，不依赖 CI 节点自带环境
impact: HIGH
impactDescription: 依赖节点环境时，换节点或节点升级会让构建结果无声改变
tags: ci, pipeline, reproducibility
---

## 构建在指定镜像内进行，不依赖 CI 节点自带环境

若构建步骤直接调用节点上的 `mvn` / `node`，那么"用哪个版本编译"就取决于节点当时装了什么。加节点、升级节点、或换一台跑，产出就可能不同——而这类差异不报错，只表现为"在某台机器上构建出来的包有问题"。

每个构建步骤都要显式指定镜像，且**版本号钉到次版本以上**：

```yaml
- name: deploy-sdk
  image: maven:3.9.9-eclipse-temurin-21     # 不写 maven:latest
  commands:
    - mvn deploy
```

同一条流水线里跨步骤的工具版本必须一致。后端用 temurin-21 构建、镜像里却是 temurin-17 运行，属于典型的跨步骤漂移。

**基础镜像的版本也要与本地对齐**：CI 用 Node 24、本地用 Node 20，`pnpm install --frozen-lockfile` 可能因原生模块的预编译产物不同而结果不同。锁定版本的价值就在这里。

**内网 / 离线 CI 步骤镜像**：内网或断公网 CI 中，构建与部署工具镜像（如 `plugins/kaniko`、`alpine/k8s`）须按目标架构离线中转至内网仓库（`docker pull --platform <arch>` → `docker save` → 传内网 → `docker load` → `docker tag` → `docker push`），保留上游 `<namespace>/<repo>` 路径（如 `registry.example.com/lib/plugins/kaniko:1.13.7`、`registry.example.com/lib/alpine/k8s:1.28.15`）。

**镜像可见性与拉取鉴权**：Drone 插件的 `settings.username`/`password` 仅用于容器内推拉业务镜像，不作用于 Runner 宿主机拉取步骤 `image:`。私有仓库新推镜像默认私有，须在控制台设为公开（或配置 `image_pull_secrets` / Runner 宿主机登录），否则拉取步骤镜像时报错拒绝（如 `denied: You may not login yet`）。
