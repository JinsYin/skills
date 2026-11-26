---
title: 镜像 tag、端口、镜像源用环境变量参数化并提供 .env.example，严禁使用 :?
impact: MEDIUM
impactDescription: 硬编码端口在宿主已占用时无法绕过；使用 :? 会在缺少 .env 时直接报错阻断启动
tags: compose, docker-compose, env, portability
---

## 镜像 tag、端口、镜像源用环境变量参数化并提供 .env.example，严禁使用 :?

开发机之间总有差异：本机已经装了 PostgreSQL 占着 5432、公司网络只能走内网镜像源、需要临时试另一个版本的数据库。这些差异若只能通过改入库的 `docker-compose.yml` 解决，改动就会被误提交，或者反复出现在每个人的工作区里。

```yaml
services:
  opengauss:
    image: ${DOCKER_REGISTRY_MIRROR:-docker.m.daocloud.io}/opengauss/opengauss:${OPENGAUSS_IMAGE_TAG:-5.0.0}
    ports:
      # 宿主已占 5432 时在 .env 中覆盖 OPENGAUSS_HOST_PORT=5433
      - "${OPENGAUSS_HOST_PORT:-5432}:5432"
```

四条配套要求：

- **一律带默认值 `${VAR:-default}`，严禁使用 `${VAR:?error}` 或 `${VAR?error}`**：保证克隆后零配置直接可跑（镜像站默认 `${DOCKER_REGISTRY_MIRROR:-docker.m.daocloud.io}`）。使用 `?` 会在未建 `.env` 时直接报错退出，破坏开箱即用。
- **与 Dockerfile 的 `BASE_REGISTRY` 区分命名**：Compose 跨 `library/` 与非官方命名空间混用，只参数化无尾斜杠主机名（`DOCKER_REGISTRY_MIRROR`）；Dockerfile 需要含尾斜杠的路径前缀（`BASE_REGISTRY`，见 `image-base-registry-arg`），不复用同名变量以防误抄与 `.env` 冲突。
- **`.env` 入 gitignore，`.env.example` 入库**，后者列全所有可覆盖项及说明
- **容器内端口不参数化**，只参数化宿主侧端口——容器内端口变化会牵动健康检查、服务间地址等一串配置

**错误示例（使用 `?` 强制要求外部变量，缺少 `.env` 时无法启动）：**

```yaml
services:
  postgres:
    image: ${DOCKER_REGISTRY_MIRROR:?err}/library/postgres:${POSTGRES_TAG:?err}
    ports:
      - "${POSTGRES_HOST_PORT:?PORT must be set}:5432"
```

**正确示例（提供安全、可直接启动的默认值）：**

```yaml
services:
  postgres:
    image: ${DOCKER_REGISTRY_MIRROR:-docker.m.daocloud.io}/library/postgres:${POSTGRES_TAG:-16}
    ports:
      - "${POSTGRES_HOST_PORT:-5432}:5432"
```

参数化的边界：只参数化**环境差异**，不要参数化架构决策。把服务名、网络拓扑也做成变量，会让文件失去可读性而收益甚微。
