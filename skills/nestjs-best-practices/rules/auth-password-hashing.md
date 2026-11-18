---
title: Hash passwords with argon2id in the Service layer
impact: CRITICAL
tags: auth, password, argon2, hashing
---

## Hash passwords with argon2id in the Service layer

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
