# Delivery

## Environments

| Env | Namespace | Tag source | Pull policy | Secret owner |
|---|---|---|---|---|
| uat | shop-uat | push → `latest` | Always | overlay/chart renders placeholders |
| prod | shop | git tag | IfNotPresent | overlay/chart renders placeholders |

## Registries

- Push: `harbor.example.internal/shop/backend`.

## CI

- Secrets that exist: `harbor_username`, `harbor_password`.

## Parity exceptions

None yet.
