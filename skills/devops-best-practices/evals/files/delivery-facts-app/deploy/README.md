# Delivery

## Layout

`deploy/docker/Dockerfile.<role>`, `deploy/k8s/{base,overlays/<env>}`, `deploy/helm/chart` (`values-<env>.yaml`), root `.drone.yml`.

## Environments

| Env | Namespace | Tag source | Pull policy | Ingress | Secret owner |
|---|---|---|---|---|---|
| uat | shop-uat | push → `latest` | Always (secret `regcred`) | shop-uat.example.internal | chart/overlay renders placeholders |
| prod | shop | git tag → `${DRONE_TAG}` | IfNotPresent (secret `regcred`) | shop.example.internal (TLS secret `shop-tls`) | ops applies `shop-secret` |

## Registries

- Push: `harbor.example.internal/shop/<role>` (roles: `backend`, `frontend`).
- Base images: `harbor.example.internal/mirror` (no Docker Hub from CI or nodes).

## CI

- Drone, nodes `arm64`, no docker.sock: build images with `plugins/kaniko`.
- Secrets that exist (do not create others): `harbor_username`, `harbor_password`.
- Events: build on `push` to `main` and on `tag`.

## Runtime

- Backend runs as UID/GID 10001, `TZ=Asia/Shanghai`, slow start ~60s.

## Parity exceptions

None yet.
