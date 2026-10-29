# Delivery Chain

Delivery chain = `deploy/docker/Dockerfile.<role>`, root `.drone.yml`, `deploy/k8s/` (Kustomize) and `deploy/helm/chart/` (Helm), both always present and in parity (rule `deploy-kustomize-helm-parity`). Runs as own unit of work: GSD phase, Superpowers phase, Matt spec.

## Layout

```
.drone.yml
deploy/
  README.md                 # delivery facts — the single source agents read
  docker/Dockerfile.<role>  # one per role (backend, frontend…); modules sharing a role use a build arg
  k8s/base/                 # one file per workload + configmap.yaml + secret.example.yaml + ingress.yaml
  k8s/overlays/<env>/       # diff only (rule deploy-base-overlay-diff-only)
  helm/chart/               # templates/ mirror k8s/base; values-<env>.yaml mirror overlays/<env>
  scripts/k8s-parity.py     # copied from this skill
```

## Order

1. **Interview**; tell user answers get recorded in `deploy/README.md`, then write it. Unanswered fact → stop and ask.
2. **Pipeline skeleton**: first deployable module end to end — Dockerfile, Drone build/push step, Kustomize base + every overlay, Helm template + every values file, parity green.
3. **One module per plan/ticket** after that, each end to end.

## Interview

| Fact | Drives |
|---|---|
| Deployable modules, their role, shared-Dockerfile build arg | `image-copy-artifact-exact-name`, layout |
| Node arch (amd64/arm64) | `compose-platform-only-when-no-native`, image build platform |
| Base-image registry/mirror | `image-base-registry-arg` |
| Target registry host + namespace | `ci-anchor-repeated-values` |
| CI build mechanism (docker plugin, kaniko, docker.sock?) and its quirks | `ci-build-inside-container` |
| Drone secret names that already exist | `secret-ci-from-store-only` |
| Trigger events/branches and tag strategy per env | `ci-explicit-event-scope`, `ci-tag-strategy-single-source`, `deploy-no-latest-in-prod` |
| Environments, namespace, replicas, ingress host/TLS per env | overlays, values files |
| Image pull policy and pull secret per env | overlays, values files |
| Secret ownership per env (chart/overlay renders it vs ops applies it) | `deploy-config-secret-split`, `deploy-kustomize-helm-parity` |
| Health endpoints and slow-start time | `deploy-three-probes` |
| Runtime UID/GID | `image-nonroot-explicit-uid`, `deploy-securitycontext-match-image` |
| Timezone | `image-tz-explicit` |

## `deploy/README.md`

Sections: **Layout** · **Environments** (table: env · namespace · tag source · pull policy · ingress · Secret owner) · **Registries** · **CI** (build mechanism, secret names, events, tag strategy, quirks) · **Parity exceptions** (each `--ignore` with its reason; normally empty) · **Commands** (build, render, deploy per env). Facts only: rationale for generic rules stays in this skill.

## Keep In Sync

Once any delivery file exists, task making change updates every existing file it touches, in same task:

| Change | Also update |
|---|---|
| New deployable module | Dockerfile role/build arg, Drone step, k8s base + overlays, Helm template + values, compose/process-compose |
| New port | Dockerfile `EXPOSE`, Service in both tracks, probes, process-compose |
| New env var / config key | ConfigMap in both tracks (+ per-env values), `.env.example` |
| New secret | Secret in both tracks (placeholders only), `.env.example`, Drone `from_secret` if CI needs it, `deploy/README.md` |
| New dependency service | docker-compose.yml, ConfigMap host/port keys in both tracks |

## Done Checks

```bash
docker build -f deploy/docker/Dockerfile.<role> .        # each touched role
kubectl kustomize deploy/k8s/overlays/<env> >/dev/null   # each env
helm lint deploy/helm/chart -f deploy/helm/chart/values-<env>.yaml
python3 deploy/scripts/k8s-parity.py                      # exit 0
```

Applying to real cluster or pushing images = outward-facing: ask first.

## Skeletons

```yaml
# .drone.yml
kind: pipeline
type: docker
name: build

x-registry: &registry registry.example.com   # from deploy/README.md; one place to change (rule ci-anchor-repeated-values)

steps:
  - name: image-backend
    image: plugins/docker:20
    settings:
      registry: *registry
      repo: registry.example.com/team/backend
      dockerfile: deploy/docker/Dockerfile.backend
      build_args: [MODULE=api]
      tags: ["${DRONE_TAG:-latest}"]
      username: { from_secret: registry_username }
      password: { from_secret: registry_password }
    when:
      event: [push, tag]
```

```yaml
# deploy/k8s/overlays/uat/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: [../../base]
namespace: app-uat
images:
  - name: registry.example.com/team/backend
    newTag: latest
```

```yaml
# deploy/helm/chart/values-uat.yaml — mirrors overlays/uat
namespace: app-uat
image:
  tag: latest
```
