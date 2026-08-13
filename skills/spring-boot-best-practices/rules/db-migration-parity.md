---
title: 迁移必须多方言同步同版本
impact: HIGH
impactDescription: 故障只在目标环境暴露
tags: db, migration, flyway, multi-dialect
---

## 迁移必须多方言同步同版本

项目同时支持多个数据库时，每条 migration 必须为**每个激活的 location 各维护一份**，版本号与名称严格一致。漏一份的后果是：开发环境全绿，目标环境启动时 Flyway 报缺失版本或表结构不一致——而这通常发生在生产。

关键约束：

- 同一版本号**只能出现在一个激活 location**，否则 Flyway 报重复版本
- 各份之间除方言差异外，内容必须逐字一致（建表体、ALTER、注释同步维护）
- 激活哪些 location 由构建期 profile 注入，不要在代码里硬编码

**改动清单**——加一条迁移时，逐个确认每个方言目录都有对应文件，再确认版本号无冲突。

同一数据库产品还有多种部署形态（分布式 / 集中式 / 单机）时，不要再按形态复制整套，见 `db-migration-base-overlay`。项目具体有几层 location、各层叫什么，以该项目 CLAUDE.md 为准。
