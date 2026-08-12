# gsx

GSD 工作流的薄前门（thin front-door）skill 集。每个 skill 包裹一条或一组 `/gsd:*` 命令，并在移交前附加项目专属校验——Context7 文档核对、讨论前置、计划评审门禁等。

## 安装

```bash
# 在 Claude Code 中
/plugin marketplace add jinsyin/skills
/plugin install gsx@jinsyin
```

本地开发：

```bash
claude --plugin-dir plugins/gsx
```

## 前置依赖

这些 skill 是 `/gsd:*` 命令的薄封装，**需要先安装 GSD**。未安装时 skill 仍会加载，但移交目标命令不存在。部分 skill 另有依赖：

- `gsx-plan-review` 需要外部 Codex CLI（跨 AI 交叉评审）
- `gsx-uat-autorun`、`gsx-vrf-autorun` 需要 Playwright MCP（Web E2E）
- `gsx-discuss-phase`、`gsx-plan-phase`、`gsx-debug`、`gsx-uat-planfix` 依赖 Context7 MCP 做文档核对

## 包含的 skill（20 个）

| 阶段 | Skill | 移交目标 |
| --- | --- | --- |
| 捕获 | `gsx-add-todo`、`gsx-add-backlog` | `/gsd:capture` |
| 讨论与计划 | `gsx-discuss-phase` | `/gsd:discuss-phase`（Context7 强制门禁） |
| | `gsx-plan-phase` | `/gsd:plan-phase`（research 与 plan 拆成两次带门禁的调用） |
| | `gsx-replan-phase` | `/gsd:plan-phase N --reviews`（折回评审意见） |
| | `gsx-plan-review` | `/gsd:review --phase N --codex` |
| | `gsx-ui-spec` | `/gsd:ui-phase`（产出 UI-SPEC.md） |
| 执行 | `gsx-fast` | `/gsd:fast`（行内轻量改动） |
| | `gsx-quick` | `/gsd:quick --discuss` |
| | `gsx-debug` | `/gsd:debug --diagnose`（先定位根因再修） |
| 评审 | `gsx-code-review` | `/gsd:code-review {N} --fix --all` |
| 人工验证门 | `gsx-vrf-autorun` | 自动跑 `<how-to-verify>` 步骤 |
| | `gsx-vrf-review` | 汇总本轮前后端 / 数据库改动 |
| | `gsx-vrf-approved` | 放行 `checkpoint:human-verify` |
| UAT | `gsx-uat-phase` | `/gsd:verify-work` |
| | `gsx-uat-autorun` | 自动跑 UAT.md `## Tests` 并回写结果 |
| | `gsx-uat-newtest`、`gsx-uat-newgap` | 追加 Test / Gap 条目 |
| | `gsx-uat-planfix` | `/gsd:plan-phase N --gaps` → `/gsd:execute-phase N --gaps-only` |
| | `gsx-uat-quickfix` | 逐条快修 Gap |

各 skill 的完整触发短语与参数见对应 `SKILL.md` 的 frontmatter。

## 用法

作为斜杠命令调用：

```
/gsx:gsx-plan-phase 3
/gsx:gsx-uat-phase
```

或用自然语言触发，例如「add a todo」「run UAT」「verify this phase」。

## 与仓库 skills/ 的关系

`plugins/gsx/skills/` 下均为指向 `skills/` 的符号链接，内容单一来源。直接编辑 `skills/gsx-*/SKILL.md` 即可，plugin 侧自动生效。
