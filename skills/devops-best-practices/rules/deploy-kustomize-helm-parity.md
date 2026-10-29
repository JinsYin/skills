---
title: Kustomize and Helm render the same resources for every environment
impact: CRITICAL
impactDescription: change landing in one track deploys fine there; other track ships without it, failing only in env deployed by that tool
tags: deploy, kustomize, helm, parity
---

## Kustomize and Helm render the same resources for every environment

`deploy/k8s/` (Kustomize) and `deploy/helm/chart/` (Helm) = two renderings of one deployment. Env var, config key or Secret key added to one track deploys fine there; other track ships without it, and Pod fails or silently falls back to default only in envs deployed by that tool.

Map tracks one-to-one:

| Kustomize | Helm |
|---|---|
| `k8s/base/<resource>.yaml` | `helm/chart/templates/<resource>.yaml` |
| `k8s/overlays/<env>/` | `helm/chart/values-<env>.yaml` |
| env set under `overlays/` | env set of `values-*.yaml` |

**Wrong** — key added to one track only:

```yaml
# deploy/k8s/base/configmap.yaml
data:
  TZ: Asia/Shanghai        # helm/chart/templates/configmap.yaml never got it
```

**Right** — same task edits both, then verifies:

```bash
python3 deploy/scripts/k8s-parity.py              # all envs; exit 0 = in parity
python3 deploy/scripts/k8s-parity.py --env uat    # one env
```

Script ships with this skill as `scripts/k8s-parity.py`; copy into project's `deploy/scripts/` so CI and every agent run it. Renders both tracks per env, compares Kind/name sets, ConfigMap and Secret keys (never values), each container's env names and ports.

Change aimed at one track = change to deployment: make both tracks agree. E.g. ops taking over prod Secret → `secrets.create: false` in `values-prod.yaml` **and** `$patch: delete` for that Secret in `overlays/prod/`; else `kubectl apply -k` overwrites real Secret with placeholders.

`--ignore [ENV:]Kind/name` = last resort for difference one tool cannot express; record each with reason under `deploy/README.md` "Parity exceptions".
