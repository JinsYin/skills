---
title: Use only approved ShangMi algorithms and modes
impact: CRITICAL
impactDescription: Weak algorithms or ECB mode create directly exploitable vulnerabilities
tags: crypto, sm2, sm3, sm4, algorithms
---

## Use only approved ShangMi algorithms and modes

| Purpose | Required | Forbidden |
|---|---|---|
| Asymmetric encryption | SM2 `C1C3C2` | `C1C2C3` (isolated legacy adapter only) |
| Digital signature | SM2 + SM3 digest | — |
| Message digest | SM3 | MD5, SHA-1 |
| Symmetric encryption | `SM4/GCM/NoPadding` | **Any `SM4/ECB/*`** |
| Legacy compatibility | `SM4/CBC/PKCS5Padding` | DES, 3DES, RC4 |

ECB encrypts identical plaintext blocks into identical ciphertext blocks, exposing structure directly in ciphertext — zero semantic security regardless of key size.

Use vetted Bouncy Castle primitives; never implement cryptographic primitives by hand.
