---
title: Never hardcode secrets; separate keys by purpose
impact: CRITICAL
tags: crypto, secret, key, rotation, config
---

## Never hardcode secrets; separate keys by purpose

Load keys from config or a secret store. A key committed once stays in git history. Use different keys for encryption, signing, and MAC so one leak does not break every property. Attach `keyId` whenever ciphertext outlives a rotation.

**Wrong:**

```ts
const SM4_KEY = '0123456789abcdeffedcba9876543210'; // ❌
```

**Right:**

```ts
sm4Key(keyId: string): Uint8Array {
  const hex = this.config.sm4Keys[keyId];
  if (!hex) throw new BizException(ErrorCode.DECRYPT_FAILED);
  return Buffer.from(hex, 'hex');
}
```

SM2 keys travel as hex or PEM. SM4 keys are 16 raw bytes. Wire encoding for ciphertext is hex or Base64, chosen once per protocol and written down in project `CLAUDE.md`.
