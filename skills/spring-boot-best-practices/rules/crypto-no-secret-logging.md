---
title: Never log keys or plaintext
impact: CRITICAL
impactDescription: Log stores usually have far broader read access than databases
tags: crypto, logging, secrets, error-handling
---

## Never log keys or plaintext

Log non-sensitive metadata (`keyId`, payload length) only — **never** log plaintext, private keys, symmetric keys, full ciphertexts, full signatures, or decrypted payloads. Logs are centralized, retained long-term, and readable by far more roles than prod databases, widening blast radius.

Treat decryption failure, auth-tag mismatch, malformed ciphertext, and bad signature as **security errors**: return stable opaque business error code without exposing crypto failure details (prevents padding/tag oracles).

**Wrong:**

```java
log.error("Decryption failed, ciphertext={}, key={}", cipherText, keyHex, e); // ❌
```

**Right:**

```java
log.warn("Decryption failed, keyId={}, len={}", keyId, cipherText.length);
throw new BizException(ErrorCode.DECRYPT_FAILED);
```

Tests must cover: SM2 `C1C3C2` round-trip, signature verification pass/fail, SM3 known-answer digests, SM4 nonce uniqueness and tamper detection.
