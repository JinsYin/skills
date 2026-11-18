---
title: Verify JWTs with pinned algorithm, short lifetime, and external secret
impact: CRITICAL
tags: auth, jwt, token, secret
---

## Verify JWTs with pinned algorithm, short lifetime, and external secret

Verify access tokens with `@nestjs/jwt`. Pin `algorithms` on verify, keep a short `expiresIn`, and load the secret from config. A verifier that does not pin the algorithm will accept a token whose header selects a different algorithm than the one you signed with. `jwt.decode` does not verify the signature.

**Wrong:**

```ts
const payload = this.jwt.decode(token); // ❌ no signature check
// secret hardcoded, no algorithms pin, no expiry
this.jwt.sign(payload, { secret: 'dev-secret' });
```

**Right:**

```ts
JwtModule.registerAsync({
  inject: [authConfig.KEY],
  useFactory: (cfg: ConfigType<typeof authConfig>) => ({
    secret: cfg.accessSecret,
    signOptions: { algorithm: 'HS256', expiresIn: '15m' },
    verifyOptions: { algorithms: ['HS256'] },
  }),
});
```

```ts
const payload = await this.jwt.verifyAsync<AccessTokenPayload>(token);
```

HS256 secret and RS256 private key are different materials; pick one algorithm per service and record it in project `CLAUDE.md`. Never log the token or the secret. Refresh-token rotation, when the project needs it, is a separate stored credential with its own secret and lifetime — not a second copy of the access token.
