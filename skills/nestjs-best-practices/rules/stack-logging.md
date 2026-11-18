---
title: Log with nestjs-pino and a redact list
impact: LOW
tags: stack, logging, pino
---

## Log with nestjs-pino and a redact list

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
