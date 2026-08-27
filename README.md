# Agent Skills

自定义 Agent 配置与技能（Skills）集合。

## 安装与使用

### 方式一：作为 skills 库

```bash
npx skills@latest add jinsyin/skills
```

### 方式二：作为 Claude Code plugin

在 Claude Code 中添加本仓库为 marketplace，再选择安装粒度：

```
/plugin marketplace add jinsyin/skills

/plugin install gsx@jinsyin
/plugin install sdd@jinsyin
```

本地调试：

```bash
# 全量
claude --plugin-dir .

# 单个
claude --plugin-dir plugins/gsx --plugin-dir plugins/sdd
```

## 包含 Plugin

| Plugin | 内容 | 说明 |
| --- | --- | --- |
| [`gsx`](plugins/gsx/) | 20 个 `gsx-*` skill | GSD 工作流薄前门，覆盖计划、执行、评审、UAT 全流程 |
| [`sdd`](plugins/sdd/) | `rule-setup` + `to-requirements` + 4 套 `*-best-practices` + `spec-setup` + `spec-triage` + `product-spec` + `design-to-code` | 规范驱动开发：原始需求 → 立规范 → 定产品功能 → 出设计 → 产出代码 |

`gsx` / `sdd` 通过符号链接复用 `skills/` 下的原始目录，因此**内容单一来源**：编辑 `skills/<name>/SKILL.md` 即可，两个 plugin 全部自动生效。

## 包含技能

- `frontend-ui-best-practices` - 前端 UI 开发最佳实践
- `devops-best-practices` - DevOps 运维最佳实践
- `doc-writing-best-practices` - 文档编写最佳实践
- `spring-boot-best-practices` - Spring Boot 后端开发最佳实践
- `rule-setup` - 安装组装式的 Agent 约定规范至项目的 `CLAUDE.local.md` 及 `AGENTS.md` 入口文件
- `to-requirements` - 将口述原始需求与上下文方案逐项澄清，按固定结构整理并保存为 `REQUIREMENTS.md`
- `spec-setup` - **新项目**从零建规范：访谈定形态（支持一仓多形态）→ 从既有 `*-best-practices` 继承栈与规范、缺口走推荐、Context7 定版 → 只固化已裁决的，其余显式留白并记录复查触发点
- `spec-triage` - **存量项目**整顿规范：勘察取证 → 按加载成本分诊到 CLAUDE.md / skill / .claude/rules / 项目文档四层 → 检测规范与代码的漂移
- `to-md` - 内容转换 Markdown 工具
- `product-spec` - 管理产品功能规范（功能、交互、Flyway 式版本化变更记录），合成的 `CURRENT.md` 直接喂 Claude Design / v0 / Figma Make / Lovable
- `design-to-code` - 将高保真设计/原型（HTML + React JSX）还原为 Vite + React + TypeScript + Tailwind + shadcn/ui 生产级代码
- `gsx-*`（20 个）- GSD 工作流的薄前门 skill，包裹 `/gsd:*` 命令并附加项目专属校验（Context7 文档核对、讨论前置等），覆盖计划、执行、评审、UAT 全流程

## 项目目录

- `skills/` - 自定义技能资源库（唯一事实来源）
- `plugins/` - Claude Code plugin 打包（`gsx`、`sdd`），内含指向 `skills/` 的符号链接
- `.claude-plugin/marketplace.json` - marketplace 清单
- `CHANGELOG.md` - 版本变更日志
- `LICENSE` - MIT 开源协议

## 开源协议

本项目采用 [MIT License](LICENSE) 协议开源。

