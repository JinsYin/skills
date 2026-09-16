---
name: frontend-ui-best-practices
description: React + shadcn/ui 前端工程的技术栈基线与模块文档规范。涵盖包管理、构建、框架、组件库、样式与测试的选型基线，以及项目根目录与 monorepo 子包的 README 结构要求。在初始化前端项目、调整依赖选型、新增子包或补写模块文档时使用。界面与交互规范（表单校验、弹层状态、列表分页、日期格式、图标一致性）不在本 skill 范围内。
license: MIT
metadata:
  author: JinsYin
  version: "2.0.0"
---

# Frontend UI Best Practices

React + shadcn/ui 前端工程的**技术栈与结构**规范，2 条规则。

界面与交互规范（校验时机、弹层状态重置、破坏性操作确认、分页与对齐、日期数字格式、图标与
Toast 一致性）由 `ui-ux-best-practices` 负责，本 skill 不重复。

## 如何使用本 skill

| 你在做什么 | 先读 |
|---|---|
| 初始化前端项目 / 调整依赖选型 | `rules/stack-baseline.md` |
| 新增子包 / 写模块文档 | `rules/stack-module-readme.md` |

每条规则含：为什么、错误示例、正确示例。

## 规则索引

### 1. 技术栈与结构 (LOW)

- `stack-baseline` — pnpm + Vite + React + TS + shadcn/ui + Tailwind + Vitest
- `stack-module-readme` — 根目录必有 README；monorepo 下每个子包也各有一份，单包只需根 README

## 与项目 CLAUDE.md 的关系

本 skill 是**跨项目通用**基线。具体的目录结构、路由划分、状态管理选型以项目自身的
`CLAUDE.md` 为准，冲突时 CLAUDE.md 优先。

## 全量编译版

需要一次性获取全部规则时读 `AGENTS.md`。该文件由 `scripts/build.sh` 从 `rules/` 生成，
**不要手工编辑**。
