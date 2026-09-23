# Agent Skills

自定义 Agent 配置与技能（Skills）集合。

## 安装与使用

```bash
npx skills@latest add jinsyin/skills
```

## 包含技能

- `frontend-ui-best-practices` - 前端技术栈基线、项目脚手架、样式与 token 文件组织、模块文档规范
- `ui-ux-best-practices` - 后台管理界面 UI/UX 最佳实践
- `devops-best-practices` - DevOps 运维最佳实践
- `doc-writing-best-practices` - 文档编写最佳实践
- `spring-boot-best-practices` - Spring Boot 后端开发最佳实践
- `setup-rules` - 交互式安装 Agent 约定、适配器及敏感文件禁读配置
- `ideate` - 将产品想法与上下文方案逐项澄清，按固定结构整理并保存为 `docs/ideas/idea.md`
- `doc-to-md` - 内容转换 Markdown 工具
- `product-spec` - 管理产品功能规范（功能、交互、Flyway 式版本化变更记录），合成的 `CURRENT.md` 直接喂 Claude Design / v0 / Figma Make / Lovable
- `design-to-code` - 将高保真设计/原型还原为生产级 React 代码；技术栈与工程规则以 `frontend-ui-best-practices` 为准，设计系统以 `products/design/DESIGN.md` 为准，页面结构与交互以 `products/prototype/` 为准；产出留有数据接缝与视觉冻结检查，供后续 plan 接线而不改视觉
- `gsx` - GSD 工作流的统一前门，按 `--flag` 分派 20 种模式（`--fast` `--quick` `--debug` `--plan-phase` `--uat-autorun` `--vrf-approved` 等），包裹 `/gsd:*` 命令并附加项目专属校验（Context7 文档核对、原型保真约束、验收回写）

## 项目目录

- `skills/` - 自定义技能资源库（唯一事实来源）
- `CHANGELOG.md` - 版本变更日志
- `LICENSE` - MIT 开源协议

## 开源协议

本项目采用 [MIT License](LICENSE) 协议开源。
