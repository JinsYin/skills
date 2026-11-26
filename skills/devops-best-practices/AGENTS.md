# DevOps Best Practices

> 本文件由 `scripts/build.sh` 从 `rules/` 自动生成，请勿手工编辑。
> 生成时间：2026-11-26 20:43:31

## 1. 镜像构建


### 基础镜像前缀用 global ARG 参数化

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


### COPY 构建产物用确定文件名，不靠通配猜

`COPY --from=builder /build/target/app-*.jar app.jar` 依赖构建产物的命名恰好带版本号后缀。而构建配置（Maven 的 `<finalName>`、Vite 的 `build.outDir`）随时可能把它改掉——改完通配就匹配不到，`COPY` 失败。

代价在于**失败时机**：它发生在完整编译之后的最后一层，前面几分钟的构建全部作废，而错误信息只说找不到文件，不会提示是命名规则变了。

**错误（假定产物名含版本号）：**

```dockerfile
COPY --from=builder /build/target/app-*.jar app.jar
```

**正确（与构建配置约定确定名，用 ARG 参数化模块）：**

```dockerfile
ARG MODULE=app
# pom 中 <finalName>${project.artifactId}</finalName> → 产物即 ${MODULE}.jar
COPY --chown=1000:1000 --from=builder /build/${MODULE}/target/${MODULE}.jar app.jar
```

若确实无法固定命名，就在 builder 阶段先重命名成确定名，再在 runner 阶段按确定名 COPY。


### exec 形态的 ENTRYPOINT 不展开环境变量

`ENTRYPOINT ["java", "-jar", "app.jar"]` 是 exec 形态，**不经过 shell**，因此 `$JAVA_OPTS` 这类变量不会被展开——它会被当作字面量参数传进去，或者干脆不出现。

这是个沉默故障：容器正常启动、日志正常，只是你注入的 JVM 参数（时区、内存、GC）一个都没生效。

exec 形态仍是推荐默认（进程为 PID 1，能正确接收 SIGTERM）。所以正确解法**不是**改成 shell 形态，而是在需要注入变量的地方显式套一层 shell。

**错误（ConfigMap 注入的 JAVA_OPTS 完全不生效）：**

```dockerfile
ENTRYPOINT ["java", "$JAVA_OPTS", "-jar", "/app/app.jar"]
```

**正确（镜像保持 exec 形态；部署清单需要注入时覆盖 command/args）：**

```dockerfile
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

```yaml
# K8s 侧：exec 套 shell，用 exec 保证 java 仍是 PID 1
command: ["/bin/sh", "-c"]
args: ["exec java $JAVA_OPTS -jar /app/app.jar"]
```


### 先复制依赖清单再装依赖，最后复制源码

Docker 按层缓存，任一层的输入变了，**该层及其后所有层全部失效**。源码的变更频率远高于依赖清单，所以必须把 `COPY 源码` 放在 `install 依赖` 之后。

顺序写反不会报错，只是每次构建都重装依赖——本地感觉"有点慢"，在 CI 上是每次推送多几分钟。

**错误（改任意一行源码都会重新 install）：**

```dockerfile
COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm build
```

**正确（依赖层只在清单变化时失效）：**

```dockerfile
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . ./
RUN pnpm build
```

依赖安装必须用 lockfile 的严格模式（`--frozen-lockfile` / `npm ci` / `mvn -o`），否则缓存命中了也可能装出与本地不同的版本。


### 构建与运行分阶段，运行阶段只带运行时

多阶段构建不只是为了减小体积，更是为了**缩小攻击面**。单阶段镜像会把 JDK/Node、构建工具、源码、以及构建时用到的私库凭据文件全部留在产线镜像层里——即便最后一层删掉了，前面的层仍然可被提取。

运行阶段选最小可用运行时：Java 用 JRE 而非 JDK，前端产物用 nginx 而非 Node。

**错误（构建产物与工具链混在一层，`.m2/settings.xml` 里的私库凭据永久留在镜像中）：**

```dockerfile
FROM maven:3.9.9-eclipse-temurin-21
COPY . .
RUN mvn package
ENTRYPOINT ["java", "-jar", "target/app.jar"]
```

**正确（builder 阶段的一切都不进入 runner）：**

```dockerfile
FROM ${BASE_REGISTRY}maven:3.9.9-eclipse-temurin-21 AS builder
WORKDIR /build
COPY . .
RUN mvn -pl ${MODULE} package -am

FROM ${BASE_REGISTRY}eclipse-temurin:21-jre AS runner
WORKDIR /app
COPY --from=builder /build/${MODULE}/target/${MODULE}.jar app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```


### 非 root 运行，且 UID/GID 必须显式指定

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


### 显式声明时区，优先内置 tzdata 镜像实现零 OS 下包

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

## 2. 部署清单


### base 放公共资源，overlay 只放环境差量

Kustomize overlay（或 Helm 的 values 文件）的价值全在于**差量**。一旦某个 overlay 复制了整份 Deployment 而不是 patch，它就与 base 脱钩：后续在 base 上修的探针、安全上下文、标签，都不会传播到这个环境。

而这种脱钩不报错——`kubectl apply` 照样成功，只是这个环境悄悄停在了旧版本。

overlay 里应当只出现这几类：命名空间、副本数、资源限额、镜像 tag、域名/IP、环境标签。**其余一律回 base。**

**正确：**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base
  - secret.yaml

namespace: app-prod
commonLabels:
  env: prod

images:
  - name: registry.internal/org/app
    newTag: 1.4.2

patches:
  - path: replicas-patch.yaml
```

若发现某个 overlay 的 patch 越来越大，说明该差异其实应该参数化进 base，而不是继续堆 patch。


### 非敏感配置进 ConfigMap，敏感值进 Secret，用 envFrom 整体注入

ConfigMap 的内容以明文出现在 `kubectl describe`、事件日志和清单仓库中。密码、密钥、token 一旦写进去，等于公开——`kubectl get configmap -o yaml` 是很多人默认有的权限。

判据不是"看起来重不重要"，而是**泄漏后是否需要轮换**：需要轮换的，就是 Secret。

**正确：**

```yaml
envFrom:
  - configMapRef:
      name: app-config      # 端点、超时、开关、日志级别
  - secretRef:
      name: app-secret      # 密码、密钥、token
```

用 `envFrom` 整体注入而非逐条 `env: - name/valueFrom`：新增一个配置项时只改 ConfigMap，不必同步改每个 Deployment——后者极易漏改其中一个服务，且漏改不报错，只是那个服务读到空值。

Secret 的清单文件本身**不入库**（见 `secret-never-commit-real`），仓库里只保留 `secret.example.yaml`。


### Standardize Kubernetes Ingress on networking.k8s.io/v1 with Nginx ingressClassName

Write Kubernetes Ingress manifests with `networking.k8s.io/v1` and `spec.ingressClassName: nginx` (HuaweiCloud CCE reference: https://support.huaweicloud.com/usermanual-cce/cce_10_0364.html). Omitting `spec.ingressClassName` or using legacy `kubernetes.io/ingress.class` annotation fails on newer clusters or lets CCE provision default ELB Ingress instead of Nginx, leaving routes unreachable even after `kubectl apply` succeeds.

**Required fields and defaults:**

- **Header comment** — put `# HuaweiCloud CCE: https://support.huaweicloud.com/usermanual-cce/cce_10_0364.html` at top of every generated `ingress.yaml`.
- **API and class** — `apiVersion: networking.k8s.io/v1`, `kind: Ingress`, `spec.ingressClassName: nginx` (team default; override only per `deploy/README.md`). Replace legacy `kubernetes.io/ingress.class` annotation with `spec.ingressClassName`.
- **HTTP-only default** — omit `spec.tls` (TLS terminates upstream or stays internal); add `spec.tls` only when `deploy/README.md` requires in-cluster TLS.
- **Rules and backend** — set explicit `host`, `<path>`, `pathType: Prefix` (or `Exact` when needed), and numeric `backend.service.port.number` matching target Service `port`.
- **Kustomize and Helm dual-track** — omit env `metadata.namespace` in `k8s/base/ingress.yaml` (`overlays/<env>/kustomization.yaml` injects `namespace:`) and patch per-env `host` in overlays (`deploy-base-overlay-diff-only`); render `metadata.namespace` and `spec.rules` from `values-<env>.yaml` in Helm (`deploy-kustomize-helm-parity`).

**Wrong** — legacy annotation, unrequested `spec.tls`, hardcoded env namespace in Kustomize base:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: app-prod                       # hardcoded in k8s/base; breaks overlay reuse
  annotations:
    kubernetes.io/ingress.class: "nginx"    # deprecated; use spec.ingressClassName
spec:
  tls:                                      # unrequested TLS; breaks HTTP if Secret missing
    - hosts: [app.example.com]
      secretName: app-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app-frontend
                port:
                  number: 80
```

**Right** — rendered Ingress shape (Kustomize overlay and Helm template outputs match):

```yaml
# HuaweiCloud CCE: https://support.huaweicloud.com/usermanual-cce/cce_10_0364.html
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: <name>
  namespace: <namespace>
spec:
  ingressClassName: nginx # nginx ingress
  rules:
    - host: <host>
      http:
        paths:
          - path: <path>
            pathType: Prefix
            backend:
              service:
                name: <service_name>
                port:
                  number: <service_port>
```

Kustomize base, overlay patch, and Helm template skeletons: see `references/delivery.md`.


### Kustomize and Helm render the same resources for every environment

`deploy/k8s/` (Kustomize) and `deploy/helm/chart/` (Helm) = two renderings of one deployment. Env var, config key or Secret key added to one track deploys fine there; other track ships without it, and Pod fails or silently falls back to default only in envs deployed by that tool.

Map tracks one-to-one:

| Kustomize | Helm |
|---|---|
| `k8s/base/<resource>.yaml` | `helm/chart/templates/<resource>.yaml` |
| `k8s/overlays/<env>/` | `helm/chart/values-<env>.yaml` |
| env set under `overlays/` | env set of `values-*.yaml` |

**Wrong** — key added to one track only:

```yaml
# deploy/k8s/base/configmap.yaml
data:
  TZ: Asia/Shanghai        # helm/chart/templates/configmap.yaml never got it
```

**Right** — same task edits both, then verifies:

```bash
python3 deploy/scripts/k8s-parity.py              # all envs; exit 0 = in parity
python3 deploy/scripts/k8s-parity.py --env uat    # one env
```

Script ships with this skill as `scripts/k8s-parity.py`; copy into project's `deploy/scripts/` so CI and every agent run it. Renders both tracks per env, compares Kind/name sets, ConfigMap and Secret keys (never values), each container's env names and ports, and Ingress `ingressClassName`, `rules` (host/path/pathType/backend), and `tls`.

Change aimed at one track = change to deployment: make both tracks agree. E.g. ops taking over prod Secret → `secrets.create: false` in `values-prod.yaml` **and** `$patch: delete` for that Secret in `overlays/prod/`; else `kubectl apply -k` overwrites real Secret with placeholders.

`--ignore [ENV:]Kind/name` = last resort for difference one tool cannot express; record each with reason under `deploy/README.md` "Parity exceptions".


### 生产环境不用 latest，镜像 tag 必须确定

`latest` 让部署结果依赖"拉取那一刻仓库里是什么"。同一份清单在两个时间点 apply 会得到不同的镜像，而清单本身没有任何差异——事故复盘时无法回答"当时跑的是哪个提交"。

回滚更直接受害：`kubectl rollout undo` 回退的是清单版本，若前后清单都写着 `latest`，回退后拉到的仍是同一个镜像。

| 环境 | tag | 理由 |
|---|---|---|
| 本地 / 开发 | `latest` 可接受 | 追最新，且随时可重建 |
| 测试 / 预发 | `latest` 可接受 | 持续集成的目标就是最新 |
| **生产** | **必须确定版本号** | 可追溯、可回滚 |

生产用确定 tag 时，`imagePullPolicy` 应为 `IfNotPresent`（tag 不可变，无需每次拉取）；用 `latest` 的环境则必须 `Always`，否则节点上的旧缓存会让"最新"名不副实。

tag 的取值应与 CI 的 tag 策略同源（见 `ci-tag-strategy-single-source`），不要人工在清单里另起一套。


### securityContext 的 UID 必须与镜像内创建的用户一致

`runAsUser` 不会去镜像里查用户是否存在——它直接以该数值运行进程。若镜像里创建的是 UID 1001 而清单写 1000，进程会以一个镜像内**不存在的用户**运行：`whoami` 报错，`$HOME` 不存在，任何按用户名解析权限的逻辑都会失败。

挂载卷时更隐蔽：`fsGroup` 会把卷 chown 成指定 GID，若与进程实际 GID 不符，进程反而写不进自己的数据目录。

**正确（两处同源，并在注释里点明对应关系）：**

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000     # 与 Dockerfile 中 useradd -u 1000 一致
    runAsGroup: 1000
    # 无 PVC 时不要加 fsGroup——它会对所有卷做递归 chown，大卷上开销显著
```

`runAsNonRoot: true` 是必备的兜底：镜像若忘了 `USER` 指令，Pod 会直接拒绝启动，而不是悄悄以 root 跑起来。


### 三探针分工明确，慢启动用 startupProbe 而非调大 initialDelay

三个探针职责不同，不能互相替代：

| 探针 | 失败后果 | 管什么 |
|---|---|---|
| `startupProbe` | 重启容器 | 启动窗口，通过前另两个探针**不生效** |
| `livenessProbe` | 重启容器 | 进程死锁/僵死 |
| `readinessProbe` | 摘出 Service 端点 | 暂时不能接流量（依赖未就绪、正在预热） |

JVM、大型 Node 应用启动慢，常见的错误处置是把 `livenessProbe.initialDelaySeconds` 调到 120s 以上。副作用是**运行期的故障同样要等 120s 才被发现**——用启动期的宽容度买单了运行期的敏感度。

正确解法是用 `startupProbe` 单独覆盖启动窗口：它通过之前 liveness/readiness 都不生效，通过之后 liveness 立刻以正常的短周期工作。

**错误（启动宽容度污染了运行期）：**

```yaml
livenessProbe:
  httpGet: { path: /actuator/health/liveness, port: 8080 }
  initialDelaySeconds: 180
  periodSeconds: 15
```

**正确（启动窗口 = failureThreshold × periodSeconds = 300s）：**

```yaml
startupProbe:
  httpGet: { path: /actuator/health/liveness, port: 8080 }
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 30

livenessProbe:
  httpGet: { path: /actuator/health/liveness, port: 8080 }
  periodSeconds: 15
  failureThreshold: 3

readinessProbe:
  httpGet: { path: /actuator/health/readiness, port: 8080 }
  periodSeconds: 10
  failureThreshold: 3
```

liveness 与 readiness 必须指向**不同**的端点：liveness 只答"进程还活着吗"，readiness 才检查下游依赖。两者指向同一个含依赖检查的端点时，下游抖动会导致 Pod 被反复重启，而重启并不能修复下游。

## 3. 凭据与配置


### CI 里的凭据只能从 secret store 取，不写进 YAML

CI 配置文件（`.drone.yml` / `.gitlab-ci.yml` / workflow）是入库的，而且构建日志往往对整个团队可见。凭据写进去就是双重泄漏。

各家的取法不同但形态一致——声明引用，不写值：

```yaml
# Drone
username:
  from_secret: docker_username

# GitHub Actions
password: ${{ secrets.REGISTRY_PASSWORD }}

# GitLab CI —— 在项目 CI/CD Variables 中定义，YAML 里只用变量名
```

**注意插件与原生命令的差异**：许多 CI 插件支持 `settings.<key>.from_secret`，但你自己写的 `commands:` 步骤不走插件的 secret 解析。这时必须先经 `environment` 注入成环境变量，再在命令里引用：

```yaml
- name: deploy-sdk
  image: maven:3.9.9-eclipse-temurin-21
  environment:
    NEXUS_PASSWORD:
      from_secret: nexus_password
  commands:
    - mvn deploy -Dnexus.password=$NEXUS_PASSWORD
```

命令里引用环境变量而非直接内插密文，可避免它出现在 `set -x` 的回显中。


### 真凭据永不入库，仓里只留 example 模板

提交过的凭据不会因为下一个提交删掉它而消失——`git log -p`、任何一份克隆、以及所有 fork 里都还在。**唯一正确的处置是当作已泄漏，立刻轮换**，而不是删掉了事。

因此约束必须前移到"不可能提交"，而不是"记得别提交"：

```gitignore
# 真凭据文件，永不入库
deploy/k8s/overlays/*/secret.yaml
deploy/release/systemd/*.env
.env

# 模板必须入库（否则新人不知道要配哪些项）
!deploy/k8s/base/secret.example.yaml
!.env.example
```

模板与真文件成对存在：模板入库、列全所有键、值全部为占位；真文件被忽略、由部署者本地填。

**新增一个敏感配置项时，两个文件都要改。** 只改真文件不改模板，下一个部署的人会缺这一项——而缺失的表现通常是运行期某个功能静默不工作，不是启动失败。


### 占位值要显眼到不可能被当成真值

模板里的占位若写成 `password123`、`test-key`、`changeme`，它们看起来"像个值"——部署时容易被整段跳过，最终带上生产。而这类值通常不会导致启动失败，只会让加密、签名、鉴权在**看似正常**的情况下形同虚设。

占位要满足两条：一眼看出不是真值，且能被 grep 出来。

**错误：**

```yaml
DAP_CRYPTO_SM4_KEY: "0123456789abcdef"    # 像个合法密钥
DB_PASSWORD: "password"
```

**正确：**

```yaml
DAP_CRYPTO_SM4_KEY: "CHANGE_ME"
DB_PASSWORD: "CHANGE_ME"
```

上线前用一条命令兜底：

```bash
grep -rn 'CHANGE_ME' deploy/ && echo "❌ 存在未替换占位" && exit 1
```

这条检查应进发布清单（go-live checklist），而不是靠人记得。

**部分预填是合理的**：本地开发用的固定弱密码可以预填真值，但要就地注释说明"仅本地"，并确保该文件不用于其他环境。

## 4. 本地依赖编排


### 依赖服务必须配 healthcheck，且 start_period 覆盖真实启动耗时

容器"已启动"不等于"可服务"。数据库进程起来到能接受连接之间可能有几十秒，期间应用连上去会拿到连接拒绝或认证失败——**报错指向应用，根因在依赖**，这是本地环境最常见的误诊。

`start_period` 是关键参数：它期间的失败**不计入** `retries`，专门用于覆盖初始化窗口。首次初始化（建库、建表、导入种子数据）往往比后续启动慢一个数量级，`start_period` 要按首次算。

```yaml
healthcheck:
  # 探真实可服务性，不要只探端口
  test: ["CMD-SHELL", "gsql -U dap -d dap -c 'SELECT 1;' -h 127.0.0.1 || exit 1"]
  interval: 10s
  timeout: 10s
  retries: 15
  start_period: 90s     # 首次初始化建库建表，按最慢路径给
```

**探针要探真实可服务性**：`nc -z localhost 5432` 只证明端口在监听，而数据库在恢复期同样监听端口却拒绝查询。执行一条真实查询才是有效探测。

依赖方用 `depends_on` 的 `condition: service_healthy` 消费这个结果，否则 healthcheck 配了也只是好看。


### 可选与备用服务挂 profiles，默认不启动

`docker compose up -d` 应该恰好起**跑起项目所必需的那些**服务。备用数据库、可选中间件、调试工具若默认启动，会抢端口、吃内存，还会让新人误以为它们是架构的一部分。

```yaml
services:
  opengauss:            # 默认库，无 profiles → 零参数即启动
    image: opengauss/opengauss:5.0.0

  mysql:                # 备用库，仅在显式指定时启动
    profiles: [mysql]
    image: mysql:5.7
```

```bash
docker compose up -d                    # 只起默认集
docker compose --profile mysql up -d    # 显式追加备用库
```

**在文件头部用注释写明默认起哪些、备用怎么起。** compose 文件读者第一时间想知道的就是这个，而 `profiles` 分散在各服务定义里，通读一遍才能拼出全貌。

同时确保项目文档里的启动命令与此一致——文档说"起 MySQL"而实际默认起的是别的库，是最常见的一类文档漂移。


### 镜像 tag、端口、镜像源用环境变量参数化并提供 .env.example，严禁使用 :?

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


### platform 只在镜像确无原生架构时声明

`platform: linux/amd64` 会强制该服务走模拟层（ARM 机器上的 QEMU）。数据库这类 IO 与 CPU 双密集的服务在模拟层下可能慢数倍，且偶发难以复现的兼容问题。

很多 `platform` 声明是历史遗留：当年该镜像确实只有 amd64，后来上游发布了多架构 manifest，声明却没人去掉。

**加之前先确认镜像是否真的没有原生变体：**

```bash
docker manifest inspect <image>:<tag> | grep architecture
```

有 `arm64` 就不要加。确需保留时，就地注释写明**为什么**——否则下一个人无从判断能不能删：

```yaml
  mysql:
    image: mysql:5.7
    platform: linux/amd64   # 5.7 官方镜像无 arm64 变体，Apple Silicon 必需
```

反例是给整个 compose 文件统一加 `platform`——那会把本可原生运行的服务一并拖进模拟层。

## 5. CI 流水线


### Centralize repeated values in top-level global-variables YAML anchors

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


### 构建在指定镜像内进行，不依赖 CI 节点自带环境

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


### Annotate pipeline header and every step in .drone.yml

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


### Run independent build steps in parallel and wire downstream steps with depends_on

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


### Declare top-level platform explicitly in .drone.yml

Omitting `platform` defaults Drone to `linux/amd64`. On ARM64 runners, builds stall unscheduled or emit wrong-arch images that pass CI and crash on Kubernetes startup with `exec format error`.

Declare top-level `platform` right after `name: default`. Team default: `linux/arm64`; override `arch` only per `deploy/README.md`.

```yaml
kind: pipeline
type: docker
name: default

platform:
  os: linux
  arch: arm64
```


### Scope both pipeline trigger (ref + event) and every step when.event explicitly

Pipeline `trigger` gates whether pipeline runs; step `when` gates which steps participate.

- **Omitting `trigger.ref`** builds and pushes on every feature branch.
- **Omitting step `when.event`** re-runs all image builds and overwrites tags when `trigger.event` adds lightweight events (`promote`).

Enforce both layers:

1. **Top-level `trigger:`** declares `ref:` (`refs/heads/master`, `refs/tags/*`) and `event:` (`push`, `tag`; add `promote` only when promote steps exist).
2. **Every step** declares `when.event`; `promote` steps scope `when.target`, and tag-bound prod deploys also scope `when.ref: [refs/tags/*]` (prevents promoting `:latest` branch builds) with `depends_on: [clone]` to skip rebuilds.

```yaml
trigger:
  ref:
    - refs/heads/master
    - refs/tags/*
  event:
    - push
    - tag
    - promote

steps:
  - name: build-api
    when:
      event:
        - push
        - tag                     # promote does not rebuild images

  - name: deploy-prod
    depends_on: [clone]
    when:
      event:
        - promote
      target:
        - prod                    # scope promote to explicit target
      ref:
        - refs/tags/*             # tag-bound prod deploy only
```

Drone `when:` fields AND-only (no OR per step); `drone/envsubst` omits `${var:+alt}`. Keep tag-only prod promote as one step; for branch promotes without extra build steps, push dual tags (`latest` + short commit SHA) + registry retention rules.


### Build container images with pinned plugins/kaniko

Build all Drone container images with `plugins/kaniko` (team default: `plugins/kaniko:1.13.7`). Rootless in-container build needs no `docker.sock` mount or privileged DinD. Never use `plugins/docker` or floating tags.

**Required settings per Kaniko step:**

- `image: *KANIKO_IMAGE` — pin patch version (default `plugins/kaniko:1.13.7`); air-gapped/internal CI: mirror preserving upstream path (`registry.example.com/lib/plugins/kaniko:1.13.7`) + ensure Runner pull access (`ci-build-inside-container`).
- `environment.DRONE_OUTPUT: *DRONE_OUTPUT` (`/tmp/drone-output` in `global-variables:`) — omitting crashes Kaniko with `open : no such file or directory`.
- `settings.context: .` — explicit build context.
- `settings.skip_tls_verify: true` — team default for internal registries; set `false` only if `deploy/README.md` requires verified CA.
- `settings.username` / `settings.password` via `from_secret`; `image`, `registry`, `repo`, `tags`, `dockerfile` via `global-variables:` anchors (`ci-anchor-repeated-values`).
- `settings.build_args` — pass `*BASE_REGISTRY_ARG` (`image-base-registry-arg`), `MODULE=<service>` for shared Dockerfiles, and consumed language mirrors (`*NPM_REGISTRY_ARG`); add OS mirror only if Dockerfile installs OS packages from verified internal mirror (prefer zero OS downloads per `image-tz-explicit`).

**Correct:**

```yaml
- name: build-api
  image: *KANIKO_IMAGE
  environment:
    DRONE_OUTPUT: *DRONE_OUTPUT
  settings:
    registry: *DOCKER_REGISTRY
    repo: *REPO_API
    username:
      from_secret: registry_username
    password:
      from_secret: registry_password
    tags:
      - *DOCKER_TAG
    dockerfile: *DOCKERFILE_BACKEND
    context: .
    build_args:
      - *BASE_REGISTRY_ARG
      - MODULE=app-api
    skip_tls_verify: true
  when:
    event:
      - push
      - tag
```

**Optional semi-offline archive:** when `deploy/README.md` requires file-server/air-gapped delivery, add `tar_path: /drone/src/dist/images/<service>-${DRONE_TAG:-latest}.tar` under `settings:` and consume archives in downstream `depends_on` step (`ci-drone-dag-parallelism`).


### 镜像 tag 策略单一来源，部署清单与 CI 对齐

CI 决定推什么 tag，部署清单决定拉什么 tag。这两个决定必须来自同一条规则，否则就会出现"构建成功、部署成功、但跑的是上一个版本"——最难查的一类问题，因为每一步都显示绿色。

先把策略写成一句话，两侧都遵守它：

> push 到主干 → `latest`（预发环境消费）；打 tag → 版本号（生产消费）。

```yaml
# CI 侧
DOCKER_TAG: &DOCKER_TAG ${DRONE_TAG:-latest}
```

```yaml
# 部署侧（预发 overlay）
images:
  - name: registry.internal/org/app
    newTag: latest            # 对齐 CI：push 落 latest

# 生产 overlay
images:
  - name: registry.internal/org/app
    newTag: 1.4.2             # 对齐 CI：tag 落版本号
```

**生产侧的版本号应由发版脚本统一 bump**，不要人工在多个文件里各改一遍——服务数量一多，漏改一个的概率接近必然。若同时维护 Kustomize 与 Helm 两套清单，两者的版本必须一起改，并在文档里点明这个联动关系。

## 6. 本地进程编排


### process-compose is the single entrypoint and starts docker compose first

Two start commands (`docker compose up -d`, then `process-compose up`) → someone eventually runs only second: backend boots against absent database, error points at connection pool, not missing step. Agents especially start whatever last README line says.

`process-compose.yml` = only entrypoint. First process brings deps up, waits until healthchecks pass; every app process gates on it.

```yaml
processes:
  deps:
    # --wait (implies -d) blocks until every service healthcheck passes (rule compose-healthcheck-start-period);
    # --wait-timeout turns a dependency that never gets healthy into a failure instead of a hang
    command: "docker compose up --wait --wait-timeout 180"
    availability:
      restart: "no"          # one-shot (rule proc-oneshot-restart-no)

  backend:
    command: "./mvnw spring-boot:run"
    depends_on:
      deps:
        condition: process_completed_successfully
```

```bash
process-compose -u .process-compose.sock up -D      # whole stack, detached; -u avoids default port 9876 collision
process-compose -u .process-compose.sock down       # app processes only; dependency containers keep running
docker compose down                                 # stop dependencies explicitly (never -v unless resetting data)
```

Deps long-lived: `deps` defines no `shutdown` command, so `process-compose down` leaves containers and data running; next `up` fast. `--wait` treats service without `healthcheck` as ready once container runs, so app may connect before service accepts connections; give every default service healthcheck.


### 易错的启动前提写成守护进程，而不是写进文档

有些启动前提违反后不会立刻失败，而是在很远的地方以另一种形态爆出来：编译时漏了某个 profile，直到运行期连数据库才报协议不兼容；JDK 版本不对，报错停在某个无关的编译错误上。

这类前提写进 README 是无效的——需要它的人正好是不会去读的人。应当写成一个**启动链最前端的守护进程**，让违反直接变成一句清楚的报错。

```yaml
processes:
  profile-guard:
    command: "bash ./scripts/local-startup-guard.sh"
    availability:
      restart: "no"

  build-common:
    depends_on:
      profile-guard:
        condition: process_completed_successfully
```

守护脚本要做到两点：**退出码明确**（0 通过 / 非 0 阻断），**报错信息直接给出修法**而不只是说哪里不对。

守护的对象应是"自动化能查、人容易忘"的前提：必需的构建参数、工具版本、依赖服务是否在跑、必需的环境变量是否已设。不要守护那些本来就会立刻失败的东西——那是重复劳动。


### 不写死本机路径，继承启动 shell 的环境

`process-compose.yml` 是入库文件，会被所有人用。写死 `JAVA_HOME: ${HOME}/.sdkman/candidates/java/21.0.1` 之后，其他人克隆下来仍可能因安装方式或版本不同而跑不起来，而且修法是改一个入库文件——改完又会误提交回去。

process-compose 继承启动它的 shell 环境，因此**版本选择应该交给 shell**（sdkman / nvm / asdf / direnv），文件里只描述进程本身。

**错误：**

```yaml
processes:
  app:
    environment:
      - "JAVA_HOME=${HOME}/.sdkman/candidates/java/21.0.5-tem"
```

**正确（在文件头注释里声明前提，必要时用守护进程强制）：**

```yaml
# JDK 说明：后端进程要求 JDK 21，process-compose 继承启动它的 shell 环境，
#   请在 `process-compose up -D` 前确保当前 shell 的 JDK 为 21。
#   不写死 JAVA_HOME 以保持跨机器 / 跨安装方式可移植。
```

`environment` 里适合放的是**与本机无关的固定值**：功能开关、本地固定的弱密码、mock 服务的接入凭据。这些换机器不变，写进去反而消除了不确定性。

判据是一句话：**这一行换台机器还成立吗？** 不成立就不该出现在入库文件里。


### 一次性进程必须声明 restart:"no" 并被 depends_on 条件消费

process-compose 里既有长驻服务，也有"跑完就该结束"的前置进程（编译公共模块、跑迁移、环境自检）。后者若沿用默认重启策略，成功退出会被判为异常终止而重新拉起——形成无限构建循环，CPU 打满而看起来"还在启动中"。

```yaml
processes:
  build-common:
    command: "./mvnw -pl common install"
    availability:
      restart: "no"        # 一次性进程，成功退出后不再拉起

  app:
    command: "./mvnw -pl app spring-boot:run"
    depends_on:
      build-common:
        condition: process_completed_successfully
    availability:
      restart: on_failure  # 长驻服务，崩溃时重拉
```

`condition` 要选对：`process_completed_successfully` 才会等它**成功**结束；`process_started` 只等它开始，前置构建还没跑完服务就起来了，等于没配依赖。

长驻服务用 `on_failure` 而非 `always`——`always` 会在你主动停掉某个进程时又把它拉起来，调试时很碍事。


### process-compose uses unix domain socket to prevent port conflicts

`process-compose` defaults to TCP port 9876 for its internal REST API server. When running multiple projects concurrently on the same machine, subsequent projects fail on startup:

`FTL start http server on localhost:9876 failed error="listen tcp 127.0.0.1:9876: bind: address already in use"`

In detached mode (`-D`), the CLI exits 0 immediately while the background daemon crashes, misleading agents and developers into thinking the stack started.

Bind `process-compose` to a project-scoped Unix domain socket instead of a global TCP port:

```bash
process-compose -u .process-compose.sock up -D      # start stack detached
process-compose -u .process-compose.sock down       # stop stack
process-compose -u .process-compose.sock process list
```

Alternatively, set `PC_SOCKET_PATH=.process-compose.sock` in the shell or `.envrc` (`direnv`).

**Ignore socket file in Git:**
Runtime socket files are ephemeral machine-local endpoints and must never be tracked. Add `*.sock` to `.gitignore`:

```gitignore
*.sock
```

**Pitfalls to avoid:**
- **Do not use `--no-server`:** Disabling the HTTP server prevents port conflicts but breaks IPC completely—`process-compose down`, `attach`, and `process restart` will fail.
- **Do not use `-U` without path:** Bare `-U` creates `/tmp/process-compose-<pid>.sock` using the current client PID. A subsequent `process-compose -U down` runs under a different PID and fails to find the socket. Always specify a fixed path via `-u` or `PC_SOCKET_PATH`.

