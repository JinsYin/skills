---
title: 基础镜像前缀用 global ARG 参数化
impact: HIGH
impactDescription: 硬编码镜像源导致本地或 CI 其中一方永远拉不到镜像
tags: image, dockerfile, registry, arg
---

## 基础镜像前缀用 global ARG 参数化

本地开发机和 CI 节点通常走**不同的镜像源**：本地走公网镜像加速，CI 走内网仓库（外网不可达）。把源硬编码进 `FROM`，必然有一方拉不到。

写在第一条 `FROM` 之前的 `ARG` 是 **global ARG**，作用于本文件所有 `FROM`；写在 `FROM` 之后的 ARG 只在该阶段内有效。多阶段镜像里这个区别很容易踩错。

**前缀必须含尾斜杠，且不把 `/library/` 写死在 `FROM`**：公网加速常见 `m.daocloud.io/docker.io/library/`，内网 SWR / Harbor 常见 `registry.internal/lib/`，路径层级不同。统一直接拼接 `${BASE_REGISTRY}image:tag` 才能无缝切换；切勿照抄 `docker-compose.yml` 无尾斜杠的主机名写法（见 `compose-parameterize-env`）。

**错误（CI 节点无公网，构建直接失败）：**

```dockerfile
FROM maven:3.9.9-eclipse-temurin-21 AS builder
FROM eclipse-temurin:21-jre AS runner
```

**正确（默认值给本地，CI 用 `--build-arg` 覆盖）：**

```dockerfile
# global ARG：必须在第一条 FROM 之前声明
ARG BASE_REGISTRY=m.daocloud.io/docker.io/library/

FROM ${BASE_REGISTRY}maven:3.9.9-eclipse-temurin-21 AS builder
FROM ${BASE_REGISTRY}eclipse-temurin:21-jre AS runner
```

```bash
docker build --build-arg BASE_REGISTRY=registry.internal/lib/ .
```

**例外**：某些镜像只在特定仓库有原生多架构 manifest，走镜像源反而拿到错误架构。这类应显式直连并就地注释原因。
