---
title: 非 root 运行，且 UID/GID 必须显式指定
impact: CRITICAL
impactDescription: 隐式分配的系统 UID 与 K8s securityContext 不匹配，挂载卷写不进去
tags: image, dockerfile, security, uid
---

## 非 root 运行，且 UID/GID 必须显式指定

容器以 root 运行会在逃逸时直接拿到宿主权限。但仅仅"创建一个用户"不够——**UID 数值必须显式指定并与部署清单一致**。

`useradd -r` 分配的是系统 UID（通常 100–999），而 K8s 的 `runAsUser: 1000` / `fsGroup: 1000` 期待 1000。两者不匹配时，`fsGroup` 对挂载卷执行 chown 后，进程反而失去写权限——报错是"权限拒绝"，根因却在 Dockerfile 里，排查代价很高。

**基础镜像陷阱**：
- Ubuntu 24.04（noble，含 `eclipse-temurin:21-jre`）已预置 `ubuntu` 占 UID/GID `1000`，直接 `groupadd -g 1000` 会失败（exit 4），需先释放再建。
- 官方 `node:*` 镜像已预置 `node(1000:1000)`，直接复用并构建期断言 `[ "$(id -u node)" = "1000" ] && [ "$(id -g node)" = "1000" ]`，不必删了重建。
- Alpine 使用 `addgroup -g 1000 -S app && adduser -u 1000 -G app -S -H -s /sbin/nologin app`（无 `groupadd`/`useradd`）。

**错误（UID 由系统分配，值不可控）：**

```dockerfile
RUN useradd -r -s /usr/sbin/nologin app
USER app
```

**正确（先释放占位用户，钉死 1000，并用数字 UID 切用户）：**

```dockerfile
# userdel 对非 Ubuntu 基础镜像是无害 no-op
RUN userdel -r ubuntu 2>/dev/null || true \
 && groupadd -g 1000 app \
 && useradd -u 1000 -g 1000 -m -s /usr/sbin/nologin app

COPY --chown=1000:1000 --from=builder /build/target/app.jar app.jar
# 用数字 UID:GID 而非用户名：K8s runAsNonRoot: true 未覆写 runAsUser 时只认数字 UID，写 USER app 会报 CreateContainerConfigError
USER 1000:1000
```

**非 root Nginx 额外注意**：监听非特权端口（如 `8080`），将 `pid` 与临时目录指向 `/tmp`，并设置 `port_in_redirect off; absolute_redirect off;`，避免 Ingress 后方 301 重定向暴露容器内 `:8080`。

部署清单侧必须同步（见 `deploy-securitycontext-match-image`）。
