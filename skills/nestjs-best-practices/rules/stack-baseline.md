---
title: Backend stack baseline
impact: LOW
tags: stack, dependencies
---

## Backend stack baseline

| Layer | Choice |
|---|---|
| Runtime | Node 24 + NestJS 11 (`@nestjs/core` 11.x, `@nestjs/platform-express`) |
| ORM | `drizzle-orm` 0.45.x via `drizzle-orm/node-postgres`, `drizzle-kit` 0.31.x |
| Driver | `pg` aliased to `gaussdb-nodejs@0.2.3` — see `db-gauss-driver-selection` |
| Transactions | `nestjs-cls` + `@nestjs-cls/transactional` + `@nestjs-cls/transactional-adapter-drizzle-orm` |
| Auth | `@nestjs/jwt` 11.x, global guards — see `auth-global-guard-default-deny` |
| Password | `argon2` (`argon2id`) |
| Validation | `class-validator` + `class-transformer` |
| API docs | `@nestjs/swagger` 11.x |
| Config | `@nestjs/config` 4.x + `zod` 4 |
| Logging | `nestjs-pino` 4.x (5.x tracks Nest 12) |
| Crypto | `sm-crypto-v2@2.0.1` exact |
| Ids | Application Snowflake, `bigint` mode |
| Tests | Jest + Supertest (`@nestjs/testing`) |
| Packages | pnpm workspace, versions in the catalog |

Pins above are the baseline line, not a floating "latest". `gaussdb-nodejs` and `sm-crypto-v2` stay exact. Redis, queue, and scheduler choices belong in project `CLAUDE.md`.
