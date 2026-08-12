# spec-setup

为**新项目**从零建立编码规范。**核心是克制，不是铺满。**

已有实质业务代码的存量项目用 `spec-triage`——那里有代码可取证，起手式完全不同。

## 治的是「猜写」

| Skill | 治什么 | 失败长什么样 |
|---|---|---|
| `spec-setup` | **猜写** | 代码还没落地就铺满 50 条规则，多数是模板作者的假设而非本项目的裁决 |
| `spec-triage` | **漂移** | 规则说 Flyway 双路，项目早已三层；`paths` 写 `**/*.vue`，项目零个 `.vue` |

猜写比漂移更难修：漂移至少能看出两边不一致，猜写从一开始就没有对照物。而且因为"规范上写着"，后来者不敢删，只会绕着写。

所以本 skill 只固化**已裁决的**，其余**显式留白 + 记下复查触发点**。`CLAUDE.md` 预算收紧到 60 行（`spec-triage` 是 150）。**写不满是正常的，写满才要警惕。**

## 栈从既有 skill 继承，不从零推荐

`*-best-practices` 不只是规范内容，它们同时锁定了一套已验证的技术栈。于是选型与建规范是同一件事：

```
形态匹配既有 skill  → 整套继承（栈 + 规范一次到位，边际成本为零）
skill 未覆盖的部分  → 走推荐（带理由，逐项确认）
主框架与关键依赖    → Context7 核对当前版本，记录版本 + 核对日期
```

后端在 Java 与 Go 之间没有硬理由时，选 Java 意味着 40 条规则立刻到位——这是真实的成本差，值得摆到台面上。

## 形态是多选的

一个仓里同时有后端服务 + Web 前端 + 小程序是常态，不是特例。当前收录七种形态，覆盖矩阵见 `references/platform-matrix.md`：

| 形态 | 继承 | 缺口 |
|---|---|---|
| Web fullstack | `frontend-ui` + `spring-boot` + `devops` + `doc-writing` | — |
| 后端服务（纯 API） | `spring-boot` + `devops` + `doc-writing` | — |
| 桌面应用 | `frontend-ui`（部分）+ `devops` + `doc-writing` | 打包与自动更新、进程边界 |
| CLI 工具 / SDK 库 | `devops` + `doc-writing` | 公开 API 稳定性、版本与废弃策略 |
| Mini Program | `devops` + `doc-writing` | **全部** |
| Android / iOS | `devops` + `doc-writing` | **全部** |

多形态时每个形态必须绑到具体模块目录——这是 `.claude/rules` 的 `paths:` 的唯一输入，没有它就只能写全仓通配。

零覆盖形态的规范全落项目层，收尾时提示可用 `skill-creator` 抽成 `<stack>-best-practices`，但**不当场抽**：代码还没写就抽通用规范，正是本 skill 要治的猜写。

## 流程

```
轻勘察（判起点）→ 形态访谈 → 栈解析（继承→推荐→定版）→ 决策访谈（含留白）
→ 播种四层 → 硬闸与校验 → 交棒 spec-triage
```

访谈一次走完（约 3-4 轮）后统一写入。写一半停下来，会留下半套规范——比没有更难收拾。

`--dry-run` 走完全流程但只输出改动计划。

## 留白怎么才算数

留白不是"没写"，是三行挂账，落在 `CLAUDE.md` 常驻层：

```markdown
## 规范复查触发点

当前留白：命名细则、错误码编排、测试分层——首个模块落地后回来定。
触发点：首个模块合并后、首次代码审查后、引入第二个形态时，跑 `spec-triage --check`。
未决 glob：`server/**/*.java`（目录未建，命中数 0，待落地后复核）。
```

三行各有职责：没有第一行，留白等于遗漏；没有第二行，留白永远不会被补；没有第三行，尚未存在的目录上那条 `paths:` 就是一条永不生效且无人知晓的规则。

## references

| 文件 | 内容 |
|---|---|
| `platform-matrix.md` | 形态清单 → 覆盖矩阵、既有 skill 锁定的栈、缺口推荐原则、追加新形态的规程 |
| `interview-bank.md` | 新项目问题库：形态、选型、边界、留白；含「不要问的」 |
| `seeding.md` | 四层初始模板、新项目预算、复查触发点与选型记录写法 |
| `tier-routing.md` | 分诊判例、五种常见误判（与 `spec-triage` 共用） |
| `guards.md` | 硬闸 G1～G11（与 `spec-triage` 共用；G11 为本 skill 专属） |
| `rule-authoring.md` | 规则写法：为什么必须写「后果」（与 `spec-triage` 共用） |

后三份是两个 skill 的共用地基，由本 skill 持有，`spec-triage` 反向引用。

## G11：本 skill 专属的那条闸

> 对每条准备写入的约定问一句「这条谁拍过板」。答案不是「用户在本次访谈里明确确认过」或「继承自已启用的 skill」，即命中——删掉，转入留白清单。

**留白是合格产出，猜写不是。** 这条闸是整个 skill 的收口。

## 启用

```bash
# 在仓库根目录执行；与 spec-triage 成对链接
mkdir -p "$HOME/.claude/skills"
ln -s "$(pwd)/skills/spec-setup"  "$HOME/.claude/skills/spec-setup"
ln -s "$(pwd)/skills/spec-triage" "$HOME/.claude/skills/spec-triage"
```

用符号链接而非拷贝，本仓才是唯一事实来源。
