---
title: 根目录与每个模块都要有 README
impact: MEDIUM
impactDescription: 目录职责无人可查，组件被复制而不是复用
tags: stack, structure, docs, readme
---

## 根目录与每个模块都要有 README

**项目根目录必须有 `README.md`**；monorepo 下的每个 `apps/*`、`packages/*` 子包也各自必须有 `README.md`。**单包项目只需要根 README**，`src/` 下的目录不必逐个写——单包里目录职责用一段"目录结构"小节在根 README 里说清即可，拆成多份反而增加漂移面。

包的边界不写下来就只能靠猜：`packages/ui` 里的 shadcn 组件能不能直接改、哪些能力是全站共用的、某个 app 依赖哪些内部包——猜出来的边界是当前实现的样子，不是设计意图，结果就是同一个业务组件被复制三份，改一处漏两处。

新增子包时同步新增 README；对外导出的组件、Hook、API 发生变化时同步更新，与改代码在同一个提交里。

**错误（目录靠猜）：**

```text
web/
├── README.md              ← 只写了 "pnpm dev"
├── packages/ui/           ← 没有 README，不知道能不能直接改 shadcn 组件
└── apps/admin/            ← 没有 README，不知道路由怎么划分
```

**正确（每层都能自解释）：**

```text
web/
├── README.md              ← 项目能力 + 包清单 + 快速开始
├── packages/ui/
│   └── README.md          ← shadcn/ui 组件与主题令牌；改动需全站回归
└── apps/admin/
    └── README.md          ← 后台管理端：路由划分、状态管理选型、接口约定
```

根 README 至少包含：

| 小节 | 内容 |
|---|---|
| 项目简介 | 一两句话说清这个界面服务于什么业务 |
| 核心能力 | 主要页面与功能清单 |
| 模块清单 | monorepo：表格列出各子包及其一句话职责，链接到子包 README；单包：一节"目录结构"说明各顶层目录放什么 |
| 技术栈 | 包管理、构建、框架、组件库、样式方案的版本基线 |
| 快速开始 | Node/pnpm 版本要求、安装、`dev`/`build`/`test` 命令、默认端口、后端地址配置 |

子包 README（monorepo）至少包含：

| 小节 | 内容 |
|---|---|
| 模块职责 | 这个包放什么，**以及明确不放什么** |
| 对外能力 | 导出的组件、Hook、工具；供谁使用 |
| 依赖说明 | 依赖了哪些内部包与关键三方库，为什么 |
| 本地运行 | 单独 dev / build / test 该模块的命令（如果可以单独跑） |

写法遵循 `doc-writing-best-practices`：示例可直接粘贴执行、写清为什么、中西文之间加空格。

README 不是 `CLAUDE.md` 的替代品，两者受众不同：README 面向人，讲能力与边界；CLAUDE.md 面向 AI，讲当前项目锁定的决策与约束。不要把同一段内容抄两份。
