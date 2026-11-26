# Direct K8s Deploy from Drone CI

Use for Drone CI direct K8s deploy without GitOps (e.g. Argo CD). Requires Drone Runner access to cluster APIServer + container registry.

## Pipeline Topology (Default: 4 Steps)

Keep `.drone.yml` to 4 steps (`build-<svc>...`, `deploy-uat`, `deploy-prod`) so registry keeps `latest` + release tags only:

| Trigger | Steps run | Image tag | Rebuild? |
|---|---|---|---|
| `push` to `refs/heads/master` | `build-*` → `deploy-uat` | `latest` | Yes |
| `tag` on `refs/tags/*` | `build-*` | `${DRONE_TAG}` | Yes |
| `promote` (`target: prod`, `ref: refs/tags/*`) | `deploy-prod` (`depends_on: [clone]`) | `${DRONE_TAG}` | No |

- **Branch-promote trade-off**: Drone `when:` is AND-only per step; `drone/envsubst` omits `${var:+alt}` (`ci-explicit-event-scope`). Need tagless `master` promotes without extra build steps? Push dual tags (`${DRONE_TAG:-latest}` + `sha-${DRONE_COMMIT_SHA:0:8}`) + set registry retention rules to prune old `sha-*` tags.
- **Deploy tool image**: pin `alpine/k8s:<minor>` matching cluster K8s minor (±1) under `global-variables:` (`DEPLOY_IMAGE`, `ci-anchor-repeated-values`). Air-gapped CI: mirror via offline `save`/`load`/`push` preserving `<namespace>/<repo>` + enable public visibility or Runner pull auth (`ci-build-inside-container`).

## Per-Env Config & Secrets (CI Secret `.env` Auto-Split)

Store per-env `.env` as single-line Base64 in CI secret store (`deploy_env_<env>`); skip Git `deploy` branch (repo-wide read leaks secrets, drifts on rollback).

1. **Template (`deploy/k8s/deploy.env.example`)**: match root `.env.example` exact grouping + key order — shared defaults inline, env-specific overlay overrides commented, Secret keys mirrored commented in place + active `CHANGE_ME` entries in dedicated Secret block.
2. **Dynamic allowlist split (`deploy/scripts/ci-deploy.sh`)**:
   - Parse allowed ConfigMap keys from `deploy/k8s/base/configmap.yaml` and required Secret keys from `deploy/k8s/base/secret.example.yaml` at runtime as single source of truth.
   - Render in `umask 077` temp dir with `trap ... EXIT` cleanup; copy `deploy/k8s/{base,overlays}` to satisfy Kustomize root limits without dirtying git.
   - Emit JSON Strategic Merge Patch (`cm-patch.json`) for ConfigMap (avoids `sed` escaping + `configMapGenerator` empty-value fallback) + separate `Secret`.
   - Guardrails: fail fast on unknown keys, leftover `CHANGE_ME`, `kind: Secret` in Kustomize output, namespace mismatch, or `prod` + `latest`; suppress secret echo.
   - Strict POSIX `sh` / BusyBox `awk` (`\047` over `\x27`, `tr -d '\r\n'` on `base64`).
3. **Rollout order & triggers**:
   - Inject `config-sha` + `secret-sha` pod template annotations on backend so config/secret rotation forces rollout; add `commit` + `build` annotations on `:latest` envs.
   - Stage 1: apply `Secret`, `ConfigMap`, `Service`, `Ingress`, backend `Deployment` (incl. migration `initContainer`); wait `kubectl rollout status`.
   - Stage 2: apply frontend `Deployment`; wait `kubectl rollout status`. On failure, print Pod status, Warning events, container tail logs.
4. **Local offline preflight**: expose `--dry-run <env> <env-file> [tag]` taking `.env` directly (skip manual Base64 wrap) to validate rendering + guardrails before storing secrets.

## Namespace-Scoped RBAC & Bastion Script

Isolate credentials per namespace even on shared cluster (`kubeconfig_<env>` per env):

- **Least privilege (`deploy/k8s/rbac/drone-deployer.yaml`)**: namespace-scoped `ServiceAccount`, explicit K8s 1.24+ `kubernetes.io/service-account-token` `Secret`, `Role`, `RoleBinding` — no `ClusterRole`, no `delete` verb, lock `secrets` `get`/`update`/`patch` to `resourceNames: [<app>-secret]` (`create` namespace-scoped).
- **Bastion-portable generator (`deploy/scripts/gen-drone-kubeconfig.sh`)**: runs standalone on jump hosts outside repo — support `-n`/`--namespace`, `-f`/`--rbac-file` (fallback `<script-dir>/` → `./` → repo path), `--skip-apply`, read APIServer from current `kubectl` context by default (optional override arg for internal endpoint). Output single-line Base64 kubeconfig.
- **Direct ops prep**: check cluster via `kubectl version && kubectl cluster-info`; create namespaces via plain `kubectl create namespace <ns>`; verify image pull secret per namespace.

## Done Checks

```bash
sh -n deploy/scripts/ci-deploy.sh deploy/scripts/gen-drone-kubeconfig.sh
sh deploy/scripts/ci-deploy.sh --dry-run uat /tmp/test-uat.env
sh deploy/scripts/ci-deploy.sh --dry-run prod /tmp/test-prod.env v0.1.0
```

Live cluster apply or pushing images = outward-facing: ask first.
