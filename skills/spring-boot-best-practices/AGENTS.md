# Spring Boot Best Practices

> Generated from `rules/` by `scripts/build.sh`. Do not edit by hand.
> Generated at: 2026-11-18 14:08:14

## 1. Layering Discipline


### Declare permission checks with annotations, not inside method bodies

Enforce auth via declarative framework config and annotations — never inline `if` checks inside controller methods. Declarative security **fails closed**: once fallback rule is wired, new endpoints stay protected automatically. Imperative checks **fail open**: one forgotten `if` exposes endpoint unauthenticated, and privileged test tokens still get 200.

See `stack-auth-framework` for framework selection. Equivalent forms:

| Requirement | Spring Security | Sa-Token |
|---|---|---|
| Authenticated user | `.anyRequest().authenticated()` fallback in `SecurityFilterChain` | `@SaCheckLogin` at class level |
| Permission code | `@PreAuthorize("hasAuthority('user:query')")` | `@SaCheckPermission("user:query")` |
| Role | `@PreAuthorize("hasRole('admin')")` | `@SaCheckRole("admin")` |
| Public endpoint | `.requestMatchers("/auth/login").permitAll()` | `@SaIgnore` |

Silent failure modes (neither throws an exception):

- **Spring Security**: `@PreAuthorize` requires `@EnableMethodSecurity` (replaces `@EnableGlobalMethodSecurity` since Spring Security 6); without it, method annotations are ignored and all methods allow access. Also, `hasRole('admin')` matches authority `ROLE_admin` — stored authorities missing `ROLE_` prefix always evaluate `false`.
- **Sa-Token**: allows requests by default, checking only annotated or intercepted handlers. Put `@SaCheckLogin` on controller class so new methods inherit login check.

Register public endpoints **explicitly** (`permitAll()` in Spring Security, `@SaIgnore` in Sa-Token), never by omitting annotations — explicit opt-out proves openness is intentional.

**Wrong (inline check inside method body — fails open):**

```java
@GetMapping
public RPage<UserListItemResponse> page(@Valid UserPageQuery query) {
    if (!StpUtil.hasPermission("user:query")) {   // relies on human memory; next method forgotten = exposed
        throw new BizException(ErrorCode.FORBIDDEN);
    }
    return RPage.ok(userService.listUsers(query));
}
```

**Right (Spring Security):**

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity   // without this, @PreAuthorize below is silently ignored
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                // Pure Bearer token with no Cookie session: CSRF adds nothing; keep enabled if token is in a Cookie
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/auth/login").permitAll()   // register public endpoints explicitly
                        .anyRequest().authenticated())                // default deny fallback
                .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
                .build();
    }
}

@Tag(name = "用户")
@RestController
@RequestMapping("/users")
@Validated
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "分页查询用户")
    @GetMapping
    @PreAuthorize("hasAuthority('user:query')")
    public RPage<UserListItemResponse> page(@Valid UserPageQuery query) {
        return RPage.ok(userService.listUsers(query));
    }
}
```

**Right (Sa-Token):**

```java
@Tag(name = "用户")
@SaCheckLogin   // class-level so new methods inherit login check automatically
@RestController
@RequestMapping("/users")
@Validated
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "分页查询用户")
    @GetMapping
    @SaCheckPermission("user:query")
    public RPage<UserListItemResponse> page(@Valid UserPageQuery query) {
        return RPage.ok(userService.listUsers(query));
    }
}
```


### Controllers must never return Entities

Return view-specific `Response` types from Controllers, never `Entity`. Entity maps every table column (password hashes, soft-delete flags, internal audit fields); returning it exposes sensitive data, and adding table columns later silently widens public API output.

**Wrong (exposing raw table row):**

```java
@GetMapping("/users/{id}")
public R<UserEntity> get(@PathVariable Long id) {
    return R.ok(userService.getEntityById(id)); // ❌ includes password / deleted
}
```

**Right (view-specific Response with explicit fields):**

```java
@GetMapping("/users/{id}")
public R<UserDetailResponse> get(@PathVariable Long id) {
    return R.ok(userService.getById(id));
}
```

Service methods must also return `Response`, `Dto`, or primitives — **never** `Entity`, or leak risk shifts up into Controller.


### Cross-domain calls go through Service, never another domain's Mapper

Service may inject another Service, **never** another domain's Mapper. Bypassing owning Service skips its validation, cache eviction, and transaction invariants — bugs hidden until other domain changes.

**Wrong:**

```java
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;
    private final RoleMapper roleMapper; // ❌ bypasses RoleService
}
```

**Right:**

```java
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;   // own domain's Mapper
    private final RoleService roleService; // cross-domain via Service
}
```


### Never use Map as a response type

Return typed `Response` classes, never `Map<String, Object>`. `Map<String, Object>` lacks compile-time checks and renders empty OpenAPI schema, forcing callers to guess keys or read backend code. Renaming keys gives zero compiler warning.

**Wrong:**

```java
@GetMapping("/stats")
public R<Map<String, Object>> stats() {
    Map<String, Object> m = new HashMap<>();
    m.put("total", 100);
    m.put("active", 80);
    return R.ok(m); // ❌ invisible contract
}
```

**Right:**

```java
@Data
@Schema(description = "统计响应")
public class StatsResponse {
    @Schema(description = "总数") private Long total;
    @Schema(description = "活跃数") private Long active;
}
```

Sole exception: dynamic user-defined schemas (e.g., custom form builders), still wrapped inside typed envelope field.


### Never silently swallow exceptions

Translate caught exceptions into domain errors or rethrow — never catch without handling or rethrowing. Silent `catch` masks failure as 200 OK with empty/partial state, pushing crash downstream after root-cause context is lost.

**Wrong:**

```java
try {
    userMapper.insert(entity);
} catch (Exception e) {
    // ❌ does nothing; caller assumes insert succeeded
}
```

**Right (translate to domain error or let global handler wrap):**

```java
try {
    externalClient.sync(entity);
} catch (RestClientException e) {
    log.warn("Upstream sync failed, entityId={}", entity.getId(), e);
    throw new BizException(ErrorCode.UPSTREAM_UNAVAILABLE);
}
```

Swallowing allowed only on non-critical side channels (e.g., telemetry), and must log warning plus comment explaining why failure is safe to ignore.


### One-way layered dependencies

`Controller → Service → Mapper`: each layer depends only on adjacent lower layer. Reverse or skip-layer calls break transaction boundaries, unit testability, and reuse at once.

| Layer | Responsibility | Forbidden |
|---|---|---|
| Controller | HTTP contract: routing, binding, validation, auth | Calling Mappers; calling other Controllers |
| Service | Business logic, transactions, orchestration, external calls, caching | HTTP/view concerns; injecting another domain's Mapper |
| Mapper | Database access and ORM mapping | Business rules, validation, transaction control |

**Wrong (Controller injects Mapper directly, bypassing transactions and domain checks):**

```java
@RestController
@RequiredArgsConstructor
public class UserController {
    private final UserMapper userMapper; // ❌ skips Service layer
    @GetMapping("/users/{id}")
    public R<UserEntity> get(@PathVariable Long id) {
        return R.ok(userMapper.selectById(id));
    }
}
```

**Right:**

```java
@RestController
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;
    @GetMapping("/users/{id}")
    public R<UserDetailResponse> get(@PathVariable Long id) {
        return R.ok(userService.getById(id));
    }
}
```


### Keep HTTP types out of Services

Pass typed parameters into Services; keep `HttpServletRequest`, `request.getParameter()`, and HTTP headers/status codes out. Servlet types inside Service couple domain logic to web container — unit tests then require `MockMvc`, and cron jobs or MQ consumers cannot reuse logic.

**Wrong:**

```java
public boolean create(HttpServletRequest request) { // ❌
    String name = request.getParameter("name");
}
```

**Right (Controller parses HTTP and auth context; Service takes typed parameters):**

```java
public boolean create(UserCreateRequest request, Long operatorId) {
    // pure domain logic reusable across Controllers, cron jobs, and MQ consumers
}
```

Extract caller context (e.g., operator ID) in Controller and pass explicitly, or read via transport-agnostic context holder — never read Servlet objects in Service.

## 2. Cryptography


### Use only approved ShangMi algorithms and modes

| Purpose | Required | Forbidden |
|---|---|---|
| Asymmetric encryption | SM2 `C1C3C2` | `C1C2C3` (isolated legacy adapter only) |
| Digital signature | SM2 + SM3 digest | — |
| Message digest | SM3 | MD5, SHA-1 |
| Symmetric encryption | `SM4/GCM/NoPadding` | **Any `SM4/ECB/*`** |
| Legacy compatibility | `SM4/CBC/PKCS5Padding` | DES, 3DES, RC4 |

ECB encrypts identical plaintext blocks into identical ciphertext blocks, exposing structure directly in ciphertext — zero semantic security regardless of key size.

Use vetted Bouncy Castle primitives; never implement cryptographic primitives by hand.


### Never hardcode secrets; separate keys by purpose

Load keys and secrets from external config or secret stores — never hardcode private keys, symmetric keys, IVs, nonces, salts, or prod secrets in code. Secrets committed to git history stay permanently compromised even if deleted in later commits.

- **Separate keys by purpose**: distinct keys for encryption, signing, and MAC/integrity so one leaked key cannot compromise all security properties.
- Encode SM2 keys as PEM/DER, SM4 keys as 16 raw bytes.
- Attach `keyId` to payloads whenever ciphertext lifetime outlives key rotation.
- Use Base64 for binary wire transport unless peer protocol mandates hex.

Ciphertexts without `keyId` fail decryption after key rotation — usually discovered on rotation day.


### Never log keys or plaintext

Log non-sensitive metadata (`keyId`, payload length) only — **never** log plaintext, private keys, symmetric keys, full ciphertexts, full signatures, or decrypted payloads. Logs are centralized, retained long-term, and readable by far more roles than prod databases, widening blast radius.

Treat decryption failure, auth-tag mismatch, malformed ciphertext, and bad signature as **security errors**: return stable opaque business error code without exposing crypto failure details (prevents padding/tag oracles).

**Wrong:**

```java
log.error("Decryption failed, ciphertext={}, key={}", cipherText, keyHex, e); // ❌
```

**Right:**

```java
log.warn("Decryption failed, keyId={}, len={}", keyId, cipherText.length);
throw new BizException(ErrorCode.DECRYPT_FAILED);
```

Tests must cover: SM2 `C1C3C2` round-trip, signature verification pass/fail, SM3 known-answer digests, SM4 nonce uniqueness and tamper detection.


### Register BouncyCastle Provider once at startup

Use `org.bouncycastle:bcprov-jdk18on` and register once at app startup — never inside per-request encrypt/decrypt calls. `Security.addProvider` takes global synchronization locks and bottlenecks hot paths.

**Right:**

```java
@Configuration
public class CryptoConfig {
    @PostConstruct
    public void registerProvider() {
        if (Security.getProvider(BouncyCastleProvider.PROVIDER_NAME) == null) {
            Security.addProvider(new BouncyCastleProvider());
        }
    }
}
```

If module already uses another compliant JCE provider, keep that single provider; never mount two.


### Sign and hash canonical bytes only

Pass **deterministic byte sequences** to signing and hashing. Signing `Map.toString()`, `Object.toString()`, or JSON without deterministic key order yields different bytes across JVMs or library versions — causing random, hard-to-reproduce verification failures.

**Wrong:**

```java
byte[] data = payload.toString().getBytes(); // ❌ key order and charset unspecified
byte[] sig = signSm2Sm3(privateKey, data);
```

**Right (canonical serialization with fixed field order and UTF-8):**

```java
byte[] canonical = canonicalize(payload); // sorted keys + fixed formatting + explicit UTF-8
byte[] sig = signSm2Sm3(privateKey, canonical);
```

For untrusted external inputs, **verify signature before trusting payload**. Before SM2 decryption, validate `C1` / `C3` / `C2` segment lengths; `C1` requires uncompressed EC point prefix `0x04` unless peer protocol explicitly omits it.

Compare digests in constant time (`MessageDigest.isEqual`), never short-circuiting byte comparisons that leak timing side channels.


### Generate a fresh random IV / nonce per encryption

- SM4 key: exact 128 bits / 16 bytes.
- GCM nonce: 96 bits / 12 bytes, **unique per encryption under same key**.
- CBC IV: 16 bytes, generated fresh via `SecureRandom` per call.

GCM nonce reuse lets attackers XOR keystreams and recover GHASH authentication key, forging valid tags on arbitrary ciphertexts.

**Wrong:**

```java
private static final byte[] IV = "1234567890123456".getBytes(); // ❌ static IV
```

**Right:**

```java
byte[] nonce = new byte[12];
SecureRandom.getInstanceStrong().nextBytes(nonce); // fresh per call; transmit alongside ciphertext
```

Never derive keys by truncating or slicing password strings — collapses entropy from 128 bits to password entropy.

## 3. Entities & Persistence


### Populate audit timestamps via @TableField(fill)

Populate audit timestamps in app layer via MyBatis-Plus `MetaObjectHandler` + `@TableField(fill = ...)` — never rely on DB `ON UPDATE CURRENT_TIMESTAMP` (MySQL-only; stripped on Gauss-family DBs, leaving `updated_at` `NULL` or frozen).

**Wrong (relying on database DDL defaults/triggers):**

```java
private LocalDateTime createdAt; // ❌ no fill; relies on DB default
private LocalDateTime updatedAt;
```

**Right:**

```java
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createdAt;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updatedAt;
```

Mark `createdAt` with `FieldFill.INSERT` and `updatedAt` with `FieldFill.INSERT_UPDATE`.


### No Mapper XML or raw full-statement SQL

Extend `MPJBaseMapper<Entity>` on Mappers and build queries with MyBatis-Plus wrappers and MPJ APIs (`selectJoinPage`, `leftJoin`, `selectAs`) — no Mapper XML or raw full-statement SQL. Handwritten full SQL binds to one dialect and forks across multi-DB targets.

**Wrong:**

```java
@Mapper
public interface UserMapper extends MPJBaseMapper<UserEntity> {
    @Select("SELECT * FROM t_user WHERE status = #{status} LIMIT 10") // ❌ dialect-specific SQL
    List<UserEntity> listByStatus(String status);
}
```

**Right:**

```java
@Mapper
public interface UserMapper extends MPJBaseMapper<UserEntity> {
}

// Build queries with wrappers inside the Service
LambdaQueryWrapper<UserEntity> w = Wrappers.lambdaQuery(UserEntity.class)
        .eq(UserEntity::getStatus, status)
        .last("LIMIT 10");
```

When complex projections or aggregations cannot use wrappers alone, small bound SQL fragments inside wrappers are allowed — keep parameters bound (never concatenated) and comment equivalent SQL shape next to it.


### Use ASSIGN_ID for primary keys, never AUTO

Use `IdType.ASSIGN_ID` so app layer generates Snowflake IDs independent of DB engine — never `IdType.AUTO`. On non-MySQL DBs (e.g., openGauss `BIGSERIAL` differs from MySQL `AUTO_INCREMENT` under JDBC key generation), `AUTO` omits `id` and `INSERT` hits `NOT NULL`, throwing constraint errors far from root cause.

**Wrong:**

```java
@TableId(type = IdType.AUTO) // ❌ coupled to DB auto-increment
private Long id;
```

**Right:**

```java
@TableId(type = IdType.ASSIGN_ID)
private Long id;
```

**Exception** — use `IdType.INPUT` when primary key reuses external business ID:

```java
@TableId(value = "app_id", type = IdType.INPUT)
private Long appId;
```

## 4. Database & Migrations


### Column naming and standard audit columns

- Column names: `snake_case` (`order_no`).
- Primary key: `id`, `BIGINT` or `VARCHAR(32)` matching primary-key strategy.
- Foreign-key columns: `fk_{ref}_id`.
- Booleans: semantic names (`enabled`, `is_default`, `deleted`), `TINYINT(1)` (`0 = false` / `1 = true`).
- Four audit columns: `created_at`, `updated_at`, `created_by`, `updated_by`.
- Soft delete: `deleted TINYINT(1) NOT NULL DEFAULT 0` (`1` = deleted).

Use semantic boolean names; never name columns `flag` or `type` where `flag = 1` loses meaning over time.


### Distributed unique constraints must include the distribution key or use a global index

Distributed DBs (GaussDB Distributed, TiDB, OceanBase) shard rows by distribution key. **Plain unique indexes are shard-local**: if unique column omits distribution key, identical values on different shards insert silently without error.

Choose DDL by whether table is new in this migration:

**New table — inline table constraint (portable across topologies):**

```sql
CREATE TABLE t_authcode_agreement (
    auth_code   VARCHAR(64) NOT NULL,
    ...
    CONSTRAINT uk_authcode_agreement_auth_code UNIQUE (auth_code)
);
```

Distributed engines build a global index automatically; standalone engines build a normal unique constraint — **one SQL file works everywhere** without overlay fork (see `db-migration-base-overlay`).

**Existing table — explicit Global Unique Index (GSI):**

```sql
-- ❌ Shard-local on distributed DBs; duplicates slip in across shards
CREATE UNIQUE INDEX uk_org_name ON t_org(org_name);

-- ✅ Distributed: GSI distributed on the indexed column
CREATE GLOBAL UNIQUE INDEX uk_org_name ON t_org(org_name) DISTRIBUTE BY HASH(org_name);
```

Standalone/centralized engines reject `CREATE GLOBAL UNIQUE INDEX`, so **only this case** forks into topology overlays where centralized overlay uses plain `CREATE UNIQUE INDEX`.

`ALTER TABLE ... ADD UNIQUE` on existing distributed tables carries same distribution-key requirement and does not bypass this rule.


### Index naming with uk_ and idx_ prefixes

- Unique index: `uk_{table}_{field...}`
- Non-unique index: `idx_{table}_{field...}`

Include `{table}` so index names stay unique schema-wide — DBs with schema-scoped index namespaces fail DDL on duplicate names across tables.

```sql
CREATE UNIQUE INDEX uk_user_email ON t_user(email);
CREATE INDEX idx_order_created_at ON t_order(created_at);
```

On new tables, declare uniqueness inline in `CREATE TABLE` via `CONSTRAINT uk_x UNIQUE(...)` rather than adding a separate index afterward — inline constraints keep global-uniqueness semantics across distributed and standalone deployments.


### Use base + overlay for multi-topology databases instead of duplicating full migration sets

When one DB family spans multiple deployment topologies (distributed cluster / centralized primary-standby / standalone) and only a few DDL statements diverge, split migrations into `base + overlay` — **never duplicate full migration trees per topology**. N full copies require N synchronized edits per change; missing one passes locally and fails only when another topology boots.

Two tiers:

| Tier | Contents |
|---|---|
| `<db>-base` | **Shared baseline**: `CREATE TABLE`, seed data, `ALTER`, comments — all DDL valid across topologies |
| `<db>-<topology>` overlay | **Only divergent migrations**, one directory per topology with identical version numbers and names |

**Overlays are mutually exclusive**: active Flyway locations are always `base + one overlay`, never two overlays at build or runtime. Every version number **must appear in at most one active location** — duplicate versions across `base` and overlay abort Flyway startup.

Keep two questions separate:

**1. `base` or `overlay`?** Judge by whether portable syntax exists — not whether distributed concepts appear:

- Portable syntax exists → keep in `base`. Example: inline `CONSTRAINT uk_x UNIQUE(...)` on new table builds global index on distributed DBs and regular constraint on standalone DBs.
- No portable syntax → fork into `overlay`. Example: non-distribution-key unique index on **existing** table needs `CREATE GLOBAL UNIQUE INDEX ... DISTRIBUTE BY HASH(...)` on distributed clusters, rejected on standalone engines.

**2. How many overlays?** One **per deployment target**, even if two targets execute identical SQL today. Question 1 sets `base` vs `overlay` boundary; Question 2 sets overlay granularity.

1-to-1 profile ↔ location parity prevents unverified mental remapping: if `gauss-centralized` secretly serves both centralized GaussDB and standalone openGauss, operators editing `SPRING_FLYWAY_LOCATIONS` guess a mapping nothing checks. One extra overlay file checked via `diff` costs far less than misrouting prod migrations.

> Equivalent overlays may differ in target-product SQL comments, but editing comments on applied migrations alters Flyway checksums — see `db-migration-immutable-after-apply`.

**Wrong (duplicating new table across two overlays):**

```
gauss-distributed/V25__add_authcode_agreement.sql   -- 60-line CREATE TABLE + 3-line GSI
gauss-centralized/V25__add_authcode_agreement.sql   -- 60-line CREATE TABLE + 2-line index
```

60 duplicated DDL lines drift next time a column is added.

**Right (push portable DDL into `base`):**

```
gauss-base/V25__add_authcode_agreement.sql          -- CREATE TABLE with inline CONSTRAINT UNIQUE
```

Keep files in overlays only when syntax diverges, and keep sibling overlays **byte-identical outside divergent DDL and header comments**. Run pairwise `diff` after every overlay edit.

See also `db-migration-parity`, `db-migration-locations-injection`, `db-distributed-unique-index`, `db-migration-immutable-after-apply`.


### Applied migrations are immutable — even comment edits change checksums

Flyway hashes **entire file contents** (comments, blank lines, indentation). Editing an applied migration fails `validate` on next boot — **only in environments that already ran it**: fresh environments migrate clean while existing environments (usually prod) fail to start.

Default rule: **applied migrations are read-only; ship changes as `V<n+1>__fix_xxx.sql`**.

Sole exception: non-functional edits that **do not change executed SQL** (comments, formatting, target-product labels). Do not ship an empty `V<n+1>`; accept checksum change and run `repair` before `migrate` on every environment that already applied that version:

```bash
flyway repair   # rewrites checksums in flyway_schema_history from current file contents
flyway migrate
```

In Spring Boot, use `spring.flyway.repair-on-migrate` or a pre-deploy repair job, and **record the repair step in release notes** — skipping it crashes next rolling deploy long after the edit.

**Never disable validation to bypass checksum errors:**

```yaml
# ❌ Silences real schema drift alongside your comment edit
spring.flyway.validate-on-migrate: false
```

`validate-on-migrate: false` hides manual prod DDL drift and deleted migration files — the exact bugs validation catches. If a legacy project already disabled it, still document `repair` in release notes since no automatic check will warn operators.


### Inject Flyway locations at build time and package all inactive overlays

Inject `spring.flyway.locations` from Maven build profile placeholder instead of hardcoding in `application.yml`:

```xml
<!-- Parent POM: one profile per deployment target, each injecting its own locations -->
<profiles>
  <profile><id>distributed-gaussdb</id>
    <properties><spring.flyway.locations>classpath:db/migration/gauss-base,classpath:db/migration/gauss-distributed</spring.flyway.locations></properties>
  </profile>
  <profile><id>centralized-gaussdb</id>
    <properties><spring.flyway.locations>classpath:db/migration/gauss-base,classpath:db/migration/gauss-centralized</spring.flyway.locations></properties>
  </profile>
  <profile><id>opengauss</id>
    <properties><spring.flyway.locations>classpath:db/migration/gauss-base,classpath:db/migration/gauss-opengauss</spring.flyway.locations></properties>
  </profile>
</profiles>
```

```yaml
# application.yml
spring:
  flyway:
    locations: "@spring.flyway.locations@"
```

**Profile selects *active* locations, not *packaged* files.** Keep all overlay directories under `src/main/resources` so every overlay ships inside JAR classpath regardless of build profile — prerequisite for runtime overrides.

Name profiles after exact deployment targets (`distributed-gaussdb`, `centralized-gaussdb`) rather than generic `gaussdb` so profile IDs match location directories 1-to-1.

**Wrong (excluding inactive overlays from JAR):**

```xml
<!-- ❌ Packages only the build-time active overlay -->
<resources><resource>
  <directory>src/main/resources</directory>
  <excludes><exclude>db/migration/gauss-centralized/**</exclude></excludes>
</resource></resources>
```

Stripping overlays breaks runtime topology switching, forcing a separate untested build per environment.

**Right (package all overlays; override via env var at deploy time):**

```bash
# Override active Flyway locations when an environment's topology differs from the build profile
SPRING_FLYWAY_LOCATIONS=classpath:db/migration/gauss-base,classpath:db/migration/gauss-centralized
```

Example: staging runs centralized primary-standby while prod runs distributed cluster on identical image; `SPRING_FLYWAY_LOCATIONS` switches staging in deployment manifest.


### Keep multi-dialect migrations in lockstep at identical versions

In multi-DB projects, maintain every migration across **every active dialect location** with identical version numbers and names. Missing one dialect stays green locally while Flyway aborts startup or drifts schema in target environment — usually prod.

Invariants:

- Each version number **appears in at most one active location**, else Flyway aborts on duplicate version.
- Sibling dialect files match word-for-word outside SQL dialect differences (sync `CREATE TABLE`, `ALTER`, comments).
- Inject active locations via build profiles; never hardcode in Java/YAML.

**Checklist when adding migration** — confirm every dialect directory has matching file and no active location set collides on version numbers.

When one DB family spans multiple topologies (distributed / centralized / standalone), use `base + overlay` (`db-migration-base-overlay`). Follow project `CLAUDE.md` for exact location hierarchy.


### Three openGauss SQL dialect rules

On Gauss-family DBs (openGauss / GaussDB), rewrite these **unsupported** PostgreSQL constructs:

| Unsupported | Rewrite as |
|---|---|
| `ON CONFLICT` | `INSERT ... SELECT ... WHERE NOT EXISTS`, or explicit deduplication |
| `sys_guid()` / `gen_random_uuid()` | `md5(...)::uuid` |
| `jsonb_build_object` | JSON literal cast: `'[...]'::jsonb` |

**Wrong:**

```sql
INSERT INTO t_config(k, v) VALUES ('a', '1')
ON CONFLICT (k) DO UPDATE SET v = '1'; -- ❌ unsupported on openGauss
```

**Right:**

```sql
INSERT INTO t_config(k, v)
SELECT 'a', '1'
WHERE NOT EXISTS (SELECT 1 FROM t_config WHERE k = 'a');
```

All three come from real migration failures — check before writing SQL rather than debugging broken Flyway runs.


### Register a Flyway plugin on Gauss-family DBs to skip SET ROLE

Flyway treats openGauss / GaussDB as PostgreSQL and runs `SET ROLE '<CURRENT_USER>'` after each step to restore state. Gauss-family DBs deny `SET ROLE` to non-`sysadmin` users (even back to self without `PASSWORD`, SQLState `42602` `set role denied`), aborting Flyway with `Unable to restore connection to its original state` while reading history table — before any migration runs. Never grant `sysadmin`; register a Flyway Plugin SPI that turns role restoration into a no-op.

**Wrong (relying on built-in PostgreSQL support or switching roles in SQL):**

```sql
SET ROLE app_owner PASSWORD '...'; -- ❌ pooled connection retains this role and pollutes later requests
```

**Right (three classes with `flyway-database-postgresql` in `compile` scope):**

```java
// 1. DatabaseType: higher priority than built-in PostgreSQL (0); match product name or fall back to super
public class GaussDBDatabaseType extends PostgreSQLDatabaseType {
    @Override public String getName() { return "GaussDB"; }
    @Override public int getPriority() { return 100; }
    @Override public boolean handlesDatabaseProductNameAndVersion(String name, String ver, Connection c) {
        String n = name == null ? "" : name.toLowerCase(Locale.ROOT);
        return n.contains("gaussdb") || n.contains("opengauss") || super.handlesDatabaseProductNameAndVersion(name, ver, c);
    }
    @Override public Database createDatabase(Configuration cfg, JdbcConnectionFactory f, StatementInterceptor si) {
        return new GaussDBDatabase(cfg, f, si);
    }
}
// 2. Database: swap only the Connection wrapper
public class GaussDBDatabase extends PostgreSQLDatabase {
    // Constructor forwards all three arguments to super
    @Override protected PostgreSQLConnection doGetConnection(Connection c) { return new GaussDBConnection(this, c); }
}
// 3. Connection: make role restoration a no-op
public class GaussDBConnection extends PostgreSQLConnection {
    @Override protected void doRestoreOriginalState() { /* Gauss-family DBs reject SET ROLE; no role to restore */ }
}
```

```text
# META-INF/services/org.flywaydb.core.extensibility.Plugin
com.example.config.GaussDBDatabaseType
```

Key constraints:

- **Match product name, never JDBC URL.** Spring passes Flyway a `DataSource` without URL matching. Official openGauss driver returns `PostgreSQL` from `getDatabaseProductName()`, so matching relies on `priority = 100` + `super.handlesDatabaseProductNameAndVersion(...)` (plain PostgreSQL also hits this type, acceptable in MySQL + Gauss projects).
- **No-op restore is safe** provided migrations never run `SET ROLE`: superclass method only runs `SET ROLE`, while `schema`, `search_path`, and `autocommit` reset on `close()`.
- **Ship plugin in module that runs migrations.** Shared starters/libraries shipping migrations must bundle SPI registration too.
- Plugin imports internal `org.flywaydb.core.internal.*` APIs: comment in code that Flyway upgrades require re-running openGauss migration ITs.


### Table names use t_ prefix, snake_case, and singular nouns

Name domain tables `t_` + `snake_case` + **singular noun**: `t_order`, `t_user`, `t_order_item`. `t_` separates domain tables from views, staging tables, and framework tables; singular nouns match Entity classes 1-to-1 without `t_users` ↔ `UserEntity` mismatch.

Bind every Entity explicitly via `@TableName`, never implicit camel-to-snake conversion:

```java
@Data
@TableName("t_order_item")
public class OrderItemEntity { }
```

## 5. Response Envelopes & Error Codes


### Signal business failures with BizException, never by returning null

Throw `BizException` on business failure — never return `null` for "not found". Returning `null` pushes null-checks onto every caller, where one missed check causes `NullPointerException` and drops failure reason.

**Wrong:**

```java
public UserDetailResponse getById(Long id) {
    UserEntity e = userMapper.selectById(id);
    return e == null ? null : converter.toResponse(e); // ❌
}
```

**Right:**

```java
public UserDetailResponse getById(Long id) {
    UserEntity e = userMapper.selectById(id);
    if (e == null) {
        throw new BizException(ErrorCode.USER_NOT_FOUND);
    }
    return converter.toResponse(e);
}
```

`GlobalExceptionHandler` converts `BizException` into coded `R` envelopes. Return `Optional` only when absence is a normal branch (e.g., optional feature config).


### 6-digit error codes prefixed with the 3-digit HTTP status

Use fixed 6-digit business error codes: first 3 digits mirror HTTP status code, last 3 digits sequence errors within that class. Callers identify failure category without lookup tables, and gateways/logs aggregate by prefix.

**Wrong:**

```java
AUTH_INVALID(1001, "AK 或 SK 校验失败"), // ❌ category is opaque from the number
```

**Right:**

```java
@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    AUTH_INVALID(401001, 401, "AK 或 SK 校验失败"),
    AUTH_EXPIRED(401002, 401, "AK 已过期"),
    NOT_FOUND   (404001, 404, "资源不存在");

    private final int code;
    private final int httpStatus;
    private final String defaultMessage;
}
```

Each enum constant carries default Chinese `defaultMessage` so throw sites never repeat copy.


### Construct response envelopes via static factories only

Construct `R` / `RList` / `RPage` via static factories only — never `new` + setters, which causes `code` drift (`0` vs `200`) and missing `message` fields.

**Wrong:**

```java
R<UserResponse> r = new R<>(); // ❌
r.setCode(0);                  // drifts from factory's 200
r.setData(user);
return r;
```

**Right:**

```java
return R.ok(user);                           // success with payload
return R.ok();                               // success without payload
return R.error(ErrorCode.DUPLICATE_NAME);    // coded failure
throw new BizException(ErrorCode.NOT_FOUND); // wrapped by GlobalExceptionHandler
```

Return `R<T>` directly from Controllers, never `ResponseEntity<R<T>>`. Reserve `ResponseEntity<Resource>` or `void` + `HttpServletResponse` for file downloads and HTTP redirects needing custom status/headers.


### Standard field types across payloads

| Domain | Use | Never use |
|---|---|---|
| Dates & timestamps | `LocalDate` / `LocalDateTime` / `OffsetDateTime` | `java.util.Date` |
| Monetary amounts | `BigDecimal` (fixed scale 2) | `double` / `float` |
| Primary & foreign IDs | `Long` (Snowflake) **or** `String` (UUID) | Mixing both on one entity |
| Enums | `@JsonValue` with explicit wire value | Implicit `name()` |

Why:

- `java.util.Date` conflates instant and timezone while mutable, causing cross-timezone JSON drift; `LocalDateTime` formats as `yyyy-MM-dd HH:mm:ss` via shared Jackson serializer in `commons`.
- Binary floats cannot represent base-10 decimals, causing money rounding drift caught only at reconciliation.
- Mixing `Long` and `String` IDs on one entity breaks uniform client handling and risks JS IEEE-754 precision loss on unquoted 64-bit Snowflake IDs.

**Wrong:**

```java
private Date createdAt;      // ❌
private double amount;       // ❌ loses decimal precision
private Long id;
private String parentId;     // ❌ inconsistent with id type
```

**Right:**

```java
private LocalDateTime createdAt;
private BigDecimal amount;   // scale = 2
private Long id;
private Long parentId;
```


### Choose R, RList, or RPage by payload shape

| Payload shape | Return type |
|---|---|
| Single object | `R<{Name}Response>` |
| Unpaginated list | `RList<{Name}Response>` |
| Paginated list | `RPage<{Name}Response>` |
| Success/failure flag | `R<Boolean>` |
| Empty success | `R<Void>` + `R.ok()` |

Wrong wrapper strips `total` / `pageNo` metadata or forces callers to unwrap extra nesting.

**Wrong:**

```java
public R<List<UserResponse>> page(UserPageQuery q) { // ❌ drops pagination metadata
    return R.ok(userService.page(q).getData());
}
```

**Right:**

```java
public RPage<UserResponse> page(@Valid UserPageQuery q) {
    return RPage.ok(userService.page(q));
}
```

Services return `PageResult<T>` for paginated queries; Controllers wrap via `RPage.ok(...)`.

## 6. DTO Conventions


### Map objects with MapStruct, never manual setters

Map `Entity`, `Dto`, `Request`, and `Response` via MapStruct — never handwritten `setXxx(...)` chains, which compile cleanly when new fields are added and silently drop them at runtime.

Declare one `{Feature}Converter` per feature with `@Mapper(componentModel = "spring")`:

```java
@Mapper(componentModel = "spring")
public interface UserConverter {
    UserDetailResponse toResponse(UserEntity entity);
    List<UserListItemResponse> toListItems(List<UserEntity> entities);
    UserEntity toEntity(UserCreateRequest request);
    void updateEntity(@MappingTarget UserEntity entity, UserUpdateRequest request);
}
```

Declare explicit Converter methods for every conversion shape used — never assemble ad-hoc mappings inside Services.


### Keep Dto internal; split dual-purpose objects

Use `{Name}Dto` only across Services, between internal Service methods, and in MQ payloads. Controllers **neither accept nor return** `Dto` types.

Split any dual-purpose internal/external class into `Dto` + `Response`. Sharing one class means adding an internal field silently widens public HTTP output with zero compile-time warning.

```
Service ←→ Service      use Dto
MQ payload              use Dto
Controller ←→ External  use Request / Response
```


### Paginated queries must extend PageQuery

`{Name}Query` binds `GET` query strings via `@Valid @ModelAttribute`. **Paginated queries must `extends PageQuery`** to inherit `pageNo` / `pageSize` and their bounds (`pageNo >= 1`, `pageSize <= 200`).

Redeclaring pagination fields by hand drops the upper-bound check, letting `pageSize=999999` overload the DB.

**Wrong:**

```java
public class OrderPageQuery {
    private Long pageNo;    // ❌ missing @Min
    private Long pageSize;  // ❌ missing upper bound
}
```

**Right:**

```java
@Data
@Schema(description = "订单分页查询")
public class OrderPageQuery extends PageQuery {
    @Schema(description = "订单编号（模糊查询）")
    private String orderNo;

    @Schema(description = "状态")
    @EnumMatch(enumClass = OrderStatus.class)
    private String status;
}
```

Use plain `{Name}Query` for unpaginated endpoints — never inherit `PageQuery` without pagination.


### Name Requests by action and enforce Jakarta Validation

Name requests `{Name}{Action}Request` — `OrderCreateRequest`, `OrderUpdateRequest`, `OrderCancelRequest`. Avoid catch-all `OrderRequest` unless resource has only one write action: create and update differ in required fields, so sharing one class forces looser constraints on both.

Every constrained field **must** carry Jakarta Validation annotations with Chinese `message` (returned directly to frontend).

**Right:**

```java
@Data
@Schema(description = "创建订单请求")
public class OrderCreateRequest {
    @Schema(description = "产品 ID", example = "1001")
    @NotNull(message = "产品 ID 不能为空")
    private Long productId;

    @Schema(description = "数量", example = "2")
    @NotNull(message = "数量不能为空")
    @Min(value = 1, message = "数量必须大于等于 1")
    @Max(value = 999, message = "数量必须小于等于 999")
    private Integer quantity;
}
```

Handle `MethodArgumentNotValidException` centrally in `GlobalExceptionHandler` — never write manual null/range `if` checks in Controllers.


### Name Responses by view

Name responses after **view / use case**, not entity alone: `OrderDetailResponse`, `OrderListItemResponse`, `OrderCreateResponse`. List and detail views need different field sets; reusing detail class for list rows ships heavy unused fields on every page load.

```java
@Data
@Schema(description = "订单详情响应")
public class OrderDetailResponse {
    @Schema(description = "订单 ID") private Long id;
    @Schema(description = "订单编号") private String orderNo;
}
```

Annotate every field with `@Schema(description = ...)` in Chinese — sole documentation source for Knife4j.

## 7. Naming Conventions


### Class suffix reference table

| Role | Pattern | Example | Package |
|---|---|---|---|
| Entry point | `{Project}Application` | `OrderServerApplication` | root package |
| Controller | `{Name}Controller` | `OrderController` | `controller/` |
| Service interface | `{Name}Service` | `OrderService` | `service/` |
| Service implementation | `{Name}ServiceImpl` | `OrderServiceImpl` | `service/impl/` |
| Mapper | `{Name}Mapper` | `OrderMapper` | `mapper/` |
| Entity | `{Name}Entity` | `OrderEntity` | `entity/` |
| Request body | `{Name}{Action}Request` | `OrderCreateRequest` | `dto/{domain}/` |
| Response body | `{Name}{View}Response` | `OrderDetailResponse` | `dto/{domain}/` |
| Query parameters | `{Name}Query` / `{Name}PageQuery` | `OrderPageQuery` | `dto/{domain}/` |
| Internal DTO | `{Name}Dto` | `OrderSummaryDto` | `dto/{domain}/` |
| Exception | `{Name}Exception` | `OrderLockedException` | `exception/` |
| MapStruct converter | `{Name}Converter` | `OrderConverter` | `converter/` |
| Configuration | `{Name}Config` / `{Name}Properties` | `RedisConfig` | `config/` |
| Enum | Domain noun | `OrderStatus` | `enums/` |
| Constants | `{Name}Constants` | `AuthConstants` | `constants/` |
| Utilities | `{Name}Utils` | `DateUtils` | `utils/` |

`{Name}` = **singular** domain noun (`User`, never `Users`); keep verbs on methods, not class names (never `OrderCreator`). Spell words in full outside standard industry acronyms (`Order`, never `Ord`).


### Controller method names and declaration order

Use fixed **resource-free** CRUD verbs (`create`, never `createUser` — Controller class already names resource):

`page` (paginated) / `list` (full list) / `select` (dropdown options) / `get` / `create` / `update` / `delete` (hard delete) / `remove` (soft delete)

Use `{verb}{Resource}` for non-CRUD domain actions: `cancelProcess`, `resetPassword`.

**Fix declaration order**: all CRUD methods before non-CRUD actions, ordered `page → list → select → get → create → update → delete/remove` so every Controller reads in identical order.

```java
@GetMapping                    public RPage<UserListItemResponse> page(...)
@GetMapping("/all")            public RList<UserListItemResponse> list(...)  // cap max rows to prevent OOM
@GetMapping("/options")        public RList<UserOptionResponse> select()
@GetMapping("/{id}")           public R<UserDetailResponse> get(...)
@PostMapping                   public R<UserCreateResponse> create(...)
@PutMapping("/{id}")           public R<Boolean> update(...)
@DeleteMapping("/{id}")        public R<Boolean> remove(...)
```

Never declare both `delete` and `remove` on one Controller — mixing hard-delete and soft-delete verbs invites wrong deletion calls.


### Enum and constant naming

- Constants: `UPPER_SNAKE_CASE` inside `final` `{Xxx}Constants` class.
- Enum types: `PascalCase`; enum constants: `UPPER_SNAKE_CASE`.

Control wire serialization explicitly via `@JsonValue` (and `@JsonCreator` when needed), never `Enum.name()` — else renaming a Java enum constant breaks HTTP/JSON contracts.

```java
@Getter
@RequiredArgsConstructor
public enum OrderStatus {
    PENDING("pending", "待支付"),
    PAID("paid", "已支付"),
    CANCELLED("cancelled", "已取消");

    private final String value;
    private final String label;

    @JsonValue
    public String getValue() { return value; }
}
```


### Package by technical role first, then by domain under dto

- First-level subpackages by **technical role**: `controller`, `service`, `mapper`, `entity`, `converter`, `config`, `constants`, `enums`, `exception`, `utils`.
- Second-level subpackages by **domain noun** under `dto` only (`dto/order/`, `dto/user/`).

Keep Controllers, Services, and Mappers directly under role root without domain subpackages — one class per domain needs no extra directory depth.

```
com.example.app
├── controller/OrderController.java
├── service/OrderService.java
├── service/impl/OrderServiceImpl.java
├── mapper/OrderMapper.java
├── entity/OrderEntity.java
└── dto/order/OrderCreateRequest.java
```


### Service and Mapper method naming

**Service** — **Include** resource nouns on Service methods so cross-domain call sites stay clear out of context:

- Writes: `create{Name}` / `update{Name}` / `remove{Name}` (soft delete) / `delete{Name}` (hard delete); domain actions: `cancel{Name}` / `approve{Name}`.
- Reads: `getById` / `getBy{Xxx}` (single), `listAll{Name}s` (unpaginated), `list{Name}Options` (dropdown), `list{Name}s` (paginated).
- Return types: `Response`, `Dto`, or primitives — **never** `Entity`.

**Mapper** — Use `MPJBaseMapper` for standard CRUD (`selectById`, `insert`, ...); name custom queries `selectBy{Xxx}` / `listBy{Xxx}` / `countBy{Xxx}` / `existsBy{Xxx}`, and batch writes `insertBatch` / `updateBatchById`.


### Lowercase kebab-case plural URLs

- Lowercase **kebab-case** segments: `/order-items`.
- **Plural** resource nouns: `/orders`, `/users`, `/roles`.
- Single resource: `GET /orders/{id}`; collection: `GET /orders`.
- Non-CRUD actions: `POST /orders/{id}/cancel` — **never** RPC-style verb paths like `/cancelOrder`.

Standard query paths:

| Query shape | Path | Notes |
|---|---|---|
| Paginated | `GET /roles` | Never `/roles/page` |
| Full list | `GET /roles/all` | Cap max rows to prevent OOM |
| Dropdown options | `GET /roles/options` | Return `{id, name}` pairs only |

URLs use plural nouns (resource collections) while Java classes/Entities use singular nouns (single instances).

## 8. Stack Baseline


### Choose the auth framework by project scale and scope

Pick Spring Security or Sa-Token — **one auth framework per project**.

| Project profile | Choice | Decision criteria |
|---|---|---|
| Infra platforms, external IdPs, multi-service medium/large systems | Spring Security | Standard OAuth2 / OIDC / JWT resource servers, security compliance audits, multi-year lifecycle |
| Admin consoles, internal back-office apps, monoliths or small clusters | Sa-Token | Custom login + RBAC needing turnkey kick-out, account ban, mutex login, or step-up auth |

Two tie-breaker questions: **Must auth speak external standard protocols?** (Yes → Spring Security.) **Do session-management features outweigh protocol standards?** (Yes → Sa-Token.)

Why:

- **Spring Security** integrates natively with Spring Cloud Gateway, Spring Authorization Server, and OAuth2 Resource Server — token issuance, propagation, validation, CSRF, session fixation, security headers, password encoders, and CVE patches are maintained by Spring team. Trade-off: high conceptual overhead (`SecurityFilterChain`, `AuthenticationManager`, `AuthorizationManager`, `SecurityContext`), which medium/large platforms amortize easily.
- **Sa-Token** ships back-office session controls as one-line APIs (login checks, forced kick-out, account ban, single-device mutex login, step-up auth, temporary tokens) that require custom plumbing on Spring Security. Trade-off: weak standard-protocol integration once acting as federated identity provider.

Never mount both in one app: overlapping filter chains obscure allow/deny order and turn permission incidents into guesswork.

Apply to new projects and newly extracted services only — never migrate existing services solely for this rule.

See `layer-controller-auth-annotations` for annotation usage.


### Backend stack baseline

| Layer | Choice |
|---|---|
| Runtime & framework | Java 21 + Spring Boot 3.5 + Spring Cloud 2025.0 (or compatible) |
| API Gateway | Spring Cloud Gateway (WebFlux / Netty) |
| ORM | MyBatis-Plus + `mybatis-plus-join`, **no XML mappers** |
| Connection pool | HikariCP |
| Embedded container | Undertow |
| Auth | Spring Security or Sa-Token by project scale — see `stack-auth-framework` |
| API docs | Knife4j (on SpringDoc OpenAPI 3) |
| Object mapping | MapStruct |
| Boilerplate reduction | Lombok |
| Build | Maven 3.8+ with Maven Wrapper |
| Logging | SLF4J + Logback, structured JSON output in prod |

DB/cache versions and multi-dialect targets live in project `CLAUDE.md` — too project-specific to hardcode here.


### Extract multi-line lambdas into named methods

Extract multi-line, nested, or side-effecting lambdas into named methods. In stack traces, lambdas appear only as `lambda$methodName$0` — hiding intent, obscuring failing lines, and shifting numeric suffixes across releases when code moves.

Named methods point stack traces directly at failing step while keeping logic reusable and unit-testable.

**Wrong (exceptions report `lambda$process$0` without revealing which step failed):**

```java
list.stream()
    .map(item -> {
        var dto = new ItemDTO();
        dto.setName(item.getName());
        if (item.getParent() != null) {
            dto.setParentName(item.getParent().getName());
        }
        return dto;
    })
    .toList();
```

**Right (stack trace names `toDTO`, which is reusable and directly testable):**

```java
list.stream()
    .map(this::toDTO)
    .toList();

private ItemDTO toDTO(Item item) {
    var dto = new ItemDTO();
    dto.setName(item.getName());
    if (item.getParent() != null) {
        dto.setParentName(item.getParent().getName());
    }
    return dto;
}
```

**Threshold**: extract anything > 1 line. Keep single-expression lambdas (`x -> x.getId()`, `x -> x > 0`) inline; prefer method references (`Item::getId`) over equivalent lambdas.


### Lombok annotation conventions

| Target | Annotations |
|---|---|
| DTO | `@Data` + `@NoArgsConstructor` |
| Spring bean | `@RequiredArgsConstructor` + `private final` fields for constructor injection |
| Logger | `@Slf4j` (never handwrite `LoggerFactory.getLogger`) |
| Enum fields | `@Getter` |

Use constructor injection, never `@Autowired` field injection: `final` fields enforce immutability and fail fast at startup on missing dependencies instead of throwing `NullPointerException` at runtime.

**Write explicit constructors** in two cases: static utility classes (`private` constructor + `static` methods) and classes with constructor invariant checks — Lombok constructors bypass those checks.


### Maintain a README at the repository root and in every module

In multi-module builds, **maintain `README.md` at repo root and in every submodule**. Root README covers system purpose, capabilities, and module map; submodule README covers what that module owns, exposes, and depends on. **Single-module projects need only root README** with a package-layout section.

Without module READMEs, boundaries are reverse-engineered from `pom.xml` and package trees — mistaking current accidents for intended design until new code lands in wrong modules and erodes dependency direction.

Add `README.md` when creating a module, and update it in the **same commit** whenever public APIs, dependencies, or responsibilities change.

When citing internal Maven/Gradle coordinates in docs, reference parent dependency management or use `${project.version}` / version-catalog placeholders — never hardcode current project version.

**Wrong (code without boundary docs):**

```text
myapp/
├── README.md              ← only says "mvn spring-boot:run"
├── myapp-common/          ← no README; becomes a dumping ground for random helpers
├── myapp-user/            ← no README; unclear whether other modules may depend on it
└── myapp-gateway/         ← no README
```

**Right (self-explanatory at every level):**

```text
myapp/
├── README.md              ← capabilities + module map + getting started
├── myapp-common/
│   └── README.md          ← domain-agnostic utilities only; must never depend on domain modules
├── myapp-user/
│   └── README.md          ← user domain: registration, auth, orgs; expose via UserService only
└── myapp-gateway/
    └── README.md          ← routing, edge auth, rate limiting; zero domain logic
```

Root README minimum sections:

| Section | Content |
|---|---|
| Overview | 1–2 sentences: problem this system solves |
| Capabilities | Main externally visible features |
| Modules | Multi-module: module table with one-line responsibilities linked to module READMEs. Single-module: "Package layout" section |
| Stack | Version baseline for Java, Spring Boot, DB, middleware |
| Getting started | Prerequisites, build/start commands, default port |

Submodule README minimum sections (multi-module builds):

| Section | Content |
|---|---|
| Responsibility | What module owns — **and what explicitly does not belong here** |
| Public surface | Exposed endpoints, Services, extension points, and consumers |
| Dependencies | Internal modules and external middleware depended on, plus why |
| Local commands | Standalone build/run/test commands, where applicable |

`README.md` does not replace `CLAUDE.md`: `README.md` explains capabilities and boundaries to humans; `CLAUDE.md` states locked project decisions for agents. Never duplicate text across both.

