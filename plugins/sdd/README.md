# sdd

规范驱动开发（Spec-Driven Development）工具包：把「口述原始需求 → 建立工程规范 → 管理产品功能 → 设计 → 代码」这条链路上的 skill 打包在一起，并提供四套领域最佳实践规则集。

## 安装

```bash
# 在 Claude Code 中
/plugin marketplace add jinsyin/skills
/plugin install sdd@jinsyin
```

本地开发：

```bash
claude --plugin-dir plugins/sdd
```

## 包含的 skill（9 个）

| Skill | 作用 | 触发方式 |
| --- | --- | --- |
| `to-requirements` | 将口述、聊天记录或上下文方案逐项澄清，按固定四段结构整理并保存为项目根目录的 `REQUIREMENTS.md` | 自动 + `/sdd:to-requirements` |
| `spec-setup` | 为新项目访谈确定形态与技术栈，只固化已裁决的规范，并显式记录留白与复查触发点 | 自动 + `/sdd:spec-setup` |
| `spec-triage` | 勘察代码库取证 → 只就推断不了的事访谈 → 把约定按加载成本分诊到 CLAUDE.md / skill / .claude-rules / 项目文档四层，并检测规范与代码的漂移 | 自动 + `/sdd:spec-triage` |
| `frontend-ui-best-practices` | 前端 UI 规则集：表单、列表、弹层、格式化、一致性 | 自动 |
| `devops-best-practices` | 容器化与部署规则集（26 条 / 6 类）：Dockerfile、K8s、compose、CI、凭据 | 自动 |
| `doc-writing-best-practices` | 文档规则集：中英混排、标点、结构、示例可复制 | 自动 |
| `spring-boot-best-practices` | Spring Boot 后端规则集：分层、命名、DTO、响应封装、加密、数据库 | 自动 |
| `product-spec` | 管理产品功能规范：功能、交互、Flyway 式版本化变更记录。V 链管演进，合成的 `CURRENT.md` 喂 AI 设计工具 | 自动 + `/sdd:product-spec` |
| `design-to-code` | 把高保真设计 / 原型（HTML + React JSX）还原为 Vite + React + TypeScript + Tailwind + shadcn/ui 生产级代码 | 仅手动 `/sdd:design-to-code` |

> `design-to-code` 的 frontmatter 设了 `disable-model-invocation: true`，因此不会被模型自动触发，只能由用户显式调用。

## 规则集的用法

四个 `*-best-practices` 是**索引式**的：`SKILL.md` 只含规则索引，Claude 按当前任务定位相关条目后再按需 `Read` 对应的 `rules/*.md`，避免一次性吃掉整套规范。

## 三条典型链路

**原始需求**：

1. `/sdd:to-requirements` —— 输入口述需求与上下文方案
2. skill 逐项追问缺失、含糊或冲突的信息
3. 确认完整后写入项目根目录的 `REQUIREMENTS.md`

**代码规范**：

1. `/sdd:spec-triage` —— 为项目建立或整顿分层规范
2. 日常开发中，四套 `*-best-practices` 按文件类型自动介入
3. `/sdd:spec-triage --check` —— 定期检测规范与代码库的漂移

**产品 → 设计 → 代码**：

1. `/sdd:product-spec init` —— 建产品功能规范，产出 `.product/spec/<产品线>/CURRENT.md`
2. `/sdd:product-spec export --tool v0` —— 按目标设计工具的方言导出 prompt 包
3. 在 Claude Design / v0 / Figma Make 出高保真原型
4. `/sdd:design-to-code` —— 把原型还原为生产级前端代码
5. 产品迭代时 `/sdd:product-spec add <标题>` 记一版增量，回到第 2 步

`product-spec` 只写「有什么功能、怎么交互」，`design-to-code` 只管「怎么变成代码」，中间的「长什么样」由项目的 `tokens.css` / `design.md` 承接——三者不重叠。

## 与仓库 skills/ 的关系

`plugins/sdd/skills/` 下均为指向 `skills/` 的符号链接，内容单一来源。直接编辑 `skills/<name>/SKILL.md` 即可，plugin 侧自动生效。
