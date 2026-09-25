# Changelog

本文件记录项目的所有重要变更。
遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范与 [Semantic Versioning](https://semver.org/lang/zh-CN/) 版本号约定。

## [Unreleased]

### 新增 (Added)

- **design-to-code restyle 模式**：与 `full`、`lite` 三选一，原型只提供结构（区块、相对布局、交互流程、浮层类型、文案、状态）。Step 1 新增 Branch C：按风格描述（没写时根据产品定位自定）编写新的 DESIGN.md，经一次确认后替换 `products/design/DESIGN.md`，再走 Branch A 翻译。Step 4 用 `visual-check.mjs diff --structure` 做按顺序的文案比对和并排截图，只修结构缺漏。`progress.md` 记录所用模式，回入时沿用。`setup-rules` 的 Design 约定补充：restyle 应用的 DESIGN.md 不再从原型重新抽取。
- **design-to-code 视觉校验档位**：新增 `full`（默认）与 `lite` 两个参数，新增 Step 4 Verify，交付顺延为 Step 5。保真度改为以 token 取值精确为准；Step 4 之前两档都不渲染、不测量原型；DESIGN.md 能解释的差异直接记为合法偏差。新增 `scripts/visual-check.mjs`：`smoke` 检查类名是否生成了 CSS、控制台报错和横向溢出，`diff` 与原型成对截图并输出差异报告，最多两轮。Step 2 先确定跨页公共组件，并产出原型索引、进度账本和校验目标清单；上下文压缩后读这两份文件，不再重读原型。Step 1 的原型比对改为静态 grep，移植期间禁止重抽 DESIGN.md 或修改原型。
- **design-to-code 可接线产出**：新增 Data seam 规则——页面只经 `src/api/` 取数，后端就绪前转发同签名的 `src/mocks/` 替身，`grep -rn '@/mocks' src/api` 即 mock 台账；原型未画的状态与前置条件以 product-spec 的 `CURRENT.md` 为准；新增原型变更后的回入规则，只重写视觉层，保留已接线的 `src/api/` 与 `src/hooks/`；Step 4 交付视觉冻结检查 `scripts/visual-freeze.sh`，供后续 plan 证明未改 token、class、布局与文案。
- **前端分流与 plan 视觉边界约定**：`setup-rules` 的 Design 约定新增 design-to-code 之后的分流——新功能先 `product-spec add`；新页面或 DESIGN.md 缺失的样式走原型 → DESIGN.md → design-to-code，其余直接改代码，走全链路前一次性按已落地前端回写原型；plan 只换数据实现、接线、加守卫，须通过视觉冻结检查；mock 可作为交付态。Superpowers 约定把该边界写进 SPEC、ROADMAP 与 plan 的 Global Constraints，ROADMAP `deliverables` 标注 `mock`/`live`，前端 task 的 Done 必跑冻结检查。

### 变更与重构 (Changed & Refactored)

- **Spring Boot 迁移规则补充 gauss 系 Flyway 插件**：`spring-boot-best-practices` 新增 `db-opengauss-flyway-set-role`。gauss 系会拒绝 Flyway 在收尾时执行的 `SET ROLE`，因此需要通过 Plugin SPI 注册 DatabaseType、Database、Connection 三个类，把角色还原步骤置空。规则数由 46 增至 47。
- **技能重命名**：将 `product-spec-generate` 重命名为 `product-spec`，并同步更新技能目录、元数据、安装示例与规范模板引用。
- **前端基线扩容**：`frontend-ui-best-practices` 新增 `stack-scaffold`（脚手架命令与四项必须一开始就配对的设置）与 `stack-style-files`（`src/styles/` 下样式与 token 文件拆分）两条规则，`stack-baseline` 补充 lucide-react 图标选型，规则数由 2 增至 4。
- **design-to-code 接入外部事实来源**：新增 Authority 章节明确四个事实来源——技术栈、脚手架与样式组织以 `frontend-ui-best-practices` 为准，设计系统以 `products/design/DESIGN.md` 为准，页面结构与交互以 `products/prototype/` 为准，界面交互细则以 `ui-ux-best-practices` 为准。Step 1 拆成「有 DESIGN.md 翻译」与「无 DESIGN.md 反推」双分支，补充 `references/design-md-mapping.md` 记录角色色板到组件库 token 的逐项映射（含首选/次选链、正文核对要求、自定义 token 追加规则）与 hex→HSL 转换；目录结构改为体现 monorepo 下 `src/` 的包路径层级。
- **design-to-code 改写为英文**：技能正文与参考文件统一英文，并精简 description（该技能仅用户手动触发，原有的触发词清单为冗余）。

## [v0.9.0] - 2026-09-19

### 新增 (Added)

- **后台管理 UI/UX 规范**：新增 `ui-ux-best-practices` 技能，覆盖控制台布局密度、表格、筛选、分页、表单、弹层和敏感配置展示等规则。
- **Agent 适配与敏感文件保护**：`setup-rules` 补充多平台 Agent 资源适配、交互式安装流程和敏感文件访问限制。

### 变更与重构 (Changed & Refactored)

- **技能重命名**：将 `to-raw-requirements` 重命名为 `ideate`，将 `product-spec` 重命名为 `product-spec-generate`，并同步更新产物路径、目录和仓库文档引用。
- **文档转换技能重命名**：将 `to-md` 重命名为 `doc-to-md`，同步更新技能定义、评测元数据和脚本标识。
- **规则库整理**：整合前端与后台 UI/UX 规则，移除重复内容，精炼技能描述和规则编译脚本。
- **setup-rules Git 跟踪提示**：补充 Antigravity `.agent` 目录的提交选择说明。

### 修复 (Fixed)

- **规则资源一致性**：修正重命名后的路径、入口和规则引用，避免技能清单与实际目录不一致。

### 破坏性变更 (Breaking Changes)

- 使用旧技能名 `to-raw-requirements`、`product-spec` 或 `to-md` 的调用方需要分别迁移到 `ideate`、`product-spec-generate` 和 `doc-to-md`。

## [v0.8.0] - 2026-09-07

### 变更与重构 (Changed & Refactored)

- **技能重命名**：将原 `rule-setup` 技能重命名为 `setup-rules`，同步更新技能清单、文档与定义。
- **规范与流程优化**：强化中文注释要求，规范 Superpowers 执行阶段闭环流程；将约定片段统一收拢至 `conventions/` 目录并精炼 Core 规范。

### 移除 (Removed)

- **移除 Claude Code Plugin 打包**：移除 `plugins/gsx` 与 `plugins/sdd` 打包目录及 `.claude-plugin/marketplace.json` 清单，简化为纯 Skills 资源库。

---

## [v0.7.0] - 2026-09-02

### 新增 (Added)

- **Superpowers 多平台子代理预设**：新增支持 Claude、Codex、Cursor 三个平台的 Superpowers 专属子代理配置资产（`superpowers-implementer`、`superpowers-task-reviewer`、`superpowers-re-reviewer`、`superpowers-fixer`、`superpowers-final-reviewer`）。
- **Cursor 通用子代理与模型策略**：新增 Cursor 通用 Agent（`general-purpose`）配置预设，以及 Cursor 子代理模型强制策略与 Hook（`enforce-subagent-model.sh`、`subagent-model-policy.mdc`）。
- **Matt 约定片段**：新增 Matt Pocock 技能风格的工作流约定片段（`matt.md`）。

### 变更与优化 (Changed & Improved)

- **`rule-setup` 结构重构与约定精炼**：重构工作流片段组织结构（统一归入 `workflows/` 目录），精炼 Core 核心约定，优化 Worktree 分支收尾流程及路径引用规范。
- **版本统一升级**：`gsx`、`sdd` plugin 与 marketplace 版本统一升级至 `0.7.0`。

### 移除 (Removed)

- **移除 `spec-setup` 与 `spec-triage` skill**：清理两个废弃 skill 及其在 `sdd` plugin 和文档中的对应入口。

---

## [v0.6.0] - 2026-08-27

### 变更与重构 (Changed & Refactored)

- **`rule-setup` 技能重命名**：将原 `claude-local` 技能重命名为 `rule-setup`，同步更新 `sdd` plugin 的入口、符号链接和文档引用；功能与产物路径保持不变。
- **版本统一升级**：`gsx`、`sdd` plugin 与 marketplace 版本统一升级至 `0.6.0`。

---

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

- **`to-raw-requirements` 原始需求整理 Skill**：将口述、聊天记录与上下文方案映射为固定四段结构，逐项确认缺失、歧义和冲突后保存到 `docs/requirements/raw.md`。

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
- **通用工具**：`doc-to-md` Markdown 内容转换技能。
