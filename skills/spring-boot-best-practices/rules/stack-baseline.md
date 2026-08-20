---
title: 技术栈基线
impact: LOW
tags: stack, dependencies
---

## 技术栈基线

| 层面 | 选型 |
|---|---|
| 基础 | Java 21 + Spring Boot 3.5 + Spring Cloud 2025.0（或兼容版本） |
| 网关 | Spring Cloud Gateway（WebFlux / Netty） |
| ORM | MyBatis Plus + mybatis-plus-join，**不用 XML 映射** |
| 连接池 | HikariCP |
| Web 容器 | Undertow |
| 鉴权 | Spring Security 或 Sa-Token，按项目规模选，见 `stack-auth-framework` |
| API 文档 | Knife4j（集成 SpringDoc OpenAPI 3） |
| 对象映射 | MapStruct |
| 样板消除 | Lombok |
| 构建 | Maven 3.8+，附带 Wrapper |
| 日志 | SLF4J + Logback，生产用 JSON 结构化输出 |

数据库与缓存的具体版本、以及多数据库支持策略，以项目自身的 CLAUDE.md 为准——这部分项目间差异大，不适合写死在通用规则里。
