---
title: Backend stack baseline
impact: LOW
tags: stack, dependencies
---

## Backend stack baseline

| Layer | Choice |
|---|---|
| Runtime & framework | Java 21 + Spring Boot 3.5 + Spring Cloud 2025.0 (or compatible) |
| API Gateway | Spring Cloud Gateway (WebFlux / Netty) |
| ORM | MyBatis-Plus + `mybatis-plus-join`, **no XML mappers** |
| Connection pool | HikariCP |
| openGauss / GaussDB drivers | Allowlisted coordinates only — see `db-gauss-driver-selection` |
| Embedded container | Undertow |
| Auth | Spring Security or Sa-Token by project scale — see `stack-auth-framework` |
| API docs | Knife4j (on SpringDoc OpenAPI 3) |
| Object mapping | MapStruct |
| Boilerplate reduction | Lombok |
| Build | Maven 3.8+ with Maven Wrapper |
| Logging | SLF4J + Logback, structured JSON output in prod |

DB/cache versions and multi-dialect targets live in project `CLAUDE.md` — too project-specific to hardcode here.
