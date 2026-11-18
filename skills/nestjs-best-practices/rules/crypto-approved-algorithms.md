---
title: Use only approved ShangMi algorithms and pass every mode explicitly
impact: CRITICAL
impactDescription: Omitting sm4 mode silently encrypts with ECB
tags: crypto, sm2, sm3, sm4, gcm, ecb
---

## Use only approved ShangMi algorithms and pass every mode explicitly

Use `sm-crypto-v2` and pass every mode flag. Defaults that look safe are not: SM4 with no `mode` is ECB, which encrypts identical blocks to identical ciphertext.

| Purpose | Required | Forbidden |
|---|---|---|
| Asymmetric encryption | SM2 `cipherMode: 1` (`C1C3C2`) | `cipherMode: 0` (`C1C2C3`) except a named legacy adapter |
| Signature | `sm2.doSignature` with `hash: true` and an explicit `userId` | `hash: false` on a raw message |
| Digest | `sm3` | MD5, SHA-1 |
| Symmetric | `sm4` `mode: 'gcm'` plus a fresh 12-byte `iv` | Any call that omits `mode` (ECB), DES, 3DES, RC4 |
| Legacy compatibility | `mode: 'cbc'` with a fresh 16-byte `iv` | Reused or all-zero IV |

```ts
import { sm2, sm3, sm4 } from 'sm-crypto-v2';

sm2.doEncrypt(plain, publicKey, 1); // C1C3C2, explicit even though 1 is the default
sm2.doSignature(message, privateKey, { hash: true, userId, der: wireDer });
sm3(message);
sm4.encrypt(plain, key, { mode: 'gcm', iv, output: 'string' }); // { output, tag }
```

When the peer is the Java stack, fix `der` and `userId` in project `CLAUDE.md` and pass the same values on verify. `userId` defaults to `1234567812345678`; an implicit default drifts the moment one side overrides it.
