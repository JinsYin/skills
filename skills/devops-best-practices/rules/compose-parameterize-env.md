---
title: 镜像 tag、端口、镜像源用环境变量参数化并提供 .env.example
impact: MEDIUM
impactDescription: 硬编码端口在宿主已占用时无法绕过，只能改入库文件
tags: compose, docker-compose, env, portability
---

## 镜像 tag、端口、镜像源用环境变量参数化并提供 .env.example

开发机之间总有差异：本机已经装了 PostgreSQL 占着 5432、公司网络只能走内网镜像源、需要临时试另一个版本的数据库。这些差异若只能通过改入库的 `docker-compose.yml` 解决，改动就会被误提交，或者反复出现在每个人的工作区里。

```yaml
services:
  opengauss:
    image: ${BASE_REGISTRY:-docker.m.daocloud.io}/opengauss/opengauss:${OPENGAUSS_IMAGE_TAG:-5.0.0}
    ports:
      # 宿主已占 5432 时在 .env 中覆盖 OPENGAUSS_HOST_PORT=5433
      - "${OPENGAUSS_HOST_PORT:-5432}:5432"
```

三条配套要求：

- **一律带默认值** `${VAR:-default}`，保证零配置可跑（镜像源默认 `${BASE_REGISTRY:-docker.m.daocloud.io}`）
- **`.env` 入 gitignore，`.env.example` 入库**，后者列全所有可覆盖项及说明
- **容器内端口不参数化**，只参数化宿主侧端口——容器内端口变化会牵动健康检查、服务间地址等一串配置

参数化的边界：只参数化**环境差异**，不要参数化架构决策。把服务名、网络拓扑也做成变量，会让文件失去可读性而收益甚微。
