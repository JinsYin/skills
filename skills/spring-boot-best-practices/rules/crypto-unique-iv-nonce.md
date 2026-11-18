---
title: Generate a fresh random IV / nonce per encryption
impact: CRITICAL
impactDescription: Reusing a GCM nonce completely breaks encryption and authentication
tags: crypto, sm4, gcm, iv, nonce
---

## Generate a fresh random IV / nonce per encryption

- SM4 key: exact 128 bits / 16 bytes.
- GCM nonce: 96 bits / 12 bytes, **unique per encryption under same key**.
- CBC IV: 16 bytes, generated fresh via `SecureRandom` per call.

GCM nonce reuse lets attackers XOR keystreams and recover GHASH authentication key, forging valid tags on arbitrary ciphertexts.

**Wrong:**

```java
private static final byte[] IV = "1234567890123456".getBytes(); // ❌ static IV
```

**Right:**

```java
byte[] nonce = new byte[12];
SecureRandom.getInstanceStrong().nextBytes(nonce); // fresh per call; transmit alongside ciphertext
```

Never derive keys by truncating or slicing password strings — collapses entropy from 128 bits to password entropy.
