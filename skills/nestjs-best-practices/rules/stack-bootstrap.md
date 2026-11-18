---
title: Bootstrap prefix, logger, shutdown, and gated Swagger
impact: LOW
tags: stack, bootstrap, swagger, pipe
---

## Bootstrap prefix, logger, shutdown, and gated Swagger

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
