---
name: spec-setup
description: 为新项目从零建立编码规范：先访谈定项目形态（Web fullstack / 后端服务 / 小程序 / Android / iOS / CLI·SDK / 桌面应用，支持一仓多形态），再从既有 *-best-practices skill 继承技术栈与规范、缺口走推荐、主框架经 Context7 定版本，最后只固化已裁决的少量约束并显式留白与记录复查触发点。在用户说「新项目建规范」「初始化 CLAUDE.md 和 rules」「刚建的仓库要定规范」「选型定了帮我固化下来」「spec-setup」时使用。存量项目（已有实质业务代码）改用 spec-triage。
argument-hint: "[--dry-run]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
---

# spec-setup

## Codex Adapter

In Codex, translate this wrapper instead of rewriting it:

- `$ARGUMENTS` = text after the command name.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise print each option's content in your reply, list choices as a numbered Markdown list, and **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Context7 工具名是意图标签；若 Codex 无 Context7，改用可用的文档检索手段，并在产出里注明版本未经核对。
- Claude tool names are intent labels; use equivalent Codex tools.

---

为新项目从零建立编码规范。Reply in Chinese.

## 核心：治的是「猜写」，不是「漏写」

`spec-triage` 治**漂移**——规范与代码对不上。新项目还没有代码，谈不上漂移，它的失败模式是另一种：

**猜写** —— 代码还没落地就铺满 50 条规则，其中多数是模板作者的假设，而非本项目的裁决。等真代码写出来，规范开始处处对不上；而因为"规范上写着"，没人敢删。**新项目最贵的规范条目，是那些当时没人真正决定过的条目。**

所以本 skill 只固化**已裁决的**，其余**显式留白**并记下复查触发点。宁可少写十条，也不要写一条没人拍过板的。

## 第二个机制：栈从既有 skill 继承，不从零推荐

`*-best-practices` 系列不只是「规范内容」，它们同时锁定了**一套已验证的技术栈**（`spring-boot-best-practices` = Spring Boot 3 + Java 21 + MyBatis Plus；`frontend-ui-best-practices` = React + shadcn/ui 后台管理）。

于是选型与建规范是同一件事：

```
形态匹配既有 skill  → 整套继承（栈 + 规范一次到位，边际成本为零）
skill 未覆盖的部分  → 走推荐（带理由，逐项确认）
主框架与关键依赖    → Context7 核对当前版本
```

继承优先于推荐。凭空推荐一套栈，等于把已经验证过的规范资产扔掉重来。

## 0 — 解析参数

| 参数 | 行为 |
|---|---|
| 无 | 完整流程：勘察 → 形态 → 栈 → 决策 → 播种 → 校验 |
| `--dry-run` | 走完全流程但只输出改动计划，不写任何文件 |

访谈**一次走完**（约 3-4 轮），最后统一写入。不要写一半停下来问——半套规范比没有更难收拾。

## 1 — 轻勘察：先确认这真是新项目

新项目没什么可取证的，这一步只回答一个问题：**起点在哪。**

```bash
git ls-files | wc -l                    # 纳管文件数
git rev-list --count HEAD 2>/dev/null   # 提交数
ls package.json pom.xml build.gradle* Cargo.toml go.mod pubspec.yaml 2>/dev/null
ls CLAUDE.md AGENTS.md .claude/rules 2>/dev/null
```

| 判定 | 特征 | 走向 |
|---|---|---|
| 空仓 | 无构建文件，或仅有 README/LICENSE | 形态与栈全靠访谈 |
| 脚手架已生成 | 有构建文件与锁文件，业务源文件近乎为零 | **栈从锁文件取证**，只补问未定项 |
| 其实是存量 | 有实质业务代码（几十个源文件以上），或已有 `CLAUDE.md` / `.claude/rules` | **停下**，报告证据并建议改用 `spec-triage` |

第三种要真的停下。存量项目的正确起手是勘察取证与分诊，硬套「从零建立」会覆盖掉既有约定。若用户明确表示知情并坚持，继续，但在收尾报告里注明既有规范被绕过。

**顺带探 monorepo**：多个构建文件、`workspaces` / `pnpm-workspace.yaml` / Gradle `settings` 多模块、`apps/`+`packages/` 布局——命中任一，则形态很可能是多选，第 2 步要为每个形态问清模块目录。

## 2 — 形态访谈

**形态是多选的。** 一个仓里同时有后端服务 + Web 前端 + 小程序是常态，不是特例。

形态清单与覆盖矩阵见 `references/platform-matrix.md`（**先读它再问**，清单会随时间追加）。当前收录：Web fullstack、后端服务（纯 API）、Mini Program、Android App、iOS App、CLI 工具 / SDK 库、桌面应用。

多形态时必须追问**每个形态落在哪个模块目录**：

```
后端服务  → server/
Web 前端  → web/
小程序    → miniapp/
```

这张映射是后面 `.claude/rules` 的 `paths:` 的唯一输入。**没有它就只能写全仓通配，而全仓通配会在无关模块上命中**（`references/guards.md` G2）。目录还没建时照样要问清计划的路径，并在校验阶段标注"待目录落地后复核 glob"。

## 3 — 栈解析

对每个形态，按 `platform-matrix.md` 走三步：

**继承** —— 矩阵里标为覆盖的，直接进"启用 skill"清单，栈随之确定。不要重述这些 skill 的内容，启用即可。

**推荐** —— 矩阵里的缺口逐项给带理由的建议，用 `AskUserQuestion` 让用户确认或推翻。推荐要写清取舍，不要只报一个名字：

> 小程序端没有对口 best-practices skill。建议用原生 + TypeScript 而非跨端框架：本项目只有一个小程序目标，跨端框架的抽象层在单目标下只剩成本。若后续要上多端，这条要重新裁决。

**定版** —— 主框架与关键依赖（运行时、框架、ORM、UI 库、构建工具）走 Context7：`resolve-library-id` → `query-docs`，取当前稳定版本。**周边库不查**。记录格式：

```
Spring Boot 3.5.x（Context7 核对于 2026-08-12）
```

版本与核对日期一起记，否则半年后没人知道该不该重查。**训练数据里的版本号一律不足采信**，即使你"确定"。

**零覆盖形态**（Mini Program / Android / iOS）：全部走推荐 + 定版，规范落项目层。收尾时提示一句"这部分累积够了可以用 skill-creator 抽成 `<stack>-best-practices`"，但**不要当场抽**——代码还没写就抽通用规范，正是本 skill 要治的猜写。

## 4 — 决策访谈

问题库见 `references/interview-bank.md`。核心四问：

| 问什么 | 为什么必须问 |
|---|---|
| 哪些是硬约束、哪些只是偏好 | 全标硬约束等于没分级，冲突时 agent 无从取舍 |
| 禁区与锁定决策 | 不写进常驻层，会被自动审查反复当缺陷"修复" |
| 未来意图（要迁到什么、要拆什么） | 新项目的方向只在人脑里，代码里一点痕迹都没有 |
| **哪些领域现在故意不定** | 这是留白清单的来源，也是本 skill 与模板方案的分水岭 |

最后一问要主动问，用户不会自己提。参考问法：

> 命名细则、错误码编排、测试分层这三块，现在拍板还是等首个模块落地后再定？现在定的话我需要你给出具体规则；不定的话我记进留白清单，等触发点到了再回来补。

## 5 — 播种四层

四层模型与决策树见 `references/tier-routing.md`，写法见 `references/rule-authoring.md`，初始模板与预算见 `references/seeding.md`。

第一问永远是「这条约定换个项目还成立吗」。新项目尤其容易犯的错是把继承来的通用规范抄进 `CLAUDE.md`——**继承的是 skill，不是它的内容**。

| 层 | 新项目该放什么 | 预算 |
|---|---|---|
| `CLAUDE.md` | 已裁决的项目约束 + 启用了哪些 skill + **规范复查触发点小节** | **≤ 60 行** |
| 通用 skill | 只写"启用哪些"，不复制内容 | — |
| `.claude/rules` | 推荐得来的缺口规范，`paths:` 按第 2 步的模块映射锚定 | 单文件 ≤ 60 行 |
| 项目文档 | 选型理由、版本与核对日期、被推翻的方案 | 不限 |

`CLAUDE.md` 预算收紧到 60 行（`spec-triage` 是 150），因为新项目大部分还没裁决。**写不满是正常的，写满才要警惕。**

「规范复查触发点」小节必须落进 `CLAUDE.md` 而非项目文档——只有常驻层能保证它在场。格式见 `references/seeding.md`，三到五行，写清留白领域与何时回来补：

```markdown
## 规范复查触发点

当前留白：命名细则、错误码编排、测试分层——首个模块落地后回来定。
触发点：首个模块合并后、首次代码审查后、引入第二个形态时，跑 `spec-triage --check`。
```

## 6 — 硬闸与校验

写入前逐条过 `references/guards.md`，**命中即停下报告，不要自行放宽**。新项目场景要额外盯三条：

- **G3（glob 必须真能命中）** —— 新项目目录还没建全，空 glob 是这里最高发的沉默故障。目录尚未存在时不能"先写着"，要么等目录落地，要么在复查触发点里显式记一笔。
- **G2（glob 锚到模块）** —— 多形态仓的直接后果，见第 2 步的模块映射。
- **G11（不得写入尚未裁决的约定）** —— 本 skill 专属闸，判据见 `guards.md`。

改完逐项报告校验结果：

```
✓ paths glob 命中数    server/**/*.java → 0（目录未建，已记入复查触发点）
✓ CLAUDE.md 行数       41 / 60
✓ 无跨层重复           继承的 skill 内容未被复制进 CLAUDE.md
✓ 复查触发点小节       已写入，留白 3 项
✓ 版本记录             主框架 4 项均带 Context7 核对日期
```

## 7 — 交棒

收尾报告必须说清三件事：

1. **写了什么、故意没写什么** —— 留白清单要复述一遍，不能只躺在文件里。
2. **什么时候改用 `spec-triage`** —— 首个模块合并后、首次代码审查后跑 `spec-triage --check`；之后的整顿一律走 triage，本 skill 不再适用。
3. **零覆盖形态的后续** —— 若有 Mini Program / Android / iOS 等，提示规范累积到够量（3 个以上分类、10 条以上规则）时可用 `skill-creator` 抽成 `<stack>-best-practices`。

## references

| 文件 | 内容 |
|---|---|
| `platform-matrix.md` | 形态清单 → best-practices 覆盖矩阵、各形态默认栈候选与缺口 |
| `interview-bank.md` | 新项目问题库：形态、选型、边界、留白；含「不要问的」 |
| `seeding.md` | 四层初始模板、新项目预算、复查触发点写法 |
| `tier-routing.md` | 分诊判例、五种常见误判（与 `spec-triage` 共用） |
| `guards.md` | 硬闸，每条对应一次实际故障（与 `spec-triage` 共用） |
| `rule-authoring.md` | 规则写法：为什么必须写「后果」（与 `spec-triage` 共用） |
