---
title: 显式声明时区，优先内置 tzdata 镜像实现零 OS 下包
impact: HIGH
impactDescription: 容器默认 UTC 导致时间偏移；无公网 CI 中盲跑 apk 装 tzdata 会超时失败
tags: image, dockerfile, timezone, offline-ci
---

## 显式声明时区，优先内置 tzdata 镜像实现零 OS 下包

容器默认时区是 UTC，与宿主机无关。不显式声明，日志时间戳、定时任务触发点、以及任何依赖"当天"边界的业务逻辑都会偏移。

**优先零 OS 下包**：内网 CI 通常无法访问公网 `dl-cdn.alpinelinux.org`。选用已内置 `tzdata` 的基础镜像（glibc slim 系如 `node:24-bookworm-slim`、`eclipse-temurin`，或已预装 `tzdata` 的 `nginx:1.27-alpine`），设 `ENV TZ=Asia/Shanghai`，构建期断言时区文件存在并链接 `/etc/localtime`，彻底避免构建期 `apk`/`apt` 下包。

```dockerfile
# 推荐（内置 tzdata 的 glibc slim 或预装 tzdata 的 alpine，构建期零联网下包）
ENV TZ=Asia/Shanghai
RUN [ -f /usr/share/zoneinfo/Asia/Shanghai ] \
 && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

仅当基础镜像确实缺 `/usr/share/zoneinfo/Asia/Shanghai` **且**确认 CI 可达公网或有内网 OS 镜像源时，才换源后执行 `apk add --no-cache tzdata`。无内网 OS 源时，不要留空 `ALPINE_MIRROR` 回退公网（触发每源 60 秒超时或 `TLS: unspecified error`），也不要对已预装 `tzdata` 的镜像重复执行 `apk add`。

**JVM 应用要额外注意**：JVM 读 `TZ` 决定默认时区，但一旦通过 `JAVA_OPTS` 传了 `-Duser.timezone`，后者优先。两处都设时必须一致，否则容器时区与 JVM 时区不同——日志（容器时区）和业务时间（JVM 时区）会对不上，这种不一致极难排查。
