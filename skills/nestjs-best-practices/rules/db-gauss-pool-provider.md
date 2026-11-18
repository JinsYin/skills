---
title: One pool provider with error listener, timeouts, and shutdown
impact: CRITICAL
impactDescription: Missing pool error listener crashes the process on the first DB restart
tags: db, pool, gaussdb, drizzle, shutdown, provider
---

## One pool provider with error listener, timeouts, and shutdown

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
