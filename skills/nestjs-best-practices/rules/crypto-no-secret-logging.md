---
title: Never log keys or plaintext
impact: CRITICAL
tags: crypto, logging, pino, redact, oracle
---

## Never log keys or plaintext

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
