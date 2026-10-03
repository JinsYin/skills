# Changelog

本文件记录项目的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added

- **skillsw clean**：`./skillsw clean` 移除上游已改名/删除的 lock 条目及不在 lock 中的旧 skill，`./skillsw clean install` 清理后恢复，Core 规则改用后者。
- **github-pr-merge 按建议修改 PR**：决策新增「Apply suggestions」，选中即把评审建议推到 head 分支并 Re-review；建议已应用、无建议或 fork PR 时不显示。「Request changes」更名「Other changes」，处理建议之外的修改；选项固定按 Apply suggestions → Other changes → Merge → Reject 排列。

### Changed

- **self-improve 记录 Issue 改用 `no-pr` 标签**：无 PR 的复盘记录 Issue 标签由 `no-improvement` 改为 `no-pr`；去重改按 `rejected` 标签识别被拒的 Issue/PR。
- **self-improve 支持多 Agent Runtime 取证**：`transcript.py` 新增 `--runtime claude|codex|cursor|agy`，可读取 Codex、Cursor IDE / `cursor-agent`、Antigravity `agy` 会话的报错、纠正、skill 加载与成本；Cursor 无 Token 记录时标注 unavailable。
- **self-improve 只复盘当前会话**：移除 `--sessions`，弱信号门槛计入历史复盘 Issue 中未过门槛的同类观察；Superpowers/GSD 约定改为每次运行后都复盘，取消里程碑联合复盘。
- **setup-rules `.worktreeinclude` 注释**：写入的条目附单行英文注释，说明为何不含 `.claude/skills/`。
- **version-release 无参数自动推断级别**：按 `[Unreleased]`（为空则按提交）推断 `minor`/`patch`，`major` 须显式指定，执行前先请用户确认。

### Fixed

- **version-release 发布范围**：按构建关系统一发布成员版本，保留图外冻结原型、fixture 和 vendored 项目。

## [v0.10.0] - 2026-10-02

### Added

- **skillsw 包装脚本**：setup-rules 单独询问安装 `skillsw`，`./skillsw install [--agent …]` 按 `skills-lock.json` 恢复 skills，其余命令透传 `npx skills`。
- **github-pr-merge**：交互式评审 open PR，发布评审 comment，按用户选择 squash 合并或打回。
- **self-improve**：复盘会话提炼经验，经 Issue + PR 改进相关 skill。
- **version-release**：统一升级各模块版本，收起 `[Unreleased]` 并打 tag。
- **design-to-code restyle 模式**：原型只提供结构，按新风格重写 DESIGN.md 后还原。
- **design-to-code 视觉校验**：新增 `full`/`lite` 档位与 Verify 步骤，附 `visual-check.mjs` 截图比对。
- **design-to-code 可接线产出**：页面经 `src/api/` 取数、可用 mock 替身，并提供视觉冻结检查。
- **前端分流约定**：`setup-rules` 明确 design-to-code 之后的改动路径，plan 须通过视觉冻结检查。

### Changed

- **setup-rules Git tracking 默认忽略 skills**：只保留默认（忽略各 agent 目录的 `skills/` 子目录）与自定义，去掉全部跟踪、全部忽略。
- **已安装 skills 不再入库**：`.agents/skills/`、`.claude/skills/` 改为忽略，`npx skills add jinsyin/skills` 只列出本仓库自己的 skills；新 worktree 经 `.worktreeinclude` 复制。
- **setup-rules 排除 skills 时保留 lock**：Git tracking 忽略已安装 skills 时保留并暂存 `skills-lock.json`，配置 worktree 复制，Core 约定新增按 lock 恢复 skills 的命令。
- **self-improve 克隆内恢复流程 skills**：执行上游流程前先在克隆中 `./skillsw install`，不再依赖入库的安装副本。
- **self-improve 无改进也留档**：复盘无可改进项时仍提一个 `no-improvement` 记录 Issue（不提 PR）并立即附理由关闭。
- **github-pr-merge 评审 effort**：Reviewer 行的 effort 从 Claude Code 的 `$CLAUDE_EFFORT` 读取，不再写成 `unknown`。
- **self-improve 从克隆执行贡献流程**：上游 `CLAUDE.md` 点名的 skill 从克隆的 `.claude/skills/` 读取执行，不再因发起项目看不到而跳过。
- **self-improve 跟随上游自身规则**：安装副本与上游不一致时，后续步骤改按上游 `SKILL.md` 执行，避免旧副本漏掉 Issue 语言等规则。
- **github-pr-merge 评审记录**：Review/Re-review comment 标注 `Reviewer: <model>/<effort>`，并向用户简报核心问题与建议（Re-review 为结论）及 comment 完整链接。
- **self-improve 单次调用开销**：digest 为每次 skill 调用输出 Token、调用数、压缩次数、峰值上下文与子 Agent 数，开销类 Issue 按调用列表作证据。
- **superpowers 约定**：写计划时只定向读取路线图、规格章节、上游接口与相关代码，每份计划分派独立 subagent 起草，避免上下文溢出。
- **doc-to-md 补齐 eval fixtures 并校正精修范围**：新增全部评测样例文件，Office/EPUB 源按无法渲染处理，evals 改为斜杠命令触发。
- **doc-to-md 改写为英文**：SKILL.md 全文译为英文并精简重复说明，改为手动调用；行为不变。
- **ideate 改为手动调用并精简指令**：统一缺失值写法（`> 无` / `待定：`），规则单点定义，校验项可逐条核对。
- **self-improve Issue/PR 正文改用中文**：模板标题、字段键、表头、`model/effort` 与 Signal 保持英文；`--dry-run` 输出完整 Issue 正文；补齐 evals 与会话 fixtures。
- **已安装 Agent skills 纳入版本管理**：保存 skills、Claude 入口与安装锁文件，排除 Antigravity 安装入口。
- **setup-rules update 自动执行**：不再逐项确认，直接刷新已安装项，保留未识别段落，异常目标跳过并在报告中列出；补齐 evals。
- **github-pr-merge**：明确 fork PR 冲突与打回的处理、推送后刷新 merge SHA 校验，无 PR 时也执行收尾同步，并补齐 evals。
- **github-pr-merge 收尾同步本地**：处理完所有 PR 后，本地无新提交则 `pull --ff-only`，有新提交则 rebase 到远端默认分支后自动 push。
- **Codex sol Agent 模型配置**：`setup-rules` 的 `superpowers-fixer` 与 `superpowers-final-reviewer` 切换至 `gpt-6.1-sol`，保持 reasoning effort。
- **design-to-code 文案压缩**：精简 SKILL.md 正文、description 与 `design-md-mapping.md`，减少每次加载的 Token。
- **commit message 优先 caveman-commit**：`setup-rules` Core 约定提交信息在已安装时遵循 `caveman-commit` 规则，描述始终用中文。
- **github-pr-merge 文案压缩**：精简 SKILL.md 正文与 description，减少每次加载的 Token。
- **version-release 文案压缩**：精简 SKILL.md 正文与 description，减少每次加载的 Token。
- **version-release 完成标准更明确**：changelog 须覆盖自上个 tag 起所有面向用户的提交，无关的未提交改动原样保留并询问。
- **self-improve 完成标准更明确**：`--dry-run` 也会复盘自身并写入报告，各步补齐完成标准，description 更精简。
- **self-improve 文案压缩**：精简 SKILL.md 正文与 description，减少每次加载的 Token。
- **self-improve 重试信号去误报**：`digest` 的重复计数带上 Edit 内容与 Read 偏移，同一文件的多处修改不再被标为重试。
- **self-improve 复盘重度第三方 skill**：手动触发且 Token 或耗时占比 ≥25% 的第三方 skill，改进建议写入 `setup-rules` 约定并提 PR；修复无参数斜杠命令未被识别。
- **self-improve 区分常用与当前档位**：`transcript.py meta` 按 `model/effort` 成对统计，分别输出用得最多的 `most` 与最后一次的 `last`，改进运行取 `last`；Issue 模板 Context 同步。
- **design-to-code 结构以原型渲染为准**：隐藏区块不移植；`CURRENT.md` 与原型冲突时以原型和 DESIGN.md 为准，差异走 `product-spec add`。
- **CHANGELOG 条目精简**：`setup-rules` Core 约定要求每条单行，只写变更及其影响，省略实现细节。
- **self-improve 成本复盘**：分析 Token 与耗时热点以缩短流程，Issue/PR 按 skill 打标签。
- **self-improve 来源记录**：Issue 记录来源项目、Agent Runtime、会话与 model/effort。
- **setup-rules 接入 self-improve**：GSD 与 Superpowers 流程出现纠正或返工后显式调用。
- **Design 约定接入 self-improve**：`design-to-code` 完成并提交后调用 `self-improve`；Design 约定按三级标题归类。
- **Agent 模型配置**：Codex 切至 `gpt-5.6`，Cursor 切至 `grok-4.6`，Claude 子 Agent 改为 `sonnet/xhigh`。
- **setup-rules 接入 version-release**：CHANGELOG 规则移入 Core，发版统一走 `version-release`。
- **Spring Boot gauss 系 Flyway**：新增规则绕过 gauss 系拒绝的 `SET ROLE`。
- **技能重命名**：`product-spec-generate` 改回 `product-spec`。
- **前端基线扩容**：新增脚手架与样式文件拆分规则，图标选用 lucide-react。
- **design-to-code 事实来源**：明确技术栈、DESIGN.md、原型与交互规范各自的权威来源。
- **design-to-code 英文化**：正文改为英文，精简 description。

### Fixed

- **design-to-code、version-release 可被 skills CLI 识别**：修正 `description` 的 YAML 写法，`npx skills add jinsyin/skills` 不再跳过这两个 skill。
- **Claude 文件跟踪补齐**：移除 Claude 目录忽略规则，纳入 setup-rules update 的 Claude eval fixtures。
- **self-improve 发 PR 与同步更稳**：显式取默认分支、push 失败不再被吞、`gh pr create` 带 `--head`，同步改从本地 PR 分支取文件；不再默认派生子 Agent。

## [v0.9.0] - 2026-09-19

### Added

- **后台管理 UI/UX 规范**：新增 `ui-ux-best-practices` 技能，覆盖控制台布局密度、表格、筛选、分页、表单、弹层和敏感配置展示等规则。
- **Agent 适配与敏感文件保护**：`setup-rules` 补充多平台 Agent 资源适配、交互式安装流程和敏感文件访问限制。

### Changed

- **技能重命名**：将 `to-raw-requirements` 重命名为 `ideate`，将 `product-spec` 重命名为 `product-spec-generate`，并同步更新产物路径、目录和仓库文档引用。
- **文档转换技能重命名**：将 `to-md` 重命名为 `doc-to-md`，同步更新技能定义、评测元数据和脚本标识。
- **规则库整理**：整合前端与后台 UI/UX 规则，移除重复内容，精炼技能描述和规则编译脚本。
- **setup-rules Git 跟踪提示**：补充 Antigravity `.agent` 目录的提交选择说明。
- **BREAKING**：旧技能名 `to-raw-requirements`、`product-spec`、`to-md` 需分别迁移到 `ideate`、`product-spec-generate`、`doc-to-md`。

### Fixed

- **规则资源一致性**：修正重命名后的路径、入口和规则引用，避免技能清单与实际目录不一致。

## [v0.8.0] - 2026-09-07

### Changed

- **技能重命名**：将原 `rule-setup` 技能重命名为 `setup-rules`，同步更新技能清单、文档与定义。
- **规范与流程优化**：强化中文注释要求，规范 Superpowers 执行阶段闭环流程；将约定片段统一收拢至 `conventions/` 目录并精炼 Core 规范。

### Removed

- **移除 Claude Code Plugin 打包**：移除 `plugins/gsx` 与 `plugins/sdd` 打包目录及 `.claude-plugin/marketplace.json` 清单，简化为纯 Skills 资源库。

## [v0.7.0] - 2026-09-02

### Added

- **Superpowers 多平台子代理预设**：新增支持 Claude、Codex、Cursor 三个平台的 Superpowers 专属子代理配置资产（`superpowers-implementer`、`superpowers-task-reviewer`、`superpowers-re-reviewer`、`superpowers-fixer`、`superpowers-final-reviewer`）。
- **Cursor 通用子代理与模型策略**：新增 Cursor 通用 Agent（`general-purpose`）配置预设，以及 Cursor 子代理模型强制策略与 Hook（`enforce-subagent-model.sh`、`subagent-model-policy.mdc`）。
- **Matt 约定片段**：新增 Matt Pocock 技能风格的工作流约定片段（`matt.md`）。

### Changed

- **`rule-setup` 结构重构与约定精炼**：重构工作流片段组织结构（统一归入 `workflows/` 目录），精炼 Core 核心约定，优化 Worktree 分支收尾流程及路径引用规范。
- **版本统一升级**：`gsx`、`sdd` plugin 与 marketplace 版本统一升级至 `0.7.0`。

### Removed

- **移除 `spec-setup` 与 `spec-triage` skill**：清理两个废弃 skill 及其在 `sdd` plugin 和文档中的对应入口。

## [v0.6.0] - 2026-08-27

### Changed

- **`rule-setup` 技能重命名**：将原 `claude-local` 技能重命名为 `rule-setup`，同步更新 `sdd` plugin 的入口、符号链接和文档引用；功能与产物路径保持不变。
- **版本统一升级**：`gsx`、`sdd` plugin 与 marketplace 版本统一升级至 `0.6.0`。

## [v0.5.0] - 2026-08-24

### Added

- **`claude-local` 约定安装 Skill**：安装组装式的 Agent 约定规范至项目的 `CLAUDE.local.md` 及 `AGENTS.md` 入口文件，提供 Core（中文回复、安全防护、Git 垂直特性提交规范）、GSD 工作流偏好与 Superpowers 工作流规范，支持交互式选择与非破坏性合并。

### Changed

- **SDD 工具包更新**：`sdd` plugin 现包含 `claude-local` 技能，进一步完善规范驱动开发全流程工具链。
- **`.gitignore` 规则整理**：分类补充 Agent 运行目录、本地配置、系统与编辑器缓存等忽略规则。
- **仓库约定入口**：初始化 `AGENTS.md` 与 `CLAUDE.md`，并接入 `CLAUDE.local.md`。

## [v0.4.0] - 2026-08-20

### Added

- **`stack-module-readme` 模块说明规范**：Spring Boot 后端规范与前端 UI 规范新增模块 README 要求，定义项目根目录与子模块/子包的说明文档标准结构。
- **`stack-auth-framework` 鉴权框架选型规范**：新增 Spring Security 与 Sa-Token 按项目规模二选一评估规则（基础设施/认证中心/中大型系统选 Spring Security，后台管理/单体/中小项目选 Sa-Token）。

### Changed

- **声明式鉴权规范重构**：`layer-controller-auth-annotations` 改为框架无关模式，补充两套框架对照表、显式放行规则及静默失效陷阱说明。
- **GSX Thin Front-Door 与规范脚手架联动**：更新 `gsx-discuss-phase`、`gsx-plan-phase`、`gsx-debug`、`gsx-uat-planfix`、`gsx-vrf-review` 与 `spec-setup/guards.md` 中对应的鉴权框架校验规则。

## [v0.3.0] - 2026-08-13

### Added

- **`to-raw-requirements` 原始需求整理 Skill**：将口述、聊天记录与上下文方案映射为固定四段结构，逐项确认缺失、歧义和冲突后保存到 `docs/requirements/raw.md`。

### Changed

- **SDD 链路前移**：`sdd` plugin 现覆盖「原始需求 → 工程规范 → 产品功能规范 → 设计 → 代码」，版本升级至 0.3.0。

## [v0.2.0] - 2026-08-13

### Added

- **`spec-setup` 规范脚手架 Skill**：支持从零访谈确定新项目架构形态（支持一仓多形态），从既有 `*-best-practices` 继承栈与规范，固化已裁决规则并显式留白，与 `spec-triage` 彻底解耦。

### Changed

- **Spring Boot 最佳实践演进**：沉淀多形态部署迁移分层规则，修正 overlay 分叉判据并补充迁移不可变规则。
- **SDD 与 GSD 工作流解耦**：解耦 SDD 规则集及 `spec-triage` 对 GSD 工作流的强绑定，通用化高频文档与产物路径判定。
- **Marketplace 清简**：移除全量合集 `jinsyin-skills` plugin，只保留 `gsx` 与 `sdd` 两个独立 plugin，marketplace 名称统一简化为 `jinsyin`。

### Fixed

- 移除 Skill 规则文档中的硬编码本地路径。

## [v0.1.0] - 2026-08-11

### Added

- **Claude Code Marketplace & Plugins**：初始化 `jinsyin` marketplace 清单，提供 `gsx` 与 `sdd` 插件包。
- **SDD 最佳实践规则集**：`frontend-ui-best-practices`、`spring-boot-best-practices`、`devops-best-practices`、`doc-writing-best-practices`。
- **spec-triage**：规范分诊与漂移检测。
- **product-spec**：产品功能规范管理。
- **design-to-code**：高保真原型/设计稿还原为生产级代码。
- **GSX Thin Front-Door (20 个 skills)**：包含 `gsx-*` 全套技能，包裹 GSD 命令并接入 Context7 文档核对校验门禁。
- **通用工具**：`doc-to-md` Markdown 内容转换技能。

[Unreleased]: https://github.com/JinsYin/skills/compare/v0.10.0...HEAD
[v0.10.0]: https://github.com/JinsYin/skills/compare/v0.9.0...v0.10.0
[v0.9.0]: https://github.com/JinsYin/skills/compare/v0.8.0...v0.9.0
[v0.8.0]: https://github.com/JinsYin/skills/compare/v0.7.0...v0.8.0
[v0.7.0]: https://github.com/JinsYin/skills/compare/v0.6.0...v0.7.0
[v0.6.0]: https://github.com/JinsYin/skills/compare/v0.5.0...v0.6.0
[v0.5.0]: https://github.com/JinsYin/skills/compare/v0.4.0...v0.5.0
[v0.4.0]: https://github.com/JinsYin/skills/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/JinsYin/skills/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/JinsYin/skills/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/JinsYin/skills/releases/tag/v0.1.0
