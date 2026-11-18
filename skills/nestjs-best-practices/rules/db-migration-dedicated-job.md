---
title: Run migrations in a dedicated one-shot job, not at app bootstrap
impact: HIGH
tags: db, migration, drizzle, deploy, job
---

## Run migrations in a dedicated one-shot job, not at app bootstrap

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
