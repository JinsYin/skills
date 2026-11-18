# NestJS Best Practices

> Generated from `rules/` by `scripts/build.sh`. Do not edit by hand.
> Generated at: 2026-11-18 19:14:30

## 1. Layering Discipline


### Controllers must never return Drizzle rows

Return a view `Response` from Controllers and from Services. A Drizzle row is the table: password hash, `deleted`, audit columns. Adding a column later widens the JSON with no compile error if the return type is the row or `any`.

Service methods return `Response`, `Dto`, or primitives — never the row type inferred from `userTable.$inferSelect`.

**Wrong:**

```ts
@Get(':id')
async get(@Param('id', ParseSnowflakePipe) id: bigint) {
  return R.ok(await this.userService.getRow(id)); // ❌ row includes passwordHash
}
```

**Right:**

```ts
@Get(':id')
async get(@Param('id', ParseSnowflakePipe) id: bigint): Promise<R<UserDetailResponse>> {
  return R.ok(await this.userService.getById(id));
}
```


### Cross-module calls go through the exported Service

A feature module exports its Service only. Callers import that module and inject the Service. Exporting a Repository, a Drizzle table, or the database handle lets another module skip validation, cache eviction, and `@Transactional()` rules.

**Wrong:**

```ts
@Module({
  providers: [OrderService, OrderRepository],
  exports: [OrderRepository], // ❌ callers bypass OrderService
})
export class OrderModule {}
```

**Right:**

```ts
@Module({
  providers: [OrderService, OrderRepository],
  exports: [OrderService],
})
export class OrderModule {}
```

```ts
constructor(
  private readonly orderRepository: OrderRepository, // own module
  private readonly userService: UserService,         // other module
) {}
```

Drizzle table objects stay module-private. A join that needs another module's table is a sign the other module should expose a Service method that returns a `Dto`.


### Never use loose types as response payloads

The payload inside `R` / `RList` / `RPage` is a named class, not `any`, `object`, `Record<string, unknown>`, or `Map`. Loose types erase the OpenAPI schema and let a renamed field ship without a compiler error.

**Wrong:**

```ts
@Get('stats')
async stats(): Promise<R<Record<string, unknown>>> {
  return R.ok({ total: 100, active: 80 }); // ❌ invisible contract
}
```

**Right:**

```ts
export class StatsResponse {
  @ApiProperty({ description: '总数' })
  total!: number;

  @ApiProperty({ description: '活跃数' })
  active!: number;
}
```

File downloads return `StreamableFile` and skip the envelope. That is the only untyped payload.


### Never silently swallow errors

A swallowed error becomes HTTP 200 with an empty or partial body. Translate it into `BizException` or rethrow. The same hole is an empty `catch`, `catch` that returns `null`, and a floating promise (`.catch(() => {})` or `void` without handling).

**Wrong:**

```ts
try {
  await this.orderRepository.insert(row);
} catch {
  // ❌ caller assumes the insert succeeded
}
```

**Right:**

```ts
try {
  await this.paymentClient.charge(order);
} catch (err) {
  this.logger.warn({ err, orderId: String(order.id) }, 'Upstream charge failed');
  throw new BizException(ErrorCode.UPSTREAM_UNAVAILABLE);
}
```

A non-critical side channel (metrics, audit best-effort) may catch, and then it must log at `warn` and carry a comment that says why the failure is safe to ignore.


### One-way layered dependencies

`Controller → Service → Repository`: each layer depends only on the adjacent lower layer. Only Repositories touch Drizzle. Reverse or skip-layer calls skip transaction boundaries, validation, and make the use case untestable without a database.

| Layer | Responsibility | Forbidden |
|---|---|---|
| Controller | HTTP contract: routing, binding, auth metadata, envelope | Injecting a Repository, `TransactionHost`, or the Drizzle handle; calling other Controllers |
| Service | Business rules, `@Transactional()` boundaries, orchestration, external calls | HTTP types; another module's Repository |
| Repository | Drizzle queries on this module's tables | Business rules, HTTP, opening its own transaction |

**Wrong (Controller queries Drizzle and skips the Service transaction):**

```ts
@Controller('users')
export class UserController {
  constructor(@Inject(DRIZZLE) private readonly db: AppDatabase) {} // ❌

  @Get(':id')
  async get(@Param('id') id: string) {
    return this.db.select().from(userTable).where(eq(userTable.id, BigInt(id)));
  }
}
```

**Right:**

```ts
@Controller('users')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Get(':id')
  async get(@Param('id', ParseSnowflakePipe) id: bigint): Promise<R<UserDetailResponse>> {
    return R.ok(await this.userService.getById(id));
  }
}
```


### Keep HTTP types out of Services

Services take typed arguments. `Express.Request`, `@Req()`, headers, and status codes stay in the Controller. A Service that reads the request cannot be called from a cron job, a queue worker, or a unit test without spinning up HTTP.

**Wrong:**

```ts
async updateProfile(req: Request) { // ❌
  const userId = (req.user as JwtUser).sub;
}
```

**Right:**

```ts
// Controller
@Patch('profile')
async update(@CurrentUser() user: JwtUser, @Body() body: UserUpdateProfileRequest) {
  return R.ok(await this.userService.updateProfile(user.sub, body));
}

// Service — reusable from HTTP, jobs, and tests
async updateProfile(userId: bigint, body: UserUpdateProfileRequest) { /* ... */ }
```

Read the authenticated principal in the Controller (or a param decorator) and pass `userId` explicitly.

## 2. Authentication & Authorization


### Register auth guards globally and opt out explicitly

Register `JwtAuthGuard` and `PermissionGuard` with `APP_GUARD`. Default is deny. A route is public only when it carries `@Public()`. A route that is not public must carry `@RequirePermissions(...)`. Missing metadata is 401 or 403, not an open route.

`useGlobalGuards()` in `main.ts` does not run under `@nestjs/testing`. `APP_GUARD` does.

| Guard | No `@Public()` | `@Public()` |
|---|---|---|
| `JwtAuthGuard` | Valid access token required, else 401 | Skip |
| `PermissionGuard` | `@RequirePermissions` required, else 403 | Skip |

**Wrong (opt-in guard — the next handler is public):**

```ts
@Controller('users')
export class UserController {
  @Get(':id')
  @UseGuards(JwtAuthGuard) // ❌ sibling methods forget this and stay open
  async get() { /* ... */ }
}
```

**Right:**

```ts
@Module({
  providers: [
    { provide: APP_GUARD, useClass: JwtAuthGuard },
    { provide: APP_GUARD, useClass: PermissionGuard },
  ],
})
export class AuthModule {}

@Controller('users')
export class UserController {
  @Get(':id')
  @RequirePermissions('user:query')
  async get() { /* ... */ }
}

@Controller('auth')
export class AuthController {
  @Post('login')
  @Public()
  async login() { /* ... */ }
}
```

Do not mount a second auth stack (Passport session + a hand-rolled guard). One mechanism, so allow/deny order stays readable.


### Verify JWTs with pinned algorithm, short lifetime, and external secret

Verify access tokens with `@nestjs/jwt`. Pin `algorithms` on verify, keep a short `expiresIn`, and load the secret from config. A verifier that does not pin the algorithm will accept a token whose header selects a different algorithm than the one you signed with. `jwt.decode` does not verify the signature.

**Wrong:**

```ts
const payload = this.jwt.decode(token); // ❌ no signature check
// secret hardcoded, no algorithms pin, no expiry
this.jwt.sign(payload, { secret: 'dev-secret' });
```

**Right:**

```ts
JwtModule.registerAsync({
  inject: [authConfig.KEY],
  useFactory: (cfg: ConfigType<typeof authConfig>) => ({
    secret: cfg.accessSecret,
    signOptions: { algorithm: 'HS256', expiresIn: '15m' },
    verifyOptions: { algorithms: ['HS256'] },
  }),
});
```

```ts
const payload = await this.jwt.verifyAsync<AccessTokenPayload>(token);
```

HS256 secret and RS256 private key are different materials; pick one algorithm per service and record it in project `CLAUDE.md`. Never log the token or the secret. Refresh-token rotation, when the project needs it, is a separate stored credential with its own secret and lifetime — not a second copy of the access token.


### Hash passwords with argon2id in the Service layer

Hash passwords with the `argon2` package, `type: argon2id`, inside the Service. Store only the PHC string. `bcrypt` and SHA-family hashes are out of the baseline. Hashing inside an Entity hook (`@BeforeInsert`) hides the algorithm in the persistence layer and is easy to call with `hashSync` on the request path.

**Wrong:**

```ts
import * as bcrypt from 'bcrypt';
row.passwordHash = bcrypt.hashSync(plain, 10); // ❌ blocks the event loop, weak baseline
```

**Right:**

```ts
import * as argon2 from 'argon2';

const passwordHash = await argon2.hash(plain, { type: argon2.argon2id });
const match = await argon2.verify(passwordHash, plain);
```

Verification failure throws `BizException(ErrorCode.AUTH_INVALID)` with the same message as "unknown user", so the endpoint is not a user-enumeration oracle. Never log `plain` or `passwordHash`.

## 3. Cryptography


### Use only approved ShangMi algorithms and pass every mode explicitly

Use `sm-crypto-v2` and pass every mode flag. Defaults that look safe are not: SM4 with no `mode` is ECB, which encrypts identical blocks to identical ciphertext.

| Purpose | Required | Forbidden |
|---|---|---|
| Asymmetric encryption | SM2 `cipherMode: 1` (`C1C3C2`) | `cipherMode: 0` (`C1C2C3`) except a named legacy adapter |
| Signature | `sm2.doSignature` with `hash: true` and an explicit `userId` | `hash: false` on a raw message |
| Digest | `sm3` | MD5, SHA-1 |
| Symmetric | `sm4` `mode: 'gcm'` plus a fresh 12-byte `iv` | Any call that omits `mode` (ECB), DES, 3DES, RC4 |
| Legacy compatibility | `mode: 'cbc'` with a fresh 16-byte `iv` | Reused or all-zero IV |

```ts
import { sm2, sm3, sm4 } from 'sm-crypto-v2';

sm2.doEncrypt(plain, publicKey, 1); // C1C3C2, explicit even though 1 is the default
sm2.doSignature(message, privateKey, { hash: true, userId, der: wireDer });
sm3(message);
sm4.encrypt(plain, key, { mode: 'gcm', iv, output: 'string' }); // { output, tag }
```

When the peer is the Java stack, fix `der` and `userId` in project `CLAUDE.md` and pass the same values on verify. `userId` defaults to `1234567812345678`; an implicit default drifts the moment one side overrides it.


### Never hardcode secrets; separate keys by purpose

Load keys from config or a secret store. A key committed once stays in git history. Use different keys for encryption, signing, and MAC so one leak does not break every property. Attach `keyId` whenever ciphertext outlives a rotation.

**Wrong:**

```ts
const SM4_KEY = '0123456789abcdeffedcba9876543210'; // ❌
```

**Right:**

```ts
sm4Key(keyId: string): Uint8Array {
  const hex = this.config.sm4Keys[keyId];
  if (!hex) throw new BizException(ErrorCode.DECRYPT_FAILED);
  return Buffer.from(hex, 'hex');
}
```

SM2 keys travel as hex or PEM. SM4 keys are 16 raw bytes. Wire encoding for ciphertext is hex or Base64, chosen once per protocol and written down in project `CLAUDE.md`.


### Never log keys or plaintext

Logs outlive the database grant. Log `keyId` and lengths only. Never log plaintext, keys, full ciphertext, signatures, tokens, or password hashes.

Decryption failure, bad GCM tag, and bad signature are one opaque `BizException`. Distinct messages are an oracle.

**Wrong:**

```ts
this.logger.error({ ciphertext, key }, 'Decrypt failed'); // ❌
```

**Right:**

```ts
this.logger.warn({ keyId, len: ciphertext.length }, 'Decrypt failed');
throw new BizException(ErrorCode.DECRYPT_FAILED);
```

Add those fields to the pino `redact` list anyway (`password`, `passwordHash`, `authorization`, `token`, `key`, `ciphertext`, `iv`, `tag`). Tests cover SM2 `C1C3C2` round-trip, signature pass and fail, an SM3 known answer, and SM4 nonce uniqueness plus a flipped tag.


### Sign canonical bytes and normalize SM2 wire formats

Sign a deterministic byte sequence. `JSON.stringify` follows insertion order, and `String(obj)` is not a contract — either one verifies on the writer and fails on the reader.

Build canonical bytes as UTF-8 of object keys sorted lexicographically, with stable separators, then pass a `Uint8Array` into `doSignature`. Verify that signature before the Service trusts any field. Compare MAC tags with `crypto.timingSafeEqual`, not `===`.

**Wrong:**

```ts
const sig = sm2.doSignature(JSON.stringify(payload), privateKey); // ❌ key order is the caller's accident
```

**Right:**

```ts
const bytes = canonicalUtf8(payload); // sorted keys, fixed separators, UTF-8
const sig = sm2.doSignature(bytes, privateKey, { hash: true, userId, der: wireDer });
const ok = sm2.doVerifySignature(bytes, sig, publicKey, { hash: true, userId, der: wireDer });
```

`der` must match on sign and verify. Mismatch looks like a bad signature and gets debugged as a key bug.


### Use sm-crypto-v2@2 only, behind one CryptoService

Depend on `sm-crypto-v2` at an exact `2.0.x` pin (baseline `2.0.1`). All SM2/SM3/SM4 calls go through one injectable `CryptoService`. A second library, or v1 of this library, reintroduces the defaults v2 removed.

| Package | Failure |
|---|---|
| `sm-crypto` (original) | No v2 GCM tag contract; easy to mix modes |
| `sm-crypto-v2@1` | SM2 `hash` defaults off; CBC/GCM still accept an all-zero IV |
| Direct `sm4.encrypt` in a feature Service | Call sites forget `mode` and silently use ECB |

**Right:**

```json
{ "dependencies": { "sm-crypto-v2": "2.0.1" } }
```

```ts
@Injectable()
export class CryptoService {
  encryptSm4Gcm(plain: Uint8Array, keyId: string): Sm4Cipher {
    const key = this.keys.sm4(keyId);
    const iv = randomBytes(12);
    const { output, tag } = sm4.encrypt(plain, key, { mode: 'gcm', iv, output: 'array' });
    return { keyId, iv, tag, output };
  }
}
```

Upgrade the pin only after GCM round-trip and SM2 verify pass against the Java peer.


### Generate a fresh random IV / nonce per encryption

- SM4 key: 128 bits (16 bytes), or 32 hex chars.
- GCM nonce: 12 bytes, unique per encryption under the same key.
- CBC IV: 16 bytes, fresh per encryption.

GCM nonce reuse lets an attacker forge tags. `sm-crypto-v2@2` throws if GCM or CBC is missing `iv`; it does not throw if you pass a constant. Generate it with `crypto.randomBytes` (or `crypto.getRandomValues`). Persist it next to the ciphertext. Decrypt with the same bytes.

**Wrong:**

```ts
const iv = Buffer.alloc(12); // ❌ all zeros, reused for every row
sm4.encrypt(plain, key, { mode: 'gcm', iv });
```

**Right:**

```ts
const iv = randomBytes(12);
const { output, tag } = sm4.encrypt(plain, key, { mode: 'gcm', iv, output: 'array' });
```

Do not derive a key by slicing a password string. That collapses 128 bits of key into the password's entropy.

## 4. ORM & Persistence


### Fill audit columns in the Repository, not with database defaults

Set `createdAt`, `updatedAt`, `createdBy`, and `updatedBy` in the Repository on every insert and update. A database `ON UPDATE CURRENT_TIMESTAMP` is MySQL-only; on Gauss `updated_at` stays at its insert value. Drizzle `$onUpdate` does not run for a statement that sets columns through a raw fragment and skips the column list, so the Repository assignment is the source of truth.

**Wrong:**

```ts
updatedAt: timestamp('updated_at').default(sql`CURRENT_TIMESTAMP`), // ❌ never moves on UPDATE
```

**Right:**

```ts
createdAt: timestamp('created_at', { mode: 'date', withTimezone: false }).notNull(),
updatedAt: timestamp('updated_at', { mode: 'date', withTimezone: false }).notNull(),
createdBy: bigint('created_by', { mode: 'bigint' }).notNull(),
updatedBy: bigint('updated_by', { mode: 'bigint' }).notNull(),
deleted: boolean('deleted').notNull().default(false),
```

```ts
async insert(values: NewUser, actorId: bigint) {
  const now = new Date();
  await this.txHost.tx.insert(userTable).values({
    ...values,
    createdAt: now,
    updatedAt: now,
    createdBy: actorId,
    updatedBy: actorId,
  });
}
```

`withTimezone: false` matches the Spring `LocalDateTime` contract (no offset). Format it on the wire as `yyyy-MM-dd HH:mm:ss` — see `envelope-field-types`. `deleted` is boolean on Gauss; do not emit MySQL `TINYINT(1)`.


### Snowflake IDs as bigint columns in bigint mode, strings on the wire

Generate primary keys in one `IdGenerator` provider (Snowflake, worker id from config, unique per process). Declare them `bigint('id', { mode: 'bigint' }).primaryKey()`. Do not use `serial`, `bigserial`, `identity`, or `uuid().defaultRandom()` — the last one emits `gen_random_uuid()`, which Gauss does not have (see `db-gauss-dialect`).

Two silent failures:

- `mode: 'number'` rounds values above `Number.MAX_SAFE_INTEGER` (2^53 − 1). Two ids collapse into one row lookup.
- A `bigint` that reaches `JSON.stringify` throws `TypeError: Do not know how to serialize a BigInt`, so the response becomes 500.

Keep `bigint` inside Repository and Service. Every Request, Response, and JWT claim uses a decimal `string`, converted in the Converter. Parse path params with one pipe.

**Wrong:**

```ts
export const userTable = pgTable('t_user', {
  id: serial('id').primaryKey(),
  orgId: bigint('org_id', { mode: 'number' }).notNull(),
});
```

**Right:**

```ts
export const userTable = pgTable('t_user', {
  id: bigint('id', { mode: 'bigint' }).primaryKey(),
  orgId: bigint('org_id', { mode: 'bigint' }).notNull(),
});

await this.txHost.tx.insert(userTable).values({
  id: this.ids.next(),
  ...values,
});

// Converter
id: row.id.toString(),
```

```ts
@Injectable()
export class ParseSnowflakePipe implements PipeTransform<string, bigint> {
  transform(value: string): bigint {
    if (!/^[0-9]{1,19}$/.test(value)) throw new BizException(ErrorCode.BAD_REQUEST);
    return BigInt(value);
  }
}
```

Leave `BigInt.prototype.toJSON` unset so a leaked bigint still throws. An external business key uses the same `bigint` or `varchar` column with no generator — the caller passes it in.


### Build queries with the Drizzle builder, not full-statement SQL

Repository methods use the Drizzle builder (`select` / `insert` / `update` / `delete`, `eq`, `and`, joins). A full SQL string binds one dialect, and a concatenated value is injection. A `sql` fragment is only for a predicate the builder cannot express; every value in it is a bound parameter. Migration files and overlays are SQL on purpose: follow `db-migration-*` and `db-gauss-dialect` there.

**Wrong:**

```ts
await this.txHost.tx.execute(sql.raw(`select * from t_user where name = '${name}'`)); // ❌
```

**Right:**

```ts
await this.txHost.tx
  .select()
  .from(userTable)
  .where(and(eq(userTable.deleted, false), eq(userTable.name, name)));
```

```ts
// Bound fragment when the builder has no operator for it
sql`${userTable.name} ILIKE ${'%' + name + '%'}`;
```

Upsert in the Service, or with `INSERT ... SELECT ... WHERE NOT EXISTS` in a migration. `.onConflictDoUpdate()` and `.onConflictDoNothing()` emit `ON CONFLICT`, which Gauss rejects (`db-gauss-dialect`).


### Run use-case transactions through CLS, and query only via txHost.tx

Open transactions with `@Transactional()` from `@nestjs-cls/transactional` on the Service method. Repositories inject `TransactionHost` and call `txHost.tx` only. A Repository that injects the root Drizzle client ignores the CLS transaction and commits its statement on its own.

Register the plugin once:

```ts
ClsModule.forRoot({
  plugins: [
    new ClsPluginTransactional({
      imports: [DbModule],
      adapter: new TransactionalAdapterDrizzleOrm({ drizzleInstanceToken: DRIZZLE }),
    }),
  ],
}),
```

```ts
type AppTxAdapter = TransactionalAdapterDrizzleOrm<AppDatabase>;

@Injectable()
export class OrderService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly payments: PaymentService,
  ) {}

  @Transactional<AppTxAdapter>()
  async place(input: PlaceOrderDto) {
    const order = await this.orders.insert(input);
    await this.payments.reserve(order.id); // same transaction if it also uses txHost.tx
    return order;
  }
}
```

```ts
constructor(private readonly txHost: TransactionHost<AppTxAdapter>) {}

async insert(input: PlaceOrderDto) {
  return this.txHost.tx.insert(orderTable).values(/* ... */).returning();
}
```

With no transaction active, `txHost.tx` is the root client (adapter behavior since transactional 3). Repositories inject `TransactionHost` only, and they query through `txHost.tx` rather than `db.transaction()`. Nested `@Transactional()` joins the current transaction (default propagation). node-postgres is async: leave `transactionMode` unset.

## 5. Database & Migrations


### Explicit snake_case column names and standard audit columns

Pass the physical column name as the first argument. A casing plugin that derives the name from the property hides a rename inside a refactor.

- Columns: `snake_case` (`order_no`).
- Primary key: `id`, `bigint`, application-generated (see `orm-id-snowflake-bigint`).
- Foreign keys: `fk_{ref}_id`, same `bigint` mode as `id`.
- Booleans: semantic names (`enabled`, `deleted`), Drizzle `boolean`. `deleted = true` means soft-deleted.
- Audit columns: `created_at`, `updated_at`, `created_by`, `updated_by` (see `orm-audit-columns-app-filled`).

```ts
orderNo: varchar('order_no', { length: 32 }).notNull(),
fkUserId: bigint('fk_user_id', { mode: 'bigint' }).notNull(),
```

Do not name a column `flag` or `type` when the value is a boolean or a status. The name has to carry the meaning after the row is read in a log.


### Distributed unique constraints must include the distribution key or use a global index

On distributed GaussDB a plain unique index is shard-local. If the unique columns do not include the distribution key, the same value inserts on two shards and no error is raised.

**New table — inline table constraint (portable, stays in base):**

```ts
export const agreement = pgTable(
  't_authcode_agreement',
  { authCode: varchar('auth_code', { length: 64 }).notNull() },
  (t) => [unique('uk_authcode_agreement_auth_code').on(t.authCode)],
);
```

The generated SQL must contain `CONSTRAINT uk_authcode_agreement_auth_code UNIQUE ("auth_code")` inside `CREATE TABLE`. Distributed Gauss builds a global index from that inline constraint; standalone Gauss builds a normal constraint. One base file, no overlay.

**Existing table — explicit global unique index, overlay only:**

```sql
-- distributed overlay
CREATE GLOBAL UNIQUE INDEX uk_org_name ON t_org(org_name) DISTRIBUTE BY HASH(org_name);

-- centralized / openGauss overlay
CREATE UNIQUE INDEX uk_org_name ON t_org(org_name);
```

`uniqueIndex()` in the Drizzle schema emits a standalone `CREATE UNIQUE INDEX`, which is shard-local on a distributed cluster. Do not use it for a uniqueness rule. `ALTER TABLE ... ADD UNIQUE` on an existing distributed table has the same distribution-key requirement.


### Declare driver and Drizzle only in packages that use them

Declare `pg` (the `gaussdb-nodejs` alias), `drizzle-orm`, and `drizzle-kit` only in the workspace package that opens a pool or runs migrations. Put versions in the pnpm catalog, not copied into every `package.json`. A root dependency is installed for every package and drags the native-less but still Gauss-specific driver into libraries that never talk to a database.

The `pg` override and `peerDependencyRules` stay at the workspace root so a transitive `pg` cannot resolve to upstream `node-postgres` beside the alias (see `db-gauss-driver-selection`).

**Wrong:**

```json
{ "name": "shared-dto", "dependencies": { "drizzle-orm": "0.45.4", "pg": "npm:gaussdb-nodejs@0.2.3" } }
```

**Right:** the API package and the migrator package depend on `drizzle-orm` and `pg`. A shared `libs/contracts` package depends on neither.


### Avoid Drizzle features that emit unsupported Gauss SQL

Gauss-family servers (GaussDB and openGauss) reject three PostgreSQL constructs. Drizzle's PostgreSQL dialect emits the first two from normal APIs. Review every generated migration for them.

| Source | SQL | Rewrite |
|---|---|---|
| `.onConflictDoUpdate()` / `.onConflictDoNothing()` | `ON CONFLICT` | `INSERT ... SELECT ... WHERE NOT EXISTS`, or do the check in the Service |
| `uuid().defaultRandom()` | `gen_random_uuid()` | Application id (`orm-id-snowflake-bigint`) or `md5(...)::uuid` in a reviewed seed |
| Hand-written `jsonb_build_object(...)` | unsupported function | JSON literal cast: `'{"a":1}'::jsonb` |

**Wrong:**

```ts
await tx.insert(configTable).values(row).onConflictDoNothing(); // ❌ ON CONFLICT
```

**Right:**

```sql
INSERT INTO t_config (k, v)
SELECT 'a', '1'
WHERE NOT EXISTS (SELECT 1 FROM t_config WHERE k = 'a');
```

`drizzle-kit` still speaks PostgreSQL. A green generate does not mean the SQL runs on Gauss. Read the new `.sql` file against this table before merging.


### Use gaussdb-nodejs aliased as pg

Connect to GaussDB and openGauss through `gaussdb-nodejs` (Huawei `node-postgres` fork with Gauss SHA256 authentication), installed **under the name `pg`**. `drizzle-orm/node-postgres` imports `pg` and detects pools by class. The alias puts Drizzle, the pool, and any transitive `pg` import on one driver. Import `Pool` from `pg` in application code too — a second import path loads a second copy of the class.

| Need | Declaration | Why |
|---|---|---|
| Driver | `"pg": "npm:gaussdb-nodejs@0.2.3"` (exact) | One module instance |
| Types | `"@types/pg"` (devDependency) | `gaussdb-nodejs` ships no typings |
| Transitive `pg` | Root `pnpm.overrides` pinning the same alias | A library that depends on upstream `pg` reintroduces a driver without Gauss auth |
| Peer range | `pnpm.peerDependencyRules.allowedVersions.pg = "0.2.3"` | `drizzle-orm` declares `pg >= 8`; the fork's version is `0.2.3` and a strict pnpm install fails closed |
| ORM binding | `drizzle-orm/node-postgres` with an explicit `Pool` | `drizzle(connectionString)` builds its own pool and skips pool settings |

**Denylist:**

| Package | Failure |
|---|---|
| Unscoped `gaussdb-node` (≤ 0.2.2) | Did not receive 0.2.3; no `sha256Iterations` |
| `npm install gaussdb-node@0.2.3` | That version is not the fork; the fork is installed only via `npm:gaussdb-nodejs@0.2.3` |
| Upstream `pg` on a Gauss target | No Gauss SHA256 password authentication |
| `postgres` (postgres.js), `drizzle-orm/postgres-js` | No Gauss fork |
| `gaussdb-nodejs` with a caret | `^0.2.3` floats a 0.x driver; bump the pin after auth works on every target |

Upstream README alias `gaussdb-node@npm:gaussdb-nodejs@0.2.3` keeps old import paths. This baseline uses the name `pg`, the module Drizzle loads. Install that one name.

**Right:**

```json
{
  "dependencies": {
    "drizzle-orm": "0.45.4",
    "pg": "npm:gaussdb-nodejs@0.2.3"
  },
  "devDependencies": { "@types/pg": "8.23.1", "drizzle-kit": "0.31.11" },
  "pnpm": {
    "overrides": { "pg": "npm:gaussdb-nodejs@0.2.3" },
    "peerDependencyRules": { "allowedVersions": { "pg": "0.2.3" } }
  }
}
```

```ts
// src/types/pg-augment.d.ts — option missing from @types/pg
import 'pg';
declare module 'pg' {
  interface ClientConfig {
    sha256Iterations?: number | 'server';
  }
}
```

`0.2.3` defaults `sha256Iterations` to `2048`. A server with another `auth_iteration_count` rejects login. Set `'server'` on the pool (`db-gauss-pool-provider`) so the client uses the count in the auth message. Confirm with `SHOW auth_iteration_count` on each target.

Before a new driver pin, connect with the application pool to every target (distributed, centralized, openGauss) and run one parameterized query plus one transaction.

**Sources:** [GaussDB Node driver][] · [GaussDB drivers][] · [gaussdb-nodejs on npm][]

[GaussDB Node driver]: https://github.com/huaweicloud-samples/database-gaussdb-node
[GaussDB drivers]: https://github.com/huaweicloud-samples/database-gaussdb-drivers
[gaussdb-nodejs on npm]: https://www.npmjs.com/package/gaussdb-nodejs


### One pool provider with error listener, timeouts, and shutdown

Create exactly one `Pool` per database in `DbModule`. Expose the pool and the Drizzle instance as `PG_POOL` and `DRIZZLE`. Close the pool on shutdown. Four defaults bite:

| Setting | Default failure | Required |
|---|---|---|
| `pool.on('error')` | An idle client error is an unhandled `'error'` event and **crashes the process** | Log and keep running |
| `connectionTimeoutMillis` | `0` waits forever when the pool is exhausted | e.g. `5000` |
| `sha256Iterations` | Client assumes `2048`; another `auth_iteration_count` rejects login | `'server'` |
| `max` | `10` per process, times replicas | `max × replicas` stays under the database connection limit |

**Wrong:**

```ts
const db = drizzle(process.env.DATABASE_URL!); // ❌ private pool, no error listener, never closed
```

**Right:**

```ts
@Global()
@Module({
  providers: [
    {
      provide: PG_POOL,
      inject: [databaseConfig.KEY],
      useFactory: (cfg: ConfigType<typeof databaseConfig>) => {
        const logger = new Logger('DbModule');
        const pool = new Pool({
          host: cfg.host,
          port: cfg.port,
          user: cfg.user,
          password: cfg.password,
          database: cfg.database,
          max: cfg.poolMax,
          idleTimeoutMillis: 30_000,
          connectionTimeoutMillis: 5_000,
          sha256Iterations: 'server',
        });
        pool.on('error', (err) => logger.error({ err }, 'Idle DB client error'));
        return pool;
      },
    },
    {
      provide: DRIZZLE,
      inject: [PG_POOL],
      useFactory: (pool: Pool) => drizzle(pool, { schema }),
    },
  ],
  exports: [PG_POOL, DRIZZLE],
})
export class DbModule implements OnModuleDestroy {
  constructor(@Inject(PG_POOL) private readonly pool: Pool) {}
  async onModuleDestroy() {
    await this.pool.end();
  }
}
```

`enableShutdownHooks()` in bootstrap calls `onModuleDestroy`. Repositories use `txHost.tx` (`orm-transaction-via-cls`). The pool is created only in `DbModule`.


### Index naming with uk_ and idx_ prefixes

- Unique constraint: `uk_{table}_{field...}` without the `t_` prefix (`uk_user_email`).
- Non-unique index: `idx_{table}_{field...}`.

Include the table so names stay unique in schemas that share one index namespace. A duplicated name fails DDL only on that engine.

```ts
(t) => [
  unique('uk_user_email').on(t.email),
  index('idx_order_created_at').on(t.createdAt),
],
```

Uniqueness on a new table is a `unique()` constraint, not `uniqueIndex()` — see `db-distributed-unique-index`.


### Split multi-topology migrations into generated base plus custom overlays

Drizzle generates one PostgreSQL journal. Topologies (distributed GaussDB, centralized GaussDB, openGauss) share that journal as the **base**. SQL that has no portable form — a global unique index on an existing table — lives in an **overlay**, one directory per target. Do not copy the whole schema into each overlay.

```text
drizzle/                          # drizzle-kit output, portable DDL only
  0007_order.sql
  meta/_journal.json
drizzle/overlay/
  distributed/0007_org_name.sql   # CREATE GLOBAL UNIQUE INDEX ...
  centralized/0007_org_name.sql   # CREATE UNIQUE INDEX ...
  opengauss/0007_org_name.sql
```

The migrator runs base, then exactly one overlay chosen by required config `DB_TOPOLOGY`. No default topology. Overlay files are not listed in `_journal.json` — Drizzle would skip or mis-order them by `when`.

The runner creates `drizzle.__sql_overlays` (`name`, `sha256`) itself (`CREATE TABLE IF NOT EXISTS`) and records each applied overlay file. If the hash of an already applied file changes, the job fails. Do not put that bookkeeping table in a generated migration or an overlay. That is the check Drizzle does not do for base files (`db-migration-immutable-after-apply`).

A version number appears in every overlay or in none. Sibling files match outside the divergent statement and a header comment. Portable DDL (inline `CONSTRAINT uk_... UNIQUE` on a new table) stays in base and does not get an overlay copy.

See `db-distributed-unique-index` for which statement is portable.


### Run migrations in a dedicated one-shot job, not at app bootstrap

Run `migrate()` from `drizzle-orm/node-postgres/migrator` inside a one-shot Nest application context (`NestFactory.createApplicationContext`), then `app.close()`. Deploy that process once, then start API replicas.

Calling `migrate()` from the API `main.ts` starts one migrator per replica. Drizzle applies pending files in a single transaction; overlapping runners deadlock or interleave DDL. A crash during boot then takes the API down with the migration.

```ts
const app = await NestFactory.createApplicationContext(MigratorModule);
try {
  await app.get(MigrationRunner).run();
} finally {
  await app.close();
}
```

`MigrationRunner` uses the same `Pool` settings as the API (`sha256Iterations: 'server'`). It runs the Drizzle base first, then the one overlay selected by config (`db-migration-base-overlay`). The API process has no migrator provider.


### Generate reviewed SQL migrations; never push or synchronize

Change schema by editing the Drizzle table, running `drizzle-kit generate`, and committing the SQL plus `meta/_journal.json` and the snapshot. Review the SQL for the Gauss denylist (`db-gauss-dialect`) before merge.

`drizzle-kit push` alters the live database to match the schema and writes no migration. The next environment does not replay that change, and a dropped column is already gone. There is no runtime `synchronize` flag in this stack; do not add one.

**Wrong:**

```json
{ "scripts": { "db:sync": "drizzle-kit push" } }
```

**Right:**

```json
{ "scripts": { "db:generate": "drizzle-kit generate" } }
```

Apply the committed SQL only from the migrator job (`db-migration-dedicated-job`).


### Applied migrations are immutable — Drizzle will not tell you

Drizzle records `hash` and `created_at` in `drizzle.__drizzle_migrations`, then decides what to run by comparing timestamps only:

```text
if (lastCreatedAt < migration.folderMillis) { execute(sql); insert hash }
```

An edited file whose `when` is already applied is **not** executed again, and the stored hash is **not** checked. Fresh databases run the new text; existing databases keep the old schema. There is no `repair` command. A comment-only edit is already drift.

Applied SQL is read-only. Ship a new generated migration. Do not disable this by deleting rows from `__drizzle_migrations`.

`folderMillis` is the `when` field in `meta/_journal.json`, not the numeric prefix in the filename.


### Regenerate migrations after rebase so journal timestamps stay increasing

The migrator runs a file only when its journal `when` is **strictly greater** than the latest `created_at` already stored. A migration rebased into history with an older `when` is skipped. The API then boots against a schema that is missing those columns, and no error names the skipped file.

After a rebase or a merge that reorders unapplied migrations, regenerate them so every new `when` is greater than the newest timestamp already applied on shared environments. Do not hand-edit `when` backwards to force an order. Do not "fix" a skip by deleting `__drizzle_migrations` rows.

Check before merge: the new journal entries sort after `max(created_at)` from the staging database.


### Table names use t_ prefix, snake_case, and singular nouns

Name domain tables `t_` + `snake_case` + a **singular** noun: `t_order`, `t_user`, `t_order_item`. The prefix separates domain tables from `drizzle.__drizzle_migrations` and from views. Singular names match the module name without a `t_users` / `User` plural mismatch.

Pass the table name explicitly. Do not rely on a global `casing: 'snake_case'` to invent it — renaming the TypeScript binding would rename the physical table on the next generate.

```ts
export const orderItem = pgTable('t_order_item', { /* ... */ });
```

## 6. Response Envelopes & Error Codes


### Signal business failures with BizException, never by returning null

Throw `BizException` when the business rule fails, including "not found". `null` pushes the check onto every caller, and the one that forgets throws a `TypeError` with the reason already lost.

**Wrong:**

```ts
async getById(id: bigint) {
  const row = await this.users.findById(id);
  return row ? this.converter.toDetail(row) : null; // ❌
}
```

**Right:**

```ts
async getById(id: bigint): Promise<UserDetailResponse> {
  const row = await this.users.findById(id);
  if (!row) throw new BizException(ErrorCode.NOT_FOUND);
  return this.converter.toDetail(row);
}
```

Return `null` only when absence is a normal branch the caller is written to handle (optional config). The exception filter turns `BizException` into the envelope (`envelope-factory-only`).


### 6-digit error codes prefixed with the 3-digit HTTP status

Business error codes are 6 digits. The first 3 are the HTTP status; the last 3 sequence errors in that class. Gateways and clients bucket failures by prefix without a lookup table. Each constant carries a default Chinese `message` so throw sites do not invent copy.

**Wrong:**

```ts
AUTH_INVALID = 1001, // ❌ category is not visible in the number
```

**Right:**

```ts
export class ErrorCode {
  static readonly AUTH_INVALID = new ErrorCode(401001, 401, '账号或密码错误');
  static readonly AUTH_EXPIRED = new ErrorCode(401002, 401, '登录已过期');
  static readonly NOT_FOUND = new ErrorCode(404001, 404, '资源不存在');
  static readonly BAD_REQUEST = new ErrorCode(400001, 400, '请求参数错误');

  private constructor(
    readonly code: number,
    readonly httpStatus: number,
    readonly message: string,
  ) {}
}
```

The HTTP status on the response and the prefix of `code` stay equal. A `401001` body with HTTP 200 trains every client to ignore status.


### Construct response envelopes via static factories only

Build `R`, `RList`, and `RPage` only through static factories. A public constructor plus property assignment drifts `code` (`0` vs `200`) and omits `message`. The constructor is `private`.

| Factory | Body |
|---|---|
| `R.ok(data)` | `code` 200, `message` `'OK'`, `data` |
| `R.okEmpty()` | `code` 200, `data` null |
| `RList.ok(items)` | `code` 200, `data` array |
| `RPage.ok(page)` | `code` 200 plus pagination fields |
| `R.error(errorCode)` | `code` from the enum, `message` from the enum, `data` null |

Controllers return the envelope directly. Do not return `HttpException` for a business failure, and do not `@Res()` the Express response to hand-write JSON — that skips the exception filter and the shared serializer.

One `@Catch()` filter maps `BizException` to `R.error` and sets the HTTP status from the error code. Validation failures become `code` `400001` with the Chinese messages joined by `；` into one `message` string, so the field stays a string, same as the Spring contract. Unknown errors become `500001` and a generic message; the stack stays in the log.


### Standard field types across payloads

| Domain | On the wire | In the Service | Never |
|---|---|---|---|
| Timestamps | `string` `yyyy-MM-dd HH:mm:ss` | `Date` (column `withTimezone: false`) | `Date.toISOString()`, a raw `Date` in the response |
| Money | decimal `string` scale 2 (`"12.50"`) | `string` or `Big` | `number` |
| Ids | decimal `string` | `bigint` | `number`, a raw `bigint` in JSON |
| Enums | the declared wire value | the enum | default numeric enum |

`Date.toISOString()` emits a UTC `Z` instant. The Spring side emits `LocalDateTime` with no offset. A shared client then parses two different strings for one column. One serializer in the envelope module formats and parses `yyyy-MM-dd HH:mm:ss`.

`number` cannot hold 64-bit snowflakes or base-10 money. A JSON number that looks right in a small fixture rounds in production. Decimal strings survive both.

One entity uses one id representation. Do not mix `string` and `number` ids on the same resource.


### Choose R, RList, or RPage by payload shape

The JSON envelope matches the Spring backends: `code`, `message`, and `data`. Pagination fields sit on `RPage`, not on a side `meta` object and not on a `success` boolean. Callers branch on `code`.

| Payload | Type |
|---|---|
| One object | `R<NameResponse>` |
| Unpaginated list | `RList<NameResponse>` |
| Paginated list | `RPage<NameResponse>` |
| Flag | `R<boolean>` |
| Empty success | `R<null>` via `R.okEmpty()` |

```ts
export class RPage<T> {
  code!: number;
  message!: string;
  data!: T[];
  total!: number;
  pageNo!: number;
  pageSize!: number;
}
```

**Wrong:**

```ts
return R.ok(page.data); // ❌ drops total / pageNo / pageSize
```

**Right:**

```ts
@Get()
async page(@Query() query: UserPageQuery): Promise<RPage<UserListItemResponse>> {
  return RPage.ok(await this.userService.listUsers(query));
}
```

Services return `PageResult<T>` (`data`, `total`, `pageNo`, `pageSize`). Controllers wrap it with `RPage.ok`. Do not add a response interceptor that wraps a second time — the Controller return value is already the body.

## 7. DTO Conventions


### Map with an explicit Converter return type

One `{Name}Converter` per feature. Each method's return type is the destination class, and the method returns an object literal. TypeScript then errors when a required field is missing. A cast, a rest spread of the row, or `plainToInstance` without `excludeExtraneousValues` copies new columns (including `passwordHash`) the moment they appear on the table.

**Wrong:**

```ts
return row as unknown as UserDetailResponse; // ❌
return { ...row, id: row.id.toString() };    // ❌ extra columns ride along
```

**Right:**

```ts
@Injectable()
export class UserConverter {
  toDetail(row: UserRow): UserDetailResponse {
    return {
      id: row.id.toString(),
      name: row.name,
      createdAt: formatDateTime(row.createdAt),
    };
  }
}
```

Do not map ad hoc inside Services. A new view gets a new method.


### Keep Dto internal; split dual-purpose objects

`{Name}Dto` crosses Services and queue payloads. Controllers do not accept or return it. A class that is both the Service result and the HTTP body grows an internal field (cost price, hash, soft-delete) and the HTTP contract grows with it, with no error at the Controller.

```text
Service ↔ Service     Dto
Queue payload         Dto
Controller ↔ client   Request / Response / Query
```

Split a dual-purpose type into `Dto` plus `Response`. Map between them in the Converter.


### Paginated queries must extend PageQuery

`{Name}PageQuery` binds the query string and `extends PageQuery`. `PageQuery` owns `pageNo` and `pageSize` with `@Min(1)` and `@Max(200)` on `pageSize`. A query that redeclares the fields drops the cap, and `pageSize=999999` reaches the database.

**Wrong:**

```ts
export class OrderPageQuery {
  pageNo!: number;   // ❌ no @Min
  pageSize!: number; // ❌ no upper bound
}
```

**Right:**

```ts
export class PageQuery {
  @Type(() => Number)
  @IsInt()
  @Min(1, { message: '页码必须大于等于 1' })
  pageNo: number = 1;

  @Type(() => Number)
  @IsInt()
  @Min(1, { message: '每页条数必须大于等于 1' })
  @Max(200, { message: '每页条数必须小于等于 200' })
  pageSize: number = 20;
}

export class OrderPageQuery extends PageQuery {
  @IsOptional()
  @IsString()
  orderNo?: string;
}
```

An unpaginated query is `{Name}Query` and does not extend `PageQuery`. The Controller method is `page` vs `list` (`naming-controller-methods`).


### Name Requests by action and enforce class-validator

Name bodies `{Name}{Action}Request`: `OrderCreateRequest`, `OrderUpdateRequest`. Create and update do not share a class — the required fields differ, and a shared class loosens both. Every constrained field has a `class-validator` decorator whose `message` is Chinese. The filter returns that message to the client (`envelope-factory-only`).

**Right:**

```ts
export class OrderCreateRequest {
  @ApiProperty({ description: '产品 ID', example: '1001' })
  @IsNotEmpty({ message: '产品 ID 不能为空' })
  productId!: string;

  @ApiProperty({ description: '数量', example: 2 })
  @IsInt({ message: '数量必须是整数' })
  @Min(1, { message: '数量必须大于等于 1' })
  @Max(999, { message: '数量必须小于等于 999' })
  quantity!: number;
}
```

Register one global pipe. `useGlobalPipes` in `main.ts` does not run in `@nestjs/testing`.

```ts
{ provide: APP_PIPE, useValue: new ValidationPipe({
  whitelist: true,
  forbidNonWhitelisted: true,
  transform: true,
})},
```

`whitelist` strips undeclared fields. `forbidNonWhitelisted` rejects them, so a typo is a 400 instead of a silently dropped update. Do not re-check null and range with `if` in the Controller.


### Name Responses by view

Name responses by view, not by the table: `OrderDetailResponse`, `OrderListItemResponse`, `OrderCreateResponse`. A list row that reuses the detail class ships unused columns on every page.

Every field has `@ApiProperty({ description })` in Chinese. That text is the OpenAPI description. Enable the Nest Swagger CLI plugin so the Controller return type is picked up; the decorator is still required because generics erase the field list.

```ts
export class OrderDetailResponse {
  @ApiProperty({ description: '订单 ID' })
  id!: string;

  @ApiProperty({ description: '订单编号' })
  orderNo!: string;
}
```

## 8. Naming Conventions


### Class suffix and file name reference

| Role | Class | File |
|---|---|---|
| Module | `{Name}Module` | `{name}.module.ts` |
| Controller | `{Name}Controller` | `{name}.controller.ts` |
| Service | `{Name}Service` | `{name}.service.ts` |
| Repository | `{Name}Repository` | `{name}.repository.ts` |
| Drizzle table | `{name}Table` | `{name}.table.ts` |
| Request | `{Name}{Action}Request` | `{name}-{action}.request.ts` |
| Response | `{Name}{View}Response` | `{name}-{view}.response.ts` |
| Query | `{Name}Query` / `{Name}PageQuery` | `{name}.query.ts` / `{name}-page.query.ts` |
| Internal DTO | `{Name}Dto` | `{name}.dto.ts` |
| Converter | `{Name}Converter` | `{name}.converter.ts` |
| Exception | `BizException` or `{Name}Exception` | `{name}.exception.ts` |
| Guard | `{Name}Guard` | `{name}.guard.ts` |
| Config | `{name}Config` | `{name}.config.ts` |

`{Name}` is a singular noun (`User`, not `Users`). Verbs stay on methods (`OrderService.create`, not `OrderCreator`). Spell words in full outside standard acronyms (`Order`, not `Ord`). File names are kebab-case; multi-word modules use `order-item.service.ts` and class `OrderItemService`.


### Controller method names and declaration order

CRUD methods use the resource-free verb. The class name already says which resource.

`page` (paginated) / `list` (full list) / `select` (dropdown) / `get` / `create` / `update` / `delete` (hard delete) / `remove` (soft delete).

Non-CRUD actions use `{verb}{Resource}`: `cancelProcess`, `resetPassword`.

Declare CRUD methods first, in the order `page → list → select → get → create → update → delete/remove`. Do not declare both `delete` and `remove` on one Controller.

```ts
@Get()                 async page(@Query() query: UserPageQuery): Promise<RPage<UserListItemResponse>>
@Get('all')            async list(): Promise<RList<UserListItemResponse>>
@Get('options')        async select(): Promise<RList<UserOptionResponse>>
@Get(':id')            async get(@Param('id', ParseSnowflakePipe) id: bigint): Promise<R<UserDetailResponse>>
@Post()                async create(@Body() body: UserCreateRequest): Promise<R<UserCreateResponse>>
@Put(':id')            async update(...): Promise<R<boolean>>
@Delete(':id')         async remove(...): Promise<R<boolean>>
```

`list` queries cap the row count in the Repository. An unbounded `select()` is an outage.


### Enum wire values are explicit

Persist and serialize an explicit string value, not the TypeScript enum member name and not a numeric enum. Renaming a member must not change JSON or the column.

```ts
export enum OrderStatus {
  Pending = 'pending',
  Paid = 'paid',
  Cancelled = 'cancelled',
}
```

```ts
status: varchar('status', { length: 32 }).notNull().$type<OrderStatus>(),
```

Validate input with `@IsEnum(OrderStatus, { message: '订单状态不合法' })`. A numeric enum (`Pending = 0`) becomes `0` in JSON the moment a decorator is forgotten, and the client cannot tell a new member from a shift.


### One feature module per folder

Nest modules are feature folders, not a global `controllers/` + `services/` split. Each feature owns its Controller, Service, Repository, table, and converter. HTTP types sit in `dto/` inside that folder.

```text
src/order/
  order.module.ts
  order.controller.ts
  order.service.ts
  order.repository.ts
  order.table.ts
  order.converter.ts
  dto/
    order-create.request.ts
    order-detail.response.ts
    order-page.query.ts
```

Shared technical pieces (`R`, `BizException`, `DbModule`, guards, `PageQuery`) live under `src/shared/` or a workspace lib. They do not accumulate feature tables. Cross-feature calls follow `layer-cross-module-via-service`.


### Service and Repository method naming

**Service** methods include the resource noun so a cross-module call reads clearly:

- Writes: `create{Name}` / `update{Name}` / `remove{Name}` (soft) / `delete{Name}` (hard). Domain actions: `cancel{Name}` / `approve{Name}`.
- Reads: `getById` / `getBy{Xxx}` (one), `listAll{Name}s` (unpaginated), `list{Name}Options`, `list{Name}s` (paginated).
- Returns: `Response`, `Dto`, or a primitive. Never a Drizzle row (`layer-controller-no-row`).

**Repository** methods: `findById` / `findBy{Xxx}` (one or null), `listBy{Xxx}`, `countBy{Xxx}`, `existsBy{Xxx}`, `insert`, `updateById`, `insertMany`. A Repository returns rows or a count, not a `Response`.


### Lowercase kebab-case plural URLs

- Segments are lowercase kebab-case: `/order-items`.
- Resource nouns are plural: `/users`, `/orders`.
- One resource: `GET /users/:id`. Collection: `GET /users`.
- Non-CRUD action: `POST /orders/:id/cancel`. Not `/cancelOrder`.

| Query | Path |
|---|---|
| Paginated | `GET /users` |
| Full list | `GET /users/all` |
| Dropdown | `GET /users/options` |

The global prefix (`api`) is set once in bootstrap, not repeated on each `@Controller`. URLs are plural collections; classes and tables stay singular.

## 9. Stack Baseline


### Backend stack baseline

| Layer | Choice |
|---|---|
| Runtime | Node 22 + NestJS 11 (`@nestjs/core` 11.x, `@nestjs/platform-express`) |
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


### Bootstrap prefix, logger, shutdown, and gated Swagger

`main.ts` wires process-wide HTTP concerns once. Guards and the validation pipe are `APP_GUARD` / `APP_PIPE` providers so tests load them too (`auth-global-guard-default-deny`, `dto-request-by-action`).

```ts
const app = await NestFactory.create(AppModule, { bufferLogs: true });
app.useLogger(app.get(Logger));
app.setGlobalPrefix('api');
app.enableShutdownHooks();
await app.listen(port);
```

`bufferLogs` holds messages until pino is attached, so early boot logs are not dropped. `enableShutdownHooks` is what closes the pool.

CORS origins come from config. An open `enableCors()` with a reflected origin is a credentialed cross-site hole; list origins.

Mount Swagger only when config says so (local and staging). Do not expose `/docs` on a production process that has no auth in front of it. The Swagger path is not a `@Public()` API route; it is a separate `SwaggerModule.setup`.


### Validate config with Zod and fail boot

Read environment variables only inside `@nestjs/config` factories. A Zod schema parses them at startup. A missing `DATABASE_HOST` or a non-numeric port crashes the process immediately instead of failing on the first request.

Feature code injects `ConfigType<typeof databaseConfig>`. It does not read `process.env`.

**Wrong:**

```ts
const port = Number(process.env.PORT || 3000); // ❌ scattered defaults, no failure on garbage
```

**Right:**

```ts
export const databaseConfig = registerAs('database', () => {
  const env = databaseEnv.parse(process.env);
  return { host: env.DATABASE_HOST, port: env.DATABASE_PORT, poolMax: env.DATABASE_POOL_MAX };
});

const databaseEnv = z.object({
  DATABASE_HOST: z.string().min(1),
  DATABASE_PORT: z.coerce.number().int().positive(),
  DATABASE_POOL_MAX: z.coerce.number().int().positive().default(10),
}).required();
```

`ConfigModule.forRoot({ isGlobal: true, load: [databaseConfig, authConfig] })` and a bad parse throws during module init. Secrets stay in the environment or a secret store, not in a committed `.env` of real values. Commit `.env.example` with empty placeholders.


### Log with nestjs-pino and a redact list

Use `nestjs-pino` as the Nest logger. Production format is JSON. Call sites use `Logger` from `nestjs-pino` (or Nest `Logger` after `app.useLogger`), not `console.log`.

Redact at the logger so a stray `log(body)` cannot persist secrets. Cover at least `req.headers.authorization`, `req.body.password`, `password`, `passwordHash`, `token`, `accessToken`, `refreshToken`, `key`, `ciphertext`, `iv`, `tag`.

```ts
LoggerModule.forRoot({
  pinoHttp: {
    redact: ['req.headers.authorization', 'req.body.password', 'password', 'passwordHash', 'token'],
  },
});
```

Log ids as decimal strings. A `bigint` in a pino object throws or becomes `{}` depending on the serializer, and the request that hit the bug is the one whose log you needed.


### Maintain a README at the repository root and in every package

A pnpm workspace has a root `README.md` and one `README.md` per package. The root README says what the system does, lists packages, records the stack line from `stack-baseline`, and shows `pnpm` install / dev / test / migrate commands. A package README says what that package owns, what it must not contain, and what it exports.

A single-package app has only the root README, with a "Package layout" section that matches `naming-module-layout`.

Update the README in the same change as a new package, a new public provider, or a new script. When a doc mentions a version, point at the catalog or `stack-baseline`, not a second hardcoded number.

`README.md` is for people. Project `CLAUDE.md` locks decisions for agents (topology, JWT algorithm, worker-id scheme). Do not paste these rules into `CLAUDE.md`.


### Test Services with mocks and HTTP with Supertest

Service unit tests create the Service with a mocked Repository. They do not open a Gauss connection and they do not boot the HTTP stack. HTTP tests use `@nestjs/testing` plus Supertest against the module, with `APP_PIPE` and `APP_GUARD` loaded, and the Repository still mocked or pointed at a disposable database the project `CLAUDE.md` names.

Assert the envelope: status, `code`, and the fields of `data`. A test that only checks HTTP 200 misses a `200` body whose `code` is `500001`.

```ts
await request(app.getHttpServer())
  .post('/api/auth/login')
  .send({ username: 'a', password: 'b' })
  .expect(200);
```

Do not point tests at a shared development database. A migration test, when the project has one, runs the migrator against an empty instance and is allowed to fail on the Gauss denylist.

