---
title: Use gaussdb-nodejs aliased as pg
impact: CRITICAL
impactDescription: Wrong package or a second pg copy compiles cleanly, then fails authentication or splits transactions
tags: db, driver, gaussdb, opengauss, drizzle, pnpm
---

## Use gaussdb-nodejs aliased as pg

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
