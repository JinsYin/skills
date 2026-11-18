---
title: Generate a fresh random IV / nonce per encryption
impact: CRITICAL
tags: crypto, sm4, gcm, iv, nonce, random
---

## Generate a fresh random IV / nonce per encryption

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
