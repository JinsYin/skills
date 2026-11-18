---
name: spring-boot-best-practices
description: "Rules for Spring Boot 3 + Java 21 + MyBatis-Plus backends: Controller/Service/Mapper layering, SM2/SM3/SM4 cryptography, MyBatis-Plus entities and primary keys, openGauss/GaussDB driver and Flyway dependencies, multi-dialect Flyway migrations, R/RList/RPage envelopes and 6-digit error codes, Request/Response/Query/Dto boundaries and MapStruct, Spring Security vs Sa-Token auth, naming, and module READMEs. Use when writing, reviewing, or refactoring Spring Boot backend code, SQL migrations, Maven DB dependencies, API contracts, auth config, or module docs."
license: MIT
metadata:
  author: JinsYin
  version: "1.0.0"
---

# Spring Boot Best Practices

Coding and architecture rules for Spring Boot 3 backends: 49 rules across 8 categories, ordered by **consequence of violation**.

## How to use this skill

Read rules on demand, **never all upfront**. Match task in routing table or index below, then `Read` only needed files:

```
rules/layer-one-direction.md
rules/entity-tableid-assign-id.md
```

Route by **what you touch**, not by reading categories top to bottom:

| What you are doing | Read first |
|---|---|
| Adding Controller | `layer-*`, `naming-controller-methods`, `envelope-r-types` |
| Adding or editing Entity | `entity-*`, `db-table-naming`, `db-column-naming` |
| Writing DB migration | `db-migration-*`, `db-opengauss-*`, `db-index-naming` |
| Adding or upgrading JDBC/R2DBC driver or Flyway dependency | `db-gauss-*`, `db-opengauss-flyway-set-role` |
| Adding unique constraint or index | `db-distributed-unique-index`, `db-index-naming` |
| Editing applied migration | `db-migration-immutable-after-apply` |
| Defining DTOs or converters | `dto-*`, `naming-class-suffix` |
| Encryption, decryption, or signing | `crypto-*` (all 6 — small, tightly coupled) |
| Designing API contracts or error handling | `envelope-*`, `naming-url` |
| Wiring authentication / authorization | `stack-auth-framework`, `layer-controller-auth-annotations` |
| Adding module / writing module docs | `stack-module-readme`, `naming-package-layout` |
| Code review | Categories matching file types in diff |

## Categories and impact

Graded by **consequence of violation**, not frequency: CRITICAL = immediate bug, security hole, or startup/runtime failure; HIGH = review rejection and rework; MEDIUM = inconsistent though valid; LOW = style preference.

| Priority | Category | Impact | Prefix | Rules |
|---|---|---|---|---|
| 1 | Layering discipline | CRITICAL | `layer-` | 7 |
| 2 | Cryptography | CRITICAL | `crypto-` | 6 |
| 3 | Entities & persistence | CRITICAL | `entity-` | 3 |
| 4 | Database & migrations | HIGH | `db-` | 12 |
| 5 | Response envelopes & error codes | HIGH | `envelope-` | 5 |
| 6 | DTO conventions | HIGH | `dto-` | 5 |
| 7 | Naming conventions | MEDIUM | `naming-` | 6 |
| 8 | Stack baseline | LOW | `stack-` | 5 |

## Rule index

### 1. Layering discipline (CRITICAL)

- `layer-one-direction` — Strict `Controller → Service → Mapper` flow; each layer depends only on adjacent lower layer
- `layer-controller-no-entity` — Return view Responses from Controllers, never Entities (leaks sensitive columns)
- `layer-no-map-response` — Use typed Response classes, never `Map<String, Object>` (hides OpenAPI contract)
- `layer-controller-auth-annotations` — Declare permissions via Spring Security / Sa-Token annotations; inline `if` checks fail open
- `layer-cross-service-via-service` — Call other domains via their Service, never their Mapper
- `layer-service-no-http` — Pass typed args into Services; keep `HttpServletRequest` out to decouple from web container
- `layer-no-silent-catch` — Translate or rethrow caught exceptions; never swallow silently (masks failure as 200 OK)

### 2. Cryptography (CRITICAL)

- `crypto-approved-algorithms` — SM2 `C1C3C2` / SM3 / SM4-GCM only; ban ECB, MD5, SHA-1, custom primitives
- `crypto-provider-registration` — Register BouncyCastle once at startup, never on hot paths
- `crypto-sign-canonical-bytes` — Sign deterministic canonical bytes only, never `toString()`
- `crypto-unique-iv-nonce` — Fresh `SecureRandom` IV/nonce per encryption; GCM nonce reuse breaks confidentiality and auth
- `crypto-no-hardcoded-secrets` — Load keys externally, separate encrypt/sign/MAC keys, attach `keyId`; never hardcode secrets
- `crypto-no-secret-logging` — Log only `keyId`/length and return opaque error codes; never log plaintext or keys

### 3. Entities & persistence (CRITICAL)

- `entity-tableid-assign-id` — Use `IdType.ASSIGN_ID` for primary keys; `AUTO` fails `INSERT` on non-MySQL DBs
- `entity-field-fill` — Populate `createdAt`/`updatedAt` via `@TableField(fill = ...)`, never DB defaults
- `entity-mapper-no-xml` — Build queries with MyBatis-Plus wrappers and MPJ API; no Mapper XML or full-statement SQL

### 4. Database & migrations (HIGH)

- `db-migration-parity` — Keep multi-dialect migrations in lockstep at identical versions; missing dialect fails only in target env
- `db-migration-base-overlay` — Split base vs overlay by portable syntax; size overlays one per deployment target
- `db-migration-locations-injection` — Inject Flyway locations via build profile while packaging all inactive overlays into JAR
- `db-migration-immutable-after-apply` — Applied migrations are read-only; even comment edits break checksums and require `repair`
- `db-distributed-unique-index` — Include distribution key in distributed unique constraints: inline on new tables, GSI on existing tables
- `db-opengauss-dialect` — openGauss three rules: no `ON CONFLICT`, no `gen_random_uuid()`, no `jsonb_build_object`
- `db-opengauss-flyway-set-role` — Gauss-family DBs reject `SET ROLE`; register project-owned Flyway Plugin SPI, never shadow JARs or disabled validation, or all migrations abort
- `db-gauss-driver-selection` — Pick Gauss JDBC/R2DBC coordinates from verified allowlist; some published versions are empty JARs or third-party-hosted
- `db-gauss-dependency-scope` — Declare drivers and Flyway only in modules using them, versions in parent; leaked artifacts crash unrelated modules
- `db-table-naming` — Table names use `t_` prefix + `snake_case` + singular noun
- `db-column-naming` — `snake_case` columns, four audit columns, `deleted` for soft delete
- `db-index-naming` — `uk_{table}_{field}` and `idx_{table}_{field}`

### 5. Response envelopes & error codes (HIGH)

- `envelope-r-types` — Pick `R` / `RList` / `RPage` by payload shape
- `envelope-factory-only` — Construct envelopes via static factories only, never `new R<>()` + setters
- `envelope-error-code-format` — 6-digit error codes prefixed with 3-digit HTTP status
- `envelope-bizexception-not-null` — Throw `BizException` on business failure, never return `null`
- `envelope-field-types` — `LocalDateTime` for timestamps, `BigDecimal` for money, uniform ID type per entity

### 6. DTO conventions (HIGH)

- `dto-request-by-action` — Name Requests by action; require Jakarta Validation with Chinese `message`
- `dto-query-extends-pagequery` — Paginated queries must `extends PageQuery` to enforce `pageSize` cap
- `dto-internal-not-exposed` — Keep `Dto` internal; split dual-role objects into `Dto` + `Response`
- `dto-response-by-view` — Name Responses by view; annotate all fields with Chinese `@Schema`
- `dto-converter-mapstruct` — Map via MapStruct; manual setters silently drop newly added fields

### 7. Naming conventions (MEDIUM)

- `naming-class-suffix` — Class suffix reference table by role and package
- `naming-controller-methods` — Fixed resource-free CRUD verbs in canonical declaration order
- `naming-service-mapper-methods` — Include resource nouns on Service methods; prefix Mapper queries with `selectBy`/`listBy`/`countBy`
- `naming-url` — Lowercase `kebab-case`, plural resources, sub-paths for non-CRUD actions
- `naming-package-layout` — Top-level packages by technical role, second-level by domain under `dto` only
- `naming-enum-constants` — Control enum JSON wire values explicitly with `@JsonValue`

### 8. Stack baseline (LOW)

- `stack-auth-framework` — Spring Security for large/infra platforms, Sa-Token for small/medium apps; one per project
- `stack-baseline` — Dependency baseline across runtime, ORM, container, docs, mapping, build, logging
- `stack-module-readme` — Root `README.md` always; one `README.md` per submodule in multi-module builds
- `stack-lambda-simple` — Extract multi-line lambdas into named methods; stack traces only show `lambda$xxx$0`
- `stack-lombok` — `@Data` on DTOs, `@RequiredArgsConstructor` + `final` fields on Spring beans

## Relationship to the project's CLAUDE.md

Cross-project baseline. Project-specific package roots, module splits, Flyway location hierarchies, and locked domain decisions live in project `CLAUDE.md` — `CLAUDE.md` wins on conflict.

Never copy these rules into project `CLAUDE.md`: `CLAUDE.md` loads every session, multiplying token cost while copies drift apart.

## Full compiled version

Read `AGENTS.md` (~50 KB) when full ruleset needed at once. Generated from `rules/` by `scripts/build.sh` — **never edit by hand**.
