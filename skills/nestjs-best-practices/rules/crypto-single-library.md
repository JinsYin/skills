---
title: Use sm-crypto-v2@2 only, behind one CryptoService
impact: CRITICAL
tags: crypto, sm-crypto-v2, dependency, provider
---

## Use sm-crypto-v2@2 only, behind one CryptoService

Depend on `sm-crypto-v2` at an exact `2.0.x` pin (baseline `2.0.1`). All SM2/SM3/SM4 calls go through one injectable `CryptoService`. A second library, or v1 of this library, reintroduces the defaults v2 removed.

| Package | Failure |
|---|---|
| `sm-crypto` (original) | No v2 GCM tag contract; easy to mix modes |
| `sm-crypto-v2@1` | SM2 `hash` defaults off; CBC/GCM still accept an all-zero IV |
| Direct `sm4.encrypt` in a feature Service | Call sites forget `mode` and silently use ECB |

**Right:**

```json
{ "dependencies": { "sm-crypto-v2": "2.0.1" } }
```

```ts
@Injectable()
export class CryptoService {
  encryptSm4Gcm(plain: Uint8Array, keyId: string): Sm4Cipher {
    const key = this.keys.sm4(keyId);
    const iv = randomBytes(12);
    const { output, tag } = sm4.encrypt(plain, key, { mode: 'gcm', iv, output: 'array' });
    return { keyId, iv, tag, output };
  }
}
```

Upgrade the pin only after GCM round-trip and SM2 verify pass against the Java peer.
