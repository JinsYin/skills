---
title: Test Services with mocks and HTTP with Supertest
impact: LOW
tags: stack, testing, jest, supertest
---

## Test Services with mocks and HTTP with Supertest

Service unit tests create the Service with a mocked Repository. They do not open a Gauss connection and they do not boot the HTTP stack. HTTP tests use `@nestjs/testing` plus Supertest against the module, with `APP_PIPE` and `APP_GUARD` loaded, and the Repository still mocked or pointed at a disposable database the project `CLAUDE.md` names.

Assert the envelope: status, `code`, and the fields of `data`. A test that only checks HTTP 200 misses a `200` body whose `code` is `500001`.

```ts
await request(app.getHttpServer())
  .post('/api/auth/login')
  .send({ username: 'a', password: 'b' })
  .expect(200);
```

Do not point tests at a shared development database. A migration test, when the project has one, runs the migrator against an empty instance and is allowed to fail on the Gauss denylist.
