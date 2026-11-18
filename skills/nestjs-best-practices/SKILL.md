---
name: nestjs-best-practices
description: "NestJS 11 + Node 22 + Drizzle on GaussDB/openGauss: Controller/Service/Repository, JWT default-deny, argon2id, SM2/SM3/SM4 via sm-crypto-v2, Snowflake bigint ids, gaussdb-nodejs aliased as pg, drizzle-kit migrations, R/RList/RPage, class-validator. Use when changing Nest APIs, Drizzle schema, SQL migrations, auth, crypto, or module docs, or when Gauss login fails, SQL contains ON CONFLICT or gen_random_uuid(), JSON throws on bigint, or a route has no guard."
license: MIT
metadata:
  author: JinsYin
  version: "1.0.0"
---

# NestJS Best Practices

NestJS 11 backend rules: 54 rules, 9 categories, ordered by **consequence of violation**.

## How to use this skill

Read rules on demand, **never all upfront**. Match the task in the routing table or the index below, then `Read` only the needed files:

```
rules/layer-one-direction.md
rules/orm-id-snowflake-bigint.md
```

Route by **what you touch**, not by reading categories top to bottom:

| What you are doing | Read first |
|---|---|
| Adding a Controller | `layer-*`, `naming-controller-methods`, `naming-url`, `envelope-r-types` |
| Adding or editing a Drizzle table | `orm-*`, `db-table-naming`, `db-column-naming`, `db-index-naming` |
| Writing a migration | `db-migration-*`, `db-gauss-dialect`, `db-distributed-unique-index` |
| Adding or upgrading the DB driver or pool | `db-gauss-driver-selection`, `db-gauss-pool-provider`, `db-gauss-dependency-scope` |
| Editing an applied migration | `db-migration-immutable-after-apply`, `db-migration-monotonic-journal` |
| Defining DTOs or converters | `dto-*`, `naming-class-file` |
| Encryption, decryption, or signing | `crypto-*` (all 6 — small, tightly coupled) |
| Designing API contracts or error handling | `envelope-*`, `naming-url` |
| Wiring authentication / authorization | `auth-*` |
| Adding a feature module or package docs | `naming-module-layout`, `stack-module-readme`, `layer-cross-module-via-service` |
| Bootstrap, config, logging, tests | `stack-*` |
| Code review | Categories matching the files in the diff |

Done when every rule you opened holds in the diff. Record any exception in project `CLAUDE.md`.

## Silent failures

Check these before finishing. Each one still returns 200, or crashes only in production, if skipped:

1. New route has `@Public()` or `@RequirePermissions`, and both guards are `APP_GUARD` (`auth-global-guard-default-deny`).
2. Controller returns `R` / `RList` / `RPage` of a Response class (`layer-controller-no-row`, `envelope-r-types`).
3. Ids are `bigint` mode `'bigint'` in Drizzle and decimal strings on the wire (`orm-id-snowflake-bigint`).
4. `pg` is `gaussdb-nodejs@0.2.3` and the pool sets `sha256Iterations: 'server'` (`db-gauss-driver-selection`, `db-gauss-pool-provider`).
5. New SQL has no `ON CONFLICT` or `gen_random_uuid()`, and the change is `drizzle-kit generate`, not `push` (`db-gauss-dialect`, `db-migration-generate-not-push`).
6. SM4 calls pass `mode: 'gcm'` and a fresh 12-byte iv (`crypto-approved-algorithms`, `crypto-unique-iv-nonce`).

## Categories and impact

Ordered by **consequence of violation**, not frequency. CRITICAL: immediate bug, security hole, or startup/runtime failure. HIGH: review rejection. MEDIUM: inconsistent but valid. LOW: style.

| Priority | Category | Impact | Prefix | Rules |
|---|---|---|---|---|
| 1 | Layering discipline | CRITICAL | `layer-` | 6 |
| 2 | Authentication & authorization | CRITICAL | `auth-` | 3 |
| 3 | Cryptography | CRITICAL | `crypto-` | 6 |
| 4 | ORM & persistence | CRITICAL | `orm-` | 4 |
| 5 | Database & migrations | HIGH | `db-` | 13 |
| 6 | Response envelopes & error codes | HIGH | `envelope-` | 5 |
| 7 | DTO conventions | HIGH | `dto-` | 5 |
| 8 | Naming conventions | MEDIUM | `naming-` | 6 |
| 9 | Stack baseline | LOW | `stack-` | 6 |

`db-gauss-driver-selection`, `db-gauss-pool-provider`, and `db-migration-generate-not-push` are CRITICAL even though the category is HIGH: a wrong driver fails authentication, a missing pool error listener crashes the process, and `push` drops columns with no history.

## Rule index

### 1. Layering discipline (CRITICAL)

- `layer-one-direction` — Strict `Controller → Service → Repository`; only Repositories touch Drizzle
- `layer-controller-no-row` — Return view Responses, never Drizzle rows (leaks hash and `deleted`)
- `layer-no-loose-response` — Typed response classes, never `any` / `Record` / `Map` (hides OpenAPI)
- `layer-cross-module-via-service` — Export the Service only; never another module's Repository
- `layer-service-no-http` — Typed args into Services; keep Express `Request` out
- `layer-no-silent-catch` — Translate or rethrow; a swallowed error looks like 200

### 2. Authentication & authorization (CRITICAL)

- `auth-global-guard-default-deny` — `APP_GUARD` JWT + permission guards; `@Public()` is the only opt-out
- `auth-jwt-verification` — Pin the algorithm, short lifetime, secret from config; never `jwt.decode`
- `auth-password-hashing` — `argon2id` in the Service; store the PHC string only

### 3. Cryptography (CRITICAL)

- `crypto-approved-algorithms` — SM2 `C1C3C2` / SM3 / SM4-GCM; omitting `mode` silently uses ECB
- `crypto-single-library` — Exact `sm-crypto-v2@2.0.1` behind one `CryptoService`; ban v1 and `sm-crypto`
- `crypto-sign-canonical-bytes` — Sign sorted-key UTF-8 bytes; pass `der` and `userId` explicitly
- `crypto-unique-iv-nonce` — Fresh `randomBytes` IV/nonce per encryption
- `crypto-no-hardcoded-secrets` — Keys from config, separated by purpose, with `keyId`
- `crypto-no-secret-logging` — Log `keyId` and length; opaque error code on crypto failure

### 4. ORM & persistence (CRITICAL)

- `orm-id-snowflake-bigint` — App Snowflake as `bigint` mode `bigint`; decimal string on the wire
- `orm-audit-columns-app-filled` — Repository sets audit columns; no `ON UPDATE` database default
- `orm-transaction-via-cls` — `@Transactional()` plus `txHost.tx`; a root client commits early
- `orm-query-builder-only` — Drizzle builder; no full-statement SQL; no `ON CONFLICT`

### 5. Database & migrations (HIGH)

- `db-gauss-driver-selection` — `pg` aliased to exact `gaussdb-nodejs@0.2.3`, plus pnpm peer override
- `db-gauss-pool-provider` — One pool, `error` listener, timeouts, `sha256Iterations: 'server'`, shutdown
- `db-gauss-dependency-scope` — Driver and Drizzle only in packages that connect
- `db-gauss-dialect` — No `ON CONFLICT`, no `gen_random_uuid()`, no `jsonb_build_object`
- `db-migration-generate-not-push` — `drizzle-kit generate` and review SQL; never `push`
- `db-migration-dedicated-job` — One-shot migrator process; not in API bootstrap
- `db-migration-immutable-after-apply` — Drizzle compares timestamps, not hashes; edits drift silently
- `db-migration-monotonic-journal` — Journal `when` must stay strictly increasing or files are skipped
- `db-migration-base-overlay` — Generated portable base plus one overlay per topology
- `db-distributed-unique-index` — Inline `UNIQUE` on new tables; `CREATE GLOBAL UNIQUE INDEX` in the overlay
- `db-table-naming` — `t_` + `snake_case` + singular noun
- `db-column-naming` — Explicit `snake_case`, four audit columns, `deleted` boolean
- `db-index-naming` — `uk_{table}_{field}` and `idx_{table}_{field}`

### 6. Response envelopes & error codes (HIGH)

- `envelope-r-types` — Pick `R` / `RList` / `RPage` by payload shape; no second wrapper
- `envelope-factory-only` — Static factories and one exception filter; private constructors
- `envelope-error-code-format` — 6-digit codes prefixed with the 3-digit HTTP status
- `envelope-bizexception-not-null` — Throw `BizException`; do not return `null` for not-found
- `envelope-field-types` — Datetime `yyyy-MM-dd HH:mm:ss`, money and ids as decimal strings

### 7. DTO conventions (HIGH)

- `dto-request-by-action` — `{Action}Request` plus global `ValidationPipe` whitelist
- `dto-query-extends-pagequery` — Paginated queries extend `PageQuery` (`pageSize` ≤ 200)
- `dto-internal-not-exposed` — `Dto` stays inside Services and queues
- `dto-response-by-view` — Responses named by view; Chinese `@ApiProperty`
- `dto-converter-explicit` — Object literal with an explicit return type; no cast, no row spread

### 8. Naming conventions (MEDIUM)

- `naming-class-file` — Class suffix and kebab-case file name table
- `naming-controller-methods` — Resource-free CRUD verbs in fixed declaration order
- `naming-service-repository-methods` — Resource noun on Services; `findBy` / `listBy` on Repositories
- `naming-url` — Lowercase kebab-case plural paths
- `naming-module-layout` — One feature folder per module; shared kernel stays feature-free
- `naming-enum-constants` — String enum wire values, not numeric enums

### 9. Stack baseline (LOW)

- `stack-baseline` — Node 22, Nest 11, Drizzle, pnpm, and the pinned Gauss and SM libraries
- `stack-config-schema` — Zod-validated `@nestjs/config`; no scattered `process.env`
- `stack-bootstrap` — Global prefix, pino logger, shutdown hooks, gated Swagger
- `stack-logging` — `nestjs-pino` 4.x JSON logs with a redact list
- `stack-testing` — Jest unit tests with a mocked Repository; Supertest for HTTP
- `stack-module-readme` — Root README always; one README per workspace package

## Relationship to the project's CLAUDE.md

Cross-project baseline. Topology, JWT algorithm (HS256 vs RS256), Snowflake worker-id scheme, and Redis or queue choices live in project `CLAUDE.md`. `CLAUDE.md` wins on conflict.

Leave rule text in this skill. Project `CLAUDE.md` records only the decisions above. A pasted copy loads every session and drifts.

## Full compiled version

Read `AGENTS.md` when the full ruleset is needed at once. Generated from `rules/` by `scripts/build.sh` — **never edit by hand**.
