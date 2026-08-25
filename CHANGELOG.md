# Changelog

本文件记录项目的所有重要变更。
遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范与 [Semantic Versioning](https://semver.org/lang/zh-CN/) 版本号约定。

## [v0.5.0] - 2026-08-24

### 新增 (Added)

- **`claude-local` 约定安装 Skill**：安装组装式的 Agent 约定规范至项目的 `CLAUDE.local.md` 及 `AGENTS.md` 入口文件，提供 Core（中文回复、安全防护、Git 垂直特性提交规范）、GSD 工作流偏好与 Superpowers 工作流规范，支持交互式选择与非破坏性合并。

### 变更与优化 (Changed & Improved)

- **SDD 工具包更新**：`sdd` plugin 现包含 `claude-local` 技能，进一步完善规范驱动开发全流程工具链。
- **工程与配置优化**：
  - 全面补充并分类整理 `.gitignore` 规则（Agent 运行目录、本地配置、系统与编辑器缓存等）。
  - 本仓库初始化 `AGENTS.md` 与 `CLAUDE.md` 规范入口，并接入 `CLAUDE.local.md`。

---

## [v0.4.0] - 2026-08-20

### 新增 (Added)

- **`stack-module-readme` 模块说明规范**：Spring Boot 后端规范与前端 UI 规范新增模块 README 要求，定义项目根目录与子模块/子包的说明文档标准结构。
- **`stack-auth-framework` 鉴权框架选型规范**：新增 Spring Security 与 Sa-Token 按项目规模二选一评估规则（基础设施/认证中心/中大型系统选 Spring Security，后台管理/单体/中小项目选 Sa-Token）。

### 变更与重构 (Changed & Refactored)

- **声明式鉴权规范重构**：`layer-controller-auth-annotations` 改为框架无关模式，补充两套框架对照表、显式放行规则及静默失效陷阱说明。
- **GSX Thin Front-Door 与规范脚手架联动**：更新 `gsx-discuss-phase`、`gsx-plan-phase`、`gsx-debug`、`gsx-uat-planfix`、`gsx-vrf-review` 与 `spec-setup/guards.md` 中对应的鉴权框架校验规则。

---

## [v0.3.0] - 2026-08-13

### 新增 (Added)

- **`to-requirements` 原始需求整理 Skill**：将口述、聊天记录与上下文方案映射为固定四段结构，逐项确认缺失、歧义和冲突后保存项目根目录的 `REQUIREMENTS.md`。

### 变更 (Changed)

- **SDD 链路前移**：`sdd` plugin 现覆盖「原始需求 → 工程规范 → 产品功能规范 → 设计 → 代码」，版本升级至 0.3.0。

---

## [v0.2.0] - 2026-08-13

### 新增 (Added)
- **`spec-setup` 规范脚手架 Skill**：支持从零访谈确定新项目架构形态（支持一仓多形态），从既有 `*-best-practices` 继承栈与规范，固化已裁决规则并显式留白，与 `spec-triage` 彻底解耦。

### 变更与重构 (Changed & Refactored)
- **Spring Boot 最佳实践演进**：沉淀多形态部署迁移分层规则，修正 overlay 分叉判据并补充迁移不可变规则。
- **SDD 与 GSD 工作流解耦**：解耦 SDD 规则集及 `spec-triage` 对 GSD 工作流的强绑定，通用化高频文档与产物路径判定。
- **Marketplace 清简**：移除全量合集 `jinsyin-skills` plugin，只保留 `gsx` 与 `sdd` 两个独立 plugin，marketplace 名称统一简化为 `jinsyin`。

### 修复 (Fixed)
- 移除 Skill 规则文档中的硬编码本地路径。

---

## [v0.1.0] - 2026-08-11

### 新增 (Added)
- **Claude Code Marketplace & Plugins**：初始化 `jinsyin` marketplace 清单，提供 `gsx` 与 `sdd` 插件包。
- **SDD 规范驱动开发工具包**：
  - 4 套最佳实践规则集（`frontend-ui-best-practices`、`spring-boot-best-practices`、`devops-best-practices`、`doc-writing-best-practices`）
  - `spec-triage` 规范分诊与漂移检测
  - `product-spec` 产品功能规范管理
  - `design-to-code` 高保真原型/设计稿一键还原生产级代码
- **GSX Thin Front-Door (20 个 skills)**：包含 `gsx-*` 全套技能，包裹 GSD 命令并接入 Context7 文档核对校验门禁。
- **通用工具**：`to-md` Markdown 内容转换技能。
