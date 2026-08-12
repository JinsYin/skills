---
name: spec-triage
description: 为一个项目建立或整顿编码规范：勘察代码库取证、只就推断不了的事访谈、再把每条约定按加载成本分诊到 CLAUDE.md / 通用 skill / .claude-rules / 项目文档四层，并检测既有规范与代码库的漂移。在用户说「给这个项目建规范」「整顿 CLAUDE.md 和 rules」「规范和代码对不上了」「检查规范漂移」「spec-triage」时使用，也用于新项目初始化规范、或规范文件膨胀到该拆分时。
argument-hint: "[--check | --tier claude-md|skill|rules | --dry-run]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# spec-triage

## Codex Adapter

In Codex, translate this wrapper instead of rewriting it:

- `$ARGUMENTS` = text after the command name.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise print each option's content in your reply, list choices as a numbered Markdown list, and **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use equivalent Codex tools.

---

建立或整顿一个项目的编码规范。**核心不是「生成规则文件」，而是分诊** —— 把每条约定路由到加载成本正确的那一层。Reply in Chinese.

## 为什么分诊是核心

规范出问题从来不是「写得不够多」，而是两种错配：

- **放错层** —— 只在写 Java 时才需要的 DTO 命名表，被放进「写代码之前就必然加载」的位置。实测案例：11 个规则文件的 `paths:` 都带着该项目工作流的产物通配（那次是 GSD 的 `.planning/**/*-PLAN.md`），导致任何规划命令无差别注入约 10.5 KB，且子代理各付一遍。换个工作流只是路径不同，机制一样。
- **漂移** —— 规则说 Flyway 是双路、项目早已三层；`paths` 写 `**/*.vue` 而项目零个 `.vue`，规则从未命中过。两种失效都不报错，只能靠审计发现。

分诊同时解决这两点：路由正确则成本正确，且每层有明确归属后，漂移检测才有靶子。

## 四层与判据

| 层 | 加载时机 | 成本 | 该放什么 | 预算 |
|---|---|---|---|---|
| `CLAUDE.md` | 每会话常驻 | 每会话、每子代理都付 | 本项目**已裁决**的具体约束、锁定决策 | ≤ 150 行 |
| 通用 skill | 触发读索引，按需读单条 | 索引一次 + 实际读的几条 | **跨项目通用**的规范 | 索引 ≤ 200 行，单规则 ≤ 80 行 |
| `.claude/rules` + `paths:` | 命中路径时注入全文 | 按文件类型付 | 窄领域、内容极少、不值得建 skill | 单文件 ≤ 60 行 |
| 项目文档 / references | 显式查阅 | 仅查表时付 | 长尾查表、脚手架模板 | 不限 |

**决策树**（完整判例见 `references/tier-routing.md`）：

```
这条约定换个项目还成立吗？
├─ 是（通用）
│   └─ 已有对口 skill？ → 加进去 ／ 否则评估是否够量建新 skill
│                          （不够量 → .claude/rules）
└─ 否（本项目特有）
    ├─ 违反即 bug / 会被反复"修复"的锁定决策 → CLAUDE.md
    ├─ 只在改某类文件时才可能犯，且内容极少 → .claude/rules + 窄 glob
    └─ 只是"想不起来具体写法"              → 项目文档
```

第一问必须先答。把通用规范塞进 `CLAUDE.md` 会让每个会话都为其他项目也适用的内容付费；把项目专属决策塞进通用 skill 则会污染其他项目。

## 0 — 解析参数

| 参数 | 行为 |
|---|---|
| 无 | 完整流程：勘察 → 分诊 → 访谈 → 落地 |
| `--check` | **只报漂移，不改任何文件** |
| `--tier <层>` | 只整顿指定层（`claude-md` / `skill` / `rules`） |
| `--dry-run` | 走完全流程但只输出改动计划 |

## 1 — 勘察（先取证，别先问）

用 Bash / Grep / Glob 摸清现状，**每个结论都要有出处**。至少覆盖：

- **技术栈与版本** —— 构建文件、锁文件、实际依赖，不看 README 的自述
- **模块布局** —— 哪些目录是源码、哪些是生成物、有无仓内多语言
- **既有规范** —— `CLAUDE.md`、`.claude/rules/**`、已启用 skill、`AGENTS.md` 等入口文件各覆盖了什么
- **真实模式与偏离率** —— 不是"应该怎么写"，是"实际怎么写的，多少处不一致"
- **构建 / 测试 / lint 命令** —— 从脚本与 CI 配置里取，不猜
- **高频文档与工作流产物路径** —— 本项目有没有在用某种规划/任务工作流（GSD、`docs/adr/**`、issue 模板…），它的产物落在哪；这是 G1 判定的输入，**不要假定，查了再说**
- **规范时效性** —— `git log -1 -- CLAUDE.md` 之后有多少提交；差距大就默认它已漂移

勘察产出一张证据表，作为后续每一步的依据。**没有出处的结论不得进入分诊。**

## 2 — 分诊

对每条候选约定，先答「通用还是本项目」，再按决策树定层。输出一张路由表：

```
约定                      当前位置              建议位置            理由
分层依赖 Controller→...   .claude/rules(注入)   spring-boot skill   跨项目通用
包名锁定 com.x.dap.*      CLAUDE.md             CLAUDE.md（不动）   本项目已裁决
上游异常透传 D-01~04      .claude/rules(注入)   CLAUDE.md           项目锁定决策，
                                                                    须对审查可见
```

冲突处理：同一条约定在多层重复出现时，**保留成本最低的那层**，其余删除并在保留处补一句指向说明。

## 3 — 访谈

**只问勘察定不了的**。每个问题都要先给证据，再问选择：

> 扫了 47 个 Controller：42 个用 `page/get/create`，3 个 `queryPage`，2 个 `listPage`。
> 定哪个为准？另外 5 个要不要一并列进技术债？

| 勘察能定（不问） | 必须问（勘察定不了） |
|---|---|
| 技术栈、模块布局、包结构 | 哪些是硬约束、哪些只是偏好 |
| 实际命名/分层模式与偏离率 | 未来意图（"要迁到 X"，代码里看不见） |
| 既有规范的覆盖面与重复 | 团队返工热点 |
| 构建/测试/CI 命令 | 禁区、已裁决不得反转的决策 |

用 `AskUserQuestion` 批量提问，一轮不超过 4 个。问题库见 `references/interview-bank.md`。

## 4 — 落地

按路由表写入。写之前**逐条过 `references/guards.md` 的硬闸**，命中即停下报告，不要自行放宽。

新增或修改规则内容时，遵守 `references/rule-authoring.md`：每条必须写清「为什么」和「违反的后果」——只写「应该这样」的规则，agent 遵守率显著低。

**删除既有规范时，三步缺一不可**（这三条都是实战踩出来的）：

1. **覆盖度比对** —— 逐条确认待删内容已被目标层覆盖。实测中一次迁移差点丢掉三处：权限注解约定、字段类型约定、以及一条明确写着"不得删除"的锁定决策。
2. **悬空引用检查** —— `grep` 全仓找指向待删文件的引用，尤其是其他 skill / command 里的 `@path` 文件引用。它们失效时**不报错**，只是约束静默消失。
3. **删除后复查** —— 再 grep 一次确认无残留。

## 5 — 校验

改完必须验，逐项报告结果：

- **skill 索引 ↔ 规则文件严格一一对应** —— 这是索引式结构唯一的沉默故障：索引多写一条，agent `Read` 失败；漏写一条，规则永远不被发现
- **`paths:` 合法** —— 不覆盖高频文档与工作流产物（判据见 `references/guards.md` G1）、glob 锚到模块
- **无跨层重复**
- **各层未超预算**
- **全仓无悬空引用**
- **编译产物已重建**（若 skill 带 `scripts/build.sh`）

## `--check` 模式

只做勘察 + 漂移检测，**不写任何文件**。逐条给出证据：

```
⚠ .claude/rules/framework/springboot/01-stack.md
   称 Flyway 双路 (mysql|gauss)，实际三层 (gauss-base|centralized|distributed)
   证据：db/migration/ 下 4 个目录
⚠ CLAUDE.md
   最后改动距今 641 个提交；docker-compose 注释称启动 MySQL，
   实际 mysql 挂在 profile 下不默认启动
```

适合在一个阶段收尾时跑——发版前、大改动合并后，或（若项目用阶段化工作流）挂在 phase 收尾之后。规范烂掉是渐进的，等到有人踩坑才发现就晚了。
