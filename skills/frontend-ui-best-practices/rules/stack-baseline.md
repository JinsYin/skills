---
title: 前端技术栈基线
impact: LOW
tags: stack, dependencies
---

## 前端技术栈基线

| 层面 | 选型 |
|---|---|
| 包管理 | pnpm |
| 构建 | Vite |
| 框架 | React + TypeScript |
| 组件库 | shadcn/ui（基于 Radix UI） |
| 样式 | Tailwind CSS |
| 测试 | Vitest |

shadcn/ui 是**拷贝进项目**而非依赖安装的组件，所以组件代码归项目所有，可直接修改；升级不会自动发生，需要主动同步上游变更。

具体的目录结构、路由划分、状态管理选型以项目自身的 CLAUDE.md 为准——这部分项目间差异大。
