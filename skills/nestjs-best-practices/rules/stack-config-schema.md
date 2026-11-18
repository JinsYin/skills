---
title: Validate config with Zod and fail boot
impact: LOW
tags: stack, config, zod
---

## Validate config with Zod and fail boot

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
