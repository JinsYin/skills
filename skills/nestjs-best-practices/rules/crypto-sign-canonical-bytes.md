---
title: Sign canonical bytes and normalize SM2 wire formats
impact: CRITICAL
tags: crypto, sm2, signature, canonical, interop
---

## Sign canonical bytes and normalize SM2 wire formats

Sign a deterministic byte sequence. `JSON.stringify` follows insertion order, and `String(obj)` is not a contract — either one verifies on the writer and fails on the reader.

Build canonical bytes as UTF-8 of object keys sorted lexicographically, with stable separators, then pass a `Uint8Array` into `doSignature`. Verify that signature before the Service trusts any field. Compare MAC tags with `crypto.timingSafeEqual`, not `===`.

**Wrong:**

```ts
const sig = sm2.doSignature(JSON.stringify(payload), privateKey); // ❌ key order is the caller's accident
```

**Right:**

```ts
const bytes = canonicalUtf8(payload); // sorted keys, fixed separators, UTF-8
const sig = sm2.doSignature(bytes, privateKey, { hash: true, userId, der: wireDer });
const ok = sm2.doVerifySignature(bytes, sig, publicKey, { hash: true, userId, der: wireDer });
```

`der` must match on sign and verify. Mismatch looks like a bad signature and gets debugged as a key bug.
