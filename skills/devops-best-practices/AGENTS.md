# DevOps Best Practices

> 本文件由 `scripts/build.sh` 从 `rules/` 自动生成，请勿手工编辑。
> 生成时间：2026-08-12 00:07:47

## 1. 镜像构建


### 基础镜像前缀用 global ARG 参数化

本地开发机和 CI 节点通常走**不同的镜像源**：本地走公网镜像加速，CI 走内网仓库（外网不可达）。把源硬编码进 `FROM`，必然有一方拉不到。

写在第一条 `FROM` 之前的 `ARG` 是 **global ARG**，作用于本文件所有 `FROM`；写在 `FROM` 之后的 ARG 只在该阶段内有效。多阶段镜像里这个区别很容易踩错。

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

**基础镜像陷阱**：Ubuntu 24.04（noble）系基础镜像（含 `eclipse-temurin:21-jre`）已预置 `ubuntu` 用户占用 UID/GID 1000，直接 `groupadd -g 1000` 会因 GID 被占而失败（exit 4）。必须先释放。

**错误（UID 由系统分配，值不可控）：**

```dockerfile
RUN useradd -r -s /usr/sbin/nologin app
USER app
```

**正确（先释放占位用户，再钉死 1000）：**

```dockerfile
# userdel 对非 Ubuntu 基础镜像是无害 no-op
RUN userdel -r ubuntu 2>/dev/null || true \
 && groupadd -g 1000 app \
 && useradd -u 1000 -g 1000 -m -s /usr/sbin/nologin app

COPY --chown=1000:1000 --from=builder /build/target/app.jar app.jar
USER app
```

部署清单侧必须同步（见 `deploy-securitycontext-match-image`）。


### 显式声明时区，alpine 需额外装 tzdata

容器默认时区是 UTC，与宿主机无关。不显式声明，日志时间戳、定时任务触发点、以及任何依赖"当天"边界的业务逻辑都会偏移。

**glibc 系镜像**（debian/ubuntu 基础，含 temurin）通常已内置 tzdata，设 `ENV TZ` 即可。**musl 系镜像**（alpine）默认不含 tzdata，只设 `TZ` 无效——必须显式安装。

```dockerfile
# glibc 系：设置即可
ENV TZ=Asia/Shanghai

# musl 系（alpine）：必须补装 tzdata
ENV TZ=Asia/Shanghai
RUN apk add --no-cache tzdata
```

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


### 镜像 tag、端口、镜像源用环境变量参数化并提供 .env.example

开发机之间总有差异：本机已经装了 PostgreSQL 占着 5432、公司网络只能走内网镜像源、需要临时试另一个版本的数据库。这些差异若只能通过改入库的 `docker-compose.yml` 解决，改动就会被误提交，或者反复出现在每个人的工作区里。

```yaml
services:
  opengauss:
    image: opengauss/opengauss:${OPENGAUSS_IMAGE_TAG:-5.0.0}
    ports:
      # 宿主已占 5432 时在 .env 中覆盖 OPENGAUSS_HOST_PORT=5433
      - "${OPENGAUSS_HOST_PORT:-5432}:5432"
```

三条配套要求：

- **一律带默认值** `${VAR:-default}`，保证零配置可跑
- **`.env` 入 gitignore，`.env.example` 入库**，后者列全所有可覆盖项及说明
- **容器内端口不参数化**，只参数化宿主侧端口——容器内端口变化会牵动健康检查、服务间地址等一串配置

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


### 重复出现的仓库地址、tag 策略用 YAML anchor 收敛

同一个 registry 主机名在四个构建步骤里各写一遍，迁仓库时就要改四处。漏掉一处不会报错——那个步骤照常推送，只是推到了旧仓库，而清单从新仓库拉，表现为"镜像明明构建成功了但 Pod 拉不到"。

```yaml
global-variables:
  DOCKER_REGISTRY: &DOCKER_REGISTRY registry.internal
  REPO_ADMIN:      &REPO_ADMIN      registry.internal/org/app-admin
  # tag 策略：push 落 latest，打 tag 落版本号
  DOCKER_TAG:      &DOCKER_TAG      ${DRONE_TAG:-latest}

steps:
  - name: build-admin
    settings:
      registry: *DOCKER_REGISTRY
      repo: *REPO_ADMIN
      tags:
        - *DOCKER_TAG
```

收敛的判据是**是否会一起变**：registry 主机名、tag 策略、镜像源前缀会一起变，值得收敛；各服务的模块名不会一起变，不必收敛。

anchor 定义要集中在文件顶部并加注释说明用途。散落在各步骤中间定义的 anchor 比重复写更难读——读者得先找到定义处才知道 `*DOCKER_TAG` 是什么。


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


### 每个步骤显式限定触发事件，不靠继承流水线级条件

流水线级的 `trigger` 决定"这次要不要跑"，步骤级的 `when` 决定"这一步该不该参与这次跑"。只写前者时，所有步骤对所有事件一视同仁。

问题出在**新增事件类型的那一刻**：为了加一个只需执行轻量操作的事件（如 promote 一个部署标记、或手动触发一次数据同步），流水线级 `trigger` 被扩了一项，结果所有构建步骤跟着跑了一遍——重建镜像、重新推送、覆盖 tag。这不是假想，是每次扩 trigger 都会遇到的默认行为。

**正确（构建步骤只认 push/tag，轻量步骤只认它自己的事件）：**

```yaml
trigger:
  event: [push, tag, promote]

steps:
  - name: build-image
    when:
      event: [push, tag]          # promote 时不重建

  - name: write-deploy-marker
    when:
      event: [promote]
      target: [sync-db-pre]       # 进一步限定 promote 的目标
```

**新增任何步骤时，第一件事就是写 `when`。** 遗漏不会报错，只会在下一次非常规事件时以"为什么它又重新构建了"的形式暴露。


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

