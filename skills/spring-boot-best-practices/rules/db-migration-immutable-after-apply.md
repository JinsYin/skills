---
title: 已执行的迁移不可编辑，改注释也算改
impact: HIGH
impactDescription: checksum 失配，已执行该版本的环境启动即失败
tags: db, migration, flyway, checksum, repair
---

## 已执行的迁移不可编辑，改注释也算改

Flyway 对每个迁移文件存一份 checksum，算的是**整个文件内容**——注释、空行、缩进全在内。改一个已经执行过的版本，下次启动 validate 阶段就会报 checksum 失配并拒绝继续，而**只在已经跑过该版本的环境上报**：新环境从零 migrate 一路绿灯，老环境（通常是生产）起不来。

所以默认纪律是：**已执行的版本只读，要改就发新版本**。给列改类型、补索引、修数据，都写 `V<n+1>__fix_xxx.sql`。

例外只有一类：改动**不影响已执行结果**，纯粹是注释、格式、或产品归属标注（例如把一份 overlay 的注释从「集中式 GaussDB」改成「社区 openGauss」）。这时重发一个新版本毫无意义——它什么也不做。正确做法是接受 checksum 变化，然后让每个已执行过该版本的环境**先 repair 再 migrate**：

```bash
flyway repair   # 用当前文件内容重写 flyway_schema_history 里的 checksum
flyway migrate
```

Spring Boot 侧对应 `spring.flyway.repair-on-migrate`（或部署流程里先跑一次 repair 任务）。**这一步必须写进变更说明**——漏掉它的环境会在下一次滚动发布时才炸，那时已经和这次改动隔了很久。

**不要用关闭校验来绕过：**

```yaml
# ❌ 把真实的结构漂移一起关掉了
spring.flyway.validate-on-migrate: false
```

`validate-on-migrate: false` 不只放过你这次的注释改动，也放过「有人手工改过生产表结构」「某个版本文件被误删」这类真问题——而这些正是 validate 唯一能替你抓到的东西。若项目因历史原因已经关着它，那更要在变更说明里显式写清 repair 步骤：此时没有任何自动检查会提醒执行者。
