# Sections

定义所有分类、排序、影响级别与描述。括号内的 section ID 即规则文件名前缀。

影响级别按**违反后果**划分，不是按出现频率：

| 级别 | 含义 |
|---|---|
| CRITICAL | 产线故障、安全问题，或构建/部署直接失败 |
| HIGH | 能跑，但会在环境切换、扩容或排障时咬人 |
| MEDIUM | 不一致或效率损失，功能正确 |
| LOW | 风格偏好 |

运维配置有一类独有的失效模式：**改动在本地看不出问题，只在另一个环境炸**。本 skill 的定级优先反映这一点——一条规则若违反后在开发机完全正常、到产线才暴露，即便"看起来只是风格"也按 HIGH 起步。

---

## 1. 镜像构建 (image)

**Impact:** CRITICAL
**Description:** Dockerfile 的分阶段、非 root、参数化与层缓存。镜像问题的代价不对称——构建期的错误立刻可见，而运行期的错误（UID 不匹配、时区、环境变量不展开）往往到部署后才暴露，且症状与根因相距很远。

## 2. 部署清单 (deploy)

**Impact:** CRITICAL
**Description:** K8s / Kustomize / Helm 的 base-overlay 分层、Nginx Ingress（`networking.k8s.io/v1` + `ingressClassName: nginx`、默认无 TLS）、三探针、安全上下文、配置与密钥分离。清单错误直接表现为 Pod 起不来、流量路由失败或反复重启，但探针配错的表现是"看起来正常"——流量打到没就绪的实例上。

## 3. 凭据与配置 (secret)

**Impact:** CRITICAL
**Description:** 真凭据永不入库、占位显式、CI 只从 secret store 取。一旦提交，历史里就永久存在——即便后续删除，也必须按泄漏处理并轮换。

## 4. 本地依赖编排 (compose)

**Impact:** HIGH
**Description:** docker compose 的 profile、健康检查、参数化与平台声明。本地环境的约定直接决定新人能否一条命令跑起来，也决定"我这儿是好的"这类问题的发生率。

## 5. CI 流水线 (ci)

**Impact:** HIGH
**Description:** Drone `.drone.yml` 强制 `plugins/kaniko` 构建、显式 `platform` 与 `trigger`/`when` 双层限定、顶部 `global-variables:` anchor 收敛、DAG 并行与 `depends_on`、注释规范及 tag 策略单一来源。CI 的错误只在推送后暴露，反馈周期以分钟计，因此约束要前移到写 YAML 的时刻。

## 6. 本地进程编排 (proc)

**Impact:** MEDIUM
**Description:** process-compose 的一次性进程、启动前置守护、可移植性。这一层的规则密度低但踩坑成本高——错误通常表现为"服务起来了但行为不对"，比起不来更难查。
