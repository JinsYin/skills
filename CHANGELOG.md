# Changelog

本文件记录项目的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added

- **write-great-skill**：新增技能，从根 `CLAUDE.md` 提炼 Skill Evals 与 Skill Workflow 的通用部分：eval 规则、按触发方分门控、起草 → 润色 → 压缩 → 验证 → 交付五步；新增省 token 方案：eval 一律交给 Sonnet（`effort: high`）subagent 执行，无 skill 基线只跑新增或改动的 eval 并以 `evals/benchmark.md` 缓存，迭代只重跑受影响的 eval，执行者看不到 expectations，评分走脚本或 Sonnet grader，第 4 步只重跑 with-skill，交付交给新的 Sonnet subagent；默认跳过 `skill-creator` 的 HTML viewer 与 description 优化循环。
- **devops-best-practices 开发环境与交付链路 playbook**：新增 `references/dev-env.md`，首个依赖随任务同时建 `docker-compose.yml` 与 `process-compose.yml`，已有项目缺任一文件时先凭证据盘点依赖与进程、给出补齐方案并询问先补还是跳过；新增 `references/delivery.md`，交付链路独立成 phase/spec，先访谈再把事实写入 `deploy/README.md`，按 `deploy/` 布局产出 Dockerfile、Drone、Kustomize 与 Helm。新增规则 `deploy-kustomize-helm-parity`（两套部署逐环境渲染一致，附 `scripts/k8s-parity.py` 只比对 key 不比对值）与 `proc-deps-via-compose-wait`（`process-compose up -D` 为唯一入口，一次性 `deps` 执行 `docker compose up --wait`）；description 扩展触发场景，并补充 evals。
- **setup-rules DevOps 约定**：新增可选约定 `devops.md`，排在 Karpathy 与 GSD 之间；首个依赖随任务建开发环境，缺开发环境时先给补齐方案并询问先补还是跳过，交付链路独立成单元，涉及开发环境或交付文件的计划在 Done 中校验 `docker compose config -q` 与 `k8s-parity.py`；按 GSD（`gsx --quick` / 新增 phase）、Matt（`/implement` quick task / 无 UI 流水线）、Superpowers（当前会话单独提交 / 修订 SPEC 后在当前里程碑追加 phase）分别路由，并补充 evals。
- **backport-prototype**：新增技能，逐页全量结构比对已上线前端与 `products/prototype/`，一次性回补前端有、原型缺的页面、字段、操作与文案；跳过数据接线、DESIGN.md 或 `progress.md` 认可的视觉差异（restyle 应用跳过全部视觉），权限守卫只记为 `fspec` 前置条件素材；原型独有内容若为待开发项则保留，否则询问是否已在代码中移除；条目以「回补已上线前端：」记入原型 CHANGELOG 的 `[Unreleased]`，多产品线加 `**<Line>**：` 前缀，最后提示 `/fspec products/prototype/`。
- **re-spec**：新增技能，依据新确认的 fspec V 文件修订需求 spec，支持 matt 本地 `.scratch/<feature>/spec.md`、GitHub Issue（经 `gh`）与 superpowers `SPEC.md`；对齐用户故事、决策与 Out of Scope，沿用 fspec 术语，界面细节只引用 `CURRENT.md` 不复制，回补条目与 Testing Decisions 不动；V 仍为 draft 时停下，无新 V 时报告已对齐；写入前先确认改动清单（用户预先授权则先写无歧义改动再提问），可在新会话运行，必要时回原 `/to-spec` 或 `/brainstorming` 会话。
- **setup-rules 约定接入 backport-prototype 与 re-spec**：Matt 规格流水线以 `/backport-prototype`、`/re-spec <spec>` 取代手工回补与修订 spec，所有步骤默认开新会话；Design 约定回补走 `backport-prototype`、新页面链路加入 `re-spec`，两者完成后提交；Superpowers 约定 UI 里程碑在 `reviewed` 与 `writing-plans` 之间走原型 → `fspec` → `re-spec` → `stitch-extract-design-md` → `design-to-code`。
- **setup-rules Matt 约定 `/implement` 收尾**：实施 `/to-tickets` 的 ticket 时，在实现提交中勾选已满足的验收项并将 Status 置为 `resolved`，未全部满足则保持原状态并说明原因；无 spec/ticket 的小改动（quick task）先提交代码，再在 `.scratch/state.md` 的 `## Quick Tasks` 表（ID `YYMMDD-xxx` | Description | Commit | Status）追加一行单独提交，参考 gsd 的 `gsd-fast`/`gsd-quick`。
- **setup-rules 规格流水线约定**：Matt 约定新增 Spec Pipeline，分正向（`/to-spec` → 原型 → `/fspec <prototype>` → 修订 spec → `stitch-extract-design-md` → `/design-to-code` → `/to-tickets <spec>`）与反向（先改前端，再择机回补原型并走 `fspec` 链）两条路径；修订 spec 回到 `/to-spec` 会话，其余步骤开新会话，以 spec 正文加评论交接。Design 约定原型 CHANGELOG 改用 Keep a Changelog，记入 `[Unreleased]`，由 `fspec` 切为同号 `[V<n>]`，多产品线条目加 `**<Line>**：` 前缀。
- **doc-writing-best-practices 参考链接规则**：新增 `struct-reference-links`，全文链接超过约 5 个或同一目标被多次引用时改用折叠式参考链接 `[文本][]`，定义集中文末、按 HTML 注释分组（本地文件在前、URL 在后），并补充 evals。
- **skillsw clean**：`./skillsw clean` 移除上游已改名/删除的 lock 条目及不在 lock 中的旧 skill，`./skillsw clean install` 清理后恢复，Core 规则改用后者。
- **github-pr-merge 按建议修改 PR**：决策新增「Apply suggestions」，选中即把评审建议推到 head 分支并 Re-review；建议已应用、无建议或 fork PR 时不显示。「Request changes」更名「Other changes」，处理建议之外的修改；选项固定按 Apply suggestions → Other changes → Merge → Reject 排列。
- **setup-rules 设计图片与品牌资源约定**：Design 约定新增设计稿存放于 `products/design/drafts/`、按 `<小写项目名>-` 前缀与 `-vN` 版本命名，Logo 定稿为 `assets/logo/logo.png`，favicon 为 64x64 的 `assets/icon/favicon.ico` 并保留原图 `favicon.png`。
- **setup-rules Core 按 zsh 语义写 Shell 命令**：glob 与以 `=` 开头的词加引号、`[` 前写 `${var}`、不以 `path` 作变量名，避免 macOS 上命令报错或检查脚本静默空跑。
- **setup-rules Superpowers 约定验 README 命令**：计划给 README 里的 shell 片段写验收时，直接跑 README 原文，不再另抄一份到计划里。
- **setup-rules Superpowers 约定：SDD 控制器按段读计划**：执行计划时控制器只按 grep 或行号读前言、全局约束和各任务的 Files / Interfaces / Done，派发前的冲突扫描交给独立 subagent，不再整份读入。

### Changed

- **根 CLAUDE.md 改为引用 write-great-skill**：移除 Skill Evals 与通用流程步骤，只保留项目级补充：eval prompt 用中文、Ship 的 rebase 推送方式、Sync（`skillsw update` 与 `/setup-rules update`，并补充 `skills/<name>/` 被替换为符号链接时的恢复方法）；提交风格沿用 `setup-rules` Core 约定。
- **gsx 改名为 gsdspec**：目录与 `name` 改为 `gsdspec`，正文、references 中的命令示例与提示同步改为 `gsdspec --<mode>`；description 保留 `gsx` 触发词；`setup-rules` 的 GSD、DevOps 约定及 README 同步新名。
- **fspec、backport-prototype 改名**：`fspec` 更名为 `write-fspec`，`backport-prototype` 更名为 `backfill-prototype`；产物仍称 fspec，`products/fspec/` 路径与 `CURRENT.md` 的 `generator: fspec` 标记不变；`re-spec`、`setup-rules` 的 Matt、Superpowers、Design 约定及 README 同步改用新名；描述保留 `fspec`、`回补原型`、`backport` 触发词；backfill-prototype 正文动词统一为 backfill，并新增跳过项：`ui-ux-best-practices` 管辖的交互约定（二次确认等）不画进原型
- **setup-rules 允许模型调用**：移除 `disable-model-invocation`，description 改为同步约定或用户要求配置规则时触发、审阅 `CLAUDE.local.md` 时不触发，使 Skill Workflow 第 7 步可由模型自动执行 `/setup-rules update`；新增自然语言触发 `update` 的 eval。
- **product-spec 更名为 fspec 并精简**：目录改为 `products/fspec/`，只保留 `/fspec [<prototype>]` 一个入口（原型默认 `products/prototype/`），移除 check、export 与设计工具方言；按上个 V 提交以来的原型 diff 起草增量 V，前端回补并入同一 V，确认后只把该 V 增量合入 `CURRENT.md`，并把原型 CHANGELOG 的 `[Unreleased]` 切为同号的 `[V<n>]`（多产品线为 `[<Line> V<n>]`）；遇旧目录 `products/specs/` 先提议 `git mv` 迁移；evals 与 fixtures 重写。
- **ideate 构想文档链接改用参考链接**：模板中的文档链接、项目地址改为 `[文本][]`，文末按 HTML 注释分组定义（调研记录在前、URL 在后）；功能调研项新增「调研记录」行，校验引用与定义一一对应，并补充 evals。
- **product-spec 文档名称统一**：产品级文档统一称为“功能规格说明书”。
- **setup-rules Changelog 约定简化**：移除逐条记录位置与条目长度要求，保留重要变更使用中文。
- **self-improve 记录 Issue 改用 `no-pr` 标签**：无 PR 的复盘记录 Issue 标签由 `no-improvement` 改为 `no-pr`；去重改按 `rejected` 标签识别被拒的 Issue/PR。
- **github-pr-merge 拒绝时打 `rejected` 标签**：Reject 关闭 PR 及其关联 Issue 前均打上 `rejected` 标签（缺失则创建）。
- **self-improve 支持多 Agent Runtime 取证**：`transcript.py` 新增 `--runtime claude|codex|cursor|agy`，可读取 Codex、Cursor IDE / `cursor-agent`、Antigravity `agy` 会话的报错、纠正、skill 加载与成本；Cursor 无 Token 记录时标注 unavailable。
- **self-improve 只复盘当前会话**：移除 `--sessions`，弱信号门槛计入历史复盘 Issue 中未过门槛的同类观察；Superpowers/GSD 约定改为每次运行后都复盘，取消里程碑联合复盘。
- **setup-rules `.worktreeinclude` 注释**：写入的条目附单行英文注释，说明为何不含 `.claude/skills/`。
- **version-release 无参数自动推断级别**：按 `[Unreleased]`（为空则按提交）推断 `minor`/`patch`，`major` 须显式指定，执行前先请用户确认。

### Fixed

- **self-improve digest 跳过 api-request-blob**：Claude Code 2.1.312 起每次请求另写一条无 usage 的 `api-request-blob` 副本，digest 不再把它计为第二次调用，消除误报的 `[retry]`、重复的 SKILL/AGENT 行与翻倍的 `calls`；fixtures 同步模拟该记录并补充 eval 断言。
- **self-improve digest 不再把后台任务通知计为用户提问**：Claude Code 的 `<task-notification>` 不再另起一轮，同一 skill 的开销不再被拆走，HEAVY-SKILL 判定恢复准确。
- **self-improve 轮次耗时**：digest 的 wall 不再把两轮之间等待用户的空闲算进上一轮，`HEAVY-SKILL` 按耗时判定恢复可信。
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
