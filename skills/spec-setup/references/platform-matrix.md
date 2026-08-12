# 形态覆盖矩阵

**形态是多选的。** 一个仓里同时有后端服务 + Web 前端 + 小程序是常态。多形态时每个形态必须绑定到具体模块目录，否则 `.claude/rules` 的 `paths:` 只能写全仓通配（`guards.md` G2）。

## 矩阵

| 形态 | 继承（直接启用 skill） | 缺口（走推荐 + Context7 定版） |
|---|---|---|
| **Web fullstack** | `frontend-ui` + `spring-boot` + `devops` + `doc-writing` | 无（若后端不用 Java 见下方"部分继承"） |
| **后端服务（纯 API）** | `spring-boot` + `devops` + `doc-writing` | 无（同上） |
| **桌面应用** | `frontend-ui`（部分）+ `devops` + `doc-writing` | 打包与自动更新、主进程/渲染进程边界、原生能力调用 |
| **CLI 工具 / SDK 库** | `devops` + `doc-writing` | 公开 API 稳定性、版本与废弃策略、发布流程、参数与退出码约定 |
| **Mini Program** | `devops` + `doc-writing` | **全部**：目录与分包、状态管理、原生能力与权限、审核合规 |
| **Android App** | `devops` + `doc-writing` | **全部**：架构分层、依赖注入、异步与生命周期、权限、混淆与发布 |
| **iOS App** | `devops` + `doc-writing` | **全部**：架构分层、并发模型、权限、签名与发布 |

`devops` 与 `doc-writing` 跨形态通用，**基本恒选**：前者覆盖容器化、CI、凭据；后者覆盖中文技术文档。除非项目明确不落容器、不写中文文档，否则都启用。

## 既有 skill 锁定的栈

继承一个 skill 等于继承它的栈。启用前先确认栈匹配，不匹配就是"部分继承"或不继承。

| Skill | 锁定的栈 | 边界 |
|---|---|---|
| `frontend-ui-best-practices` | React + shadcn/ui，**后台管理系统**形态 | 16 条规则集中在表单、列表、弹窗、格式一致性。C 端营销页、可视化大屏、移动 Web 只能部分适用 |
| `spring-boot-best-practices` | Spring Boot 3 + Java 21 + MyBatis Plus + 国密 SM2/SM3/SM4 | 40 条规则含分层依赖、响应包装、多方言迁移。换 JPA 或换语言则不继承 |
| `devops-best-practices` | Docker / docker-compose / K8s / Kustomize / Helm / process-compose / CI | 26 条规则，与应用语言无关 |
| `doc-writing-best-practices` | 中文技术文档（Markdown） | 8 条规则，与技术栈无关 |

**部分继承怎么处理**：只启用 skill，并在 `CLAUDE.md` 里写明适用边界（如"`frontend-ui` 的表单与列表规则适用；本项目是 C 端页面，弹窗与工具栏规则按情况取舍"）。不要为了"更贴合"去改通用 skill 的内容——那会污染其他项目。

## 缺口的推荐原则

推荐要给取舍理由，不要只报名字。三条判据：

1. **单目标不上抽象层** —— 只有一个小程序目标时，跨端框架的抽象层只剩成本。多端才值。
2. **优先社区默认** —— 新项目没有历史包袱，偏离社区默认要有具体理由，否则后续招人、查文档、接 AI 工具全是摩擦。
3. **能被既有 skill 接住的优先** —— 后端在 Java 与 Go 之间摇摆且无硬理由时，选 Java 意味着 40 条规则立刻到位。这是真实的成本差。

## 定版范围

只核对**主框架与关键依赖**：运行时、框架、ORM、UI 库、构建工具。周边库不查。

记录格式带核对日期，否则半年后没人知道该不该重查：

```
Spring Boot 3.5.x（Context7 核对于 2026-08-12）
React 19.x（Context7 核对于 2026-08-12）
```

**训练数据里的版本号一律不足采信**，即使很确定。这正是 Context7 存在的理由。

## 追加新形态

新增一行时，四件事缺一不可：

1. 形态名与典型判定特征（凭什么认出它）
2. 继承列——逐个确认既有 skill 的栈是否真的匹配，不确定就归入缺口
3. 缺口列——列出该形态**特有**的规范领域，不要抄别的形态
4. 若该形态零覆盖，在 `SKILL.md` 第 3 步的零覆盖清单里同步加上

同步改动 `SKILL.md` 第 2 步的形态清单枚举。**这份文件与 `SKILL.md` 的清单不同步是沉默故障**——用户会看到一个 `SKILL.md` 里没有的形态，或反之。
