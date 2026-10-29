---
name: devops-best-practices
description: "Rules and playbooks for local dev env and delivery chain: Dockerfile, docker-compose.yml, process-compose.yml, Drone `.drone.yml`, Kubernetes Kustomize + Helm kept in parity, and `deploy/README.md` delivery facts. Use when writing, reviewing or planning any of these; when a task adds a database, cache, MQ or runnable process; when backfilling a missing dev env in an existing project; when planning or running a delivery phase (containerize, set up CI, deploy to k8s, release); or when adding a module, port, env var, config key or secret to a project that already has these files — even if no file is named."
license: MIT
metadata:
  author: JinsYin
  version: "1.0.0"
---

# DevOps Best Practices

容器化与部署的规范集，28 条规则分 6 类，按**违反后果**排序。

## 如何使用本 skill

**不要一次读完所有规则。** 先在下面的索引里定位与当前任务相关的条目，再按需 `Read` 对应文件：

```
rules/image-nonroot-explicit-uid.md
rules/deploy-three-probes.md
```

每条规则含：为什么、错误示例、正确示例。

选取原则——**按你正在改的文件定位，不按分类通读**：

| 你在改什么 | 先读 |
|---|---|
| `Dockerfile` | `image-*` |
| `docker-compose.yml` | `compose-*` |
| `process-compose.yml` | `proc-*` |
| CI 流水线配置 | `ci-*`、`secret-ci-from-store-only` |
| K8s 清单 / Kustomize overlay / Helm chart | `deploy-*`、`secret-*`、`deploy/README.md` |
| 新增一个服务（端到端） | `image-*` + `deploy-*` + `ci-tag-strategy-single-source` |
| 任何含凭据的文件 | `secret-*`（全部，只有 3 条） |
| 排查"构建成功但部署跑的是旧版本" | `ci-tag-strategy-single-source`、`deploy-no-latest-in-prod` |
| 排查"本地好的、产线不对" | `image-tz-explicit`、`image-entrypoint-exec-form-env`、`image-nonroot-explicit-uid` |

## Playbooks

Read before acting, not only before editing file:

| Situation | Read |
|---|---|
| First task needing a dependency or runnable process; project runs code but lacks `docker-compose.yml` or `process-compose.yml` | `references/dev-env.md` |
| Delivery phase/spec (containerize, CI, deploy, release); new deployable module; any change to a project that already has delivery files | `references/delivery.md` |

Project-specific facts (registries, secret names, environments) come from its `deploy/README.md`; missing → ask, never invent.

## 这类规范的共性

运维配置有一个区别于业务代码的失效模式：**改动在本地看不出问题，只在另一个环境炸**。而且症状与根因往往相距很远——UID 配错报的是"权限拒绝"，ENTRYPOINT 用 exec 形态报的是"参数没生效"（其实什么都不报）。

所以本 skill 的定级不完全按"严重程度"，而按**多久之后、在离根因多远的地方暴露**。一条规则若违反后本地完全正常、到产线才咬人，即便看起来只是风格问题，也按 HIGH 起步。

## 分类与影响级别

影响级别按**违反后果**划分：CRITICAL = 产线故障/安全问题/构建部署直接失败；HIGH = 能跑但会在环境切换、扩容或排障时咬人；MEDIUM = 不一致或效率损失；LOW = 风格偏好。

| 优先级 | 分类 | 影响 | 前缀 | 条数 |
|---|---|---|---|---|
| 1 | 镜像构建 | CRITICAL | `image-` | 7 |
| 2 | 部署清单 | CRITICAL | `deploy-` | 6 |
| 3 | 凭据与配置 | CRITICAL | `secret-` | 3 |
| 4 | 本地依赖编排 | HIGH | `compose-` | 4 |
| 5 | CI 流水线 | HIGH | `ci-` | 4 |
| 6 | 本地进程编排 | MEDIUM | `proc-` | 4 |

## 规则索引

### 1. 镜像构建（CRITICAL）

- `image-base-registry-arg` — 基础镜像前缀用 global ARG 参数化，否则本地或 CI 必有一方拉不到
- `image-copy-artifact-exact-name` — COPY 产物用确定文件名，通配匹配不到时在构建最后一步才失败
- `image-entrypoint-exec-form-env` — exec 形态 ENTRYPOINT 不展开 `$JAVA_OPTS`，注入的参数静默失效
- `image-layer-cache-manifest-first` — 先 COPY 依赖清单再装依赖，顺序反了每次改源码都重装
- `image-multistage-split` — 构建与运行分阶段，单阶段会把编译器与私库凭据带进产线
- `image-nonroot-explicit-uid` — 非 root 且 UID 显式指定；`useradd -r` 的系统 UID 与 K8s `runAsUser:1000` 不匹配
- `image-tz-explicit` — 显式 `ENV TZ`；alpine 需补装 tzdata，否则设了也不生效

### 2. 部署清单（CRITICAL）

- `deploy-base-overlay-diff-only` — overlay 只放差量，复制整份清单会让 base 的修复不再传播
- `deploy-config-secret-split` — 敏感值进 Secret；ConfigMap 明文出现在 `kubectl describe` 里
- `deploy-kustomize-helm-parity` — Kustomize and Helm render the same resources and keys per env; check with `scripts/k8s-parity.py`
- `deploy-no-latest-in-prod` — 生产用确定 tag，否则回滚回退了清单却拉到同一个镜像
- `deploy-securitycontext-match-image` — `runAsUser` 必须等于镜像内创建的 UID，否则挂载卷写不进去
- `deploy-three-probes` — 慢启动用 `startupProbe`，调大 liveness 的 `initialDelay` 会让故障期同样延迟发现

### 3. 凭据与配置（CRITICAL）

- `secret-ci-from-store-only` — CI 凭据只能 `from_secret`；`commands:` 步骤不走插件的 secret 解析
- `secret-never-commit-real` — 真凭据永不入库，提交过就必须按泄漏处理并轮换
- `secret-placeholder-explicit` — 占位用 `CHANGE_ME`；像真值的占位会被带上生产且不报错

### 4. 本地依赖编排（HIGH）

- `compose-healthcheck-start-period` — 必配 healthcheck 且探真实可服务性；`start_period` 按首次初始化给
- `compose-optional-behind-profile` — 备用服务挂 `profiles`，默认不起
- `compose-parameterize-env` — 宿主端口/tag/镜像源参数化并带默认值，配 `.env.example`
- `compose-platform-only-when-no-native` — `platform` 只在镜像确无原生架构时加，多余声明强制走模拟层

### 5. CI 流水线（HIGH）

- `ci-anchor-repeated-values` — registry/tag 用 YAML anchor 收敛；漏改一处不报错，只是推到旧仓库
- `ci-build-inside-container` — 构建步骤显式指定镜像并钉版本，不依赖节点自带工具链
- `ci-explicit-event-scope` — 每个步骤写 `when.event`；扩 trigger 时未限定的步骤会被意外触发
- `ci-tag-strategy-single-source` — CI 与部署清单的 tag 策略同源，否则"构建成功、部署成功、跑的是旧版本"

### 6. 本地进程编排（MEDIUM）

- `proc-deps-via-compose-wait` — process-compose is the only start command; its one-shot `deps` runs `docker compose up --wait`
- `proc-guard-before-start` — 易错前提写成守护进程而非文档；违反后的症状通常远离根因
- `proc-no-hardcoded-host-paths` — 不写死 `JAVA_HOME` 等本机路径，该文件是入库的
- `proc-oneshot-restart-no` — 一次性进程必须 `restart:"no"`，否则成功退出后被无限拉起

## 与项目规范的关系

本 skill 是**跨项目通用基线**。具体的仓库地址、secret 名称、模块名、镜像仓库主机名属于项目事实，应写在项目的 `CLAUDE.md` 或 `AGENTS.md`，不要写进这里。

冲突时以项目自身的约定为准。

## 维护

改动 `rules/` 后必须重新生成全量版：

```bash
bash scripts/build.sh
```

`AGENTS.md` 供不支持渐进披露的工具直接通读，不重建就会与规则源不一致，而它不会自己报错。
