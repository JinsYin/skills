---
title: Never hardcode secrets; separate keys by purpose
impact: CRITICAL
impactDescription: Secrets committed to git history cannot be truly erased
tags: crypto, secrets, key-management, rotation
---

## Never hardcode secrets; separate keys by purpose

Load keys and secrets from external config or secret stores — never hardcode private keys, symmetric keys, IVs, nonces, salts, or prod secrets in code. Secrets committed to git history stay permanently compromised even if deleted in later commits.

- **Separate keys by purpose**: distinct keys for encryption, signing, and MAC/integrity so one leaked key cannot compromise all security properties.
- Encode SM2 keys as PEM/DER, SM4 keys as 16 raw bytes.
- Attach `keyId` to payloads whenever ciphertext lifetime outlives key rotation.
- Use Base64 for binary wire transport unless peer protocol mandates hex.

Ciphertexts without `keyId` fail decryption after key rotation — usually discovered on rotation day.
