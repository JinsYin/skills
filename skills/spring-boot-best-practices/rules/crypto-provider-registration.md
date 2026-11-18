---
title: Register BouncyCastle Provider once at startup
impact: HIGH
tags: crypto, bouncycastle, provider, startup
---

## Register BouncyCastle Provider once at startup

Use `org.bouncycastle:bcprov-jdk18on` and register once at app startup — never inside per-request encrypt/decrypt calls. `Security.addProvider` takes global synchronization locks and bottlenecks hot paths.

**Right:**

```java
@Configuration
public class CryptoConfig {
    @PostConstruct
    public void registerProvider() {
        if (Security.getProvider(BouncyCastleProvider.PROVIDER_NAME) == null) {
            Security.addProvider(new BouncyCastleProvider());
        }
    }
}
```

If module already uses another compliant JCE provider, keep that single provider; never mount two.
