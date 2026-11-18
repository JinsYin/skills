---
title: Sign and hash canonical bytes only
impact: CRITICAL
impactDescription: Signature verification fails randomly across peers
tags: crypto, sm2, sm3, signature, serialization
---

## Sign and hash canonical bytes only

Pass **deterministic byte sequences** to signing and hashing. Signing `Map.toString()`, `Object.toString()`, or JSON without deterministic key order yields different bytes across JVMs or library versions — causing random, hard-to-reproduce verification failures.

**Wrong:**

```java
byte[] data = payload.toString().getBytes(); // ❌ key order and charset unspecified
byte[] sig = signSm2Sm3(privateKey, data);
```

**Right (canonical serialization with fixed field order and UTF-8):**

```java
byte[] canonical = canonicalize(payload); // sorted keys + fixed formatting + explicit UTF-8
byte[] sig = signSm2Sm3(privateKey, canonical);
```

For untrusted external inputs, **verify signature before trusting payload**. Before SM2 decryption, validate `C1` / `C3` / `C2` segment lengths; `C1` requires uncompressed EC point prefix `0x04` unless peer protocol explicitly omits it.

Compare digests in constant time (`MessageDigest.isEqual`), never short-circuiting byte comparisons that leak timing side channels.
