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
| Node arch (team default `linux/arm64`; confirm if different) | `ci-drone-platform-explicit`, `compose-platform-only-when-no-native`, image build platform |
| Base-image & package mirrors (`BASE_REGISTRY`, `NPM_REGISTRY`, `ALPINE_MIRROR`) | `image-base-registry-arg`, `ci-anchor-repeated-values`, `ci-kaniko-image-build` |
| Target registry host + namespace | `ci-anchor-repeated-values` |
| Kaniko settings (`plugins/kaniko:1.13.7`, `skip_tls_verify: true` defaults; confirm overrides & whether semi-offline `tar_path` archive upload is needed) | `ci-kaniko-image-build`, `ci-drone-dag-parallelism` |
| Drone secret names that already exist | `secret-ci-from-store-only`, `ci-drone-annotated-steps` |
| Trigger `ref` + `event` (`refs/heads/master`, `refs/tags/*`, `push`/`tag`, plus `promote` target if any) and tag strategy per env | `ci-explicit-event-scope`, `ci-tag-strategy-single-source`, `deploy-no-latest-in-prod` |
| Environments, namespace, replicas, ingress class (team default `nginx`), host, path, and TLS (default none) per env | `deploy-ingress-nginx`, overlays, values files |
| Image pull policy and pull secret per env | overlays, values files |
| Secret ownership per env (chart/overlay renders it vs ops applies it) | `deploy-config-secret-split`, `deploy-kustomize-helm-parity` |
| Health endpoints and slow-start time | `deploy-three-probes` |
| Runtime UID/GID | `image-nonroot-explicit-uid`, `deploy-securitycontext-match-image` |
| Timezone | `image-tz-explicit` |

## `deploy/README.md`

Sections: **Layout** · **Environments** (table: env · namespace · tag source · pull policy · ingress [class/host/path/TLS] · Secret owner) · **Registries** (target registry + base/package mirrors) · **CI** (`platform`, Kaniko version/TLS overrides, secret names, trigger `ref`/`event`, tag strategy, semi-offline archive if any) · **Parity exceptions** (each `--ignore` with its reason; normally empty) · **Commands** (build, render, deploy per env). Facts only: rationale for generic rules stays in this skill.

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
# <Project> CI Pipeline（Drone CI + kaniko）
# ========================================
# 功能：单 pipeline 并行构建并推送各服务镜像至目标容器仓库。
#   - build-api：后端服务，复用 Dockerfile.backend，通过 MODULE 区分模块。
#   - build-frontend：前端构建，与后端并行。
# 触发条件：推送到 master 或打 tag 时触发。

kind: pipeline
type: docker
name: default

platform:
  os: linux
  arch: arm64                                    # team default; override per deploy/README.md

# 全局变量定义（YAML anchor，供各步骤复用，避免硬编码重复）
global-variables:
  DOCKER_REGISTRY:     &DOCKER_REGISTRY     registry.example.com
  REPO_API:            &REPO_API            registry.example.com/org/app-api
  REPO_FRONTEND:       &REPO_FRONTEND       registry.example.com/org/app-frontend
  DOCKERFILE_BACKEND:  &DOCKERFILE_BACKEND  deploy/docker/Dockerfile.backend
  DOCKERFILE_FRONTEND: &DOCKERFILE_FRONTEND deploy/docker/Dockerfile.frontend
  # tag 策略：push 落 latest（预发），打 tag 落版本号（生产）
  DOCKER_TAG:          &DOCKER_TAG          ${DRONE_TAG:-latest}
  # 基础镜像与包源：CI 构建时走内网镜像源；可选源用 ${VAR:-} 透传 Drone 环境变量
  BASE_REGISTRY_ARG:   &BASE_REGISTRY_ARG   'BASE_REGISTRY=registry.example.com/lib/'
  ALPINE_MIRROR_ARG:   &ALPINE_MIRROR_ARG   'ALPINE_MIRROR=${ALPINE_MIRROR:-}'
  NPM_REGISTRY_ARG:    &NPM_REGISTRY_ARG    'NPM_REGISTRY=https://npm.example.com'
  # kaniko 插件输出文件路径（修复 "open : no such file or directory" 错误）
  DRONE_OUTPUT:        &DRONE_OUTPUT        /tmp/drone-output

trigger:
  ref:
    - refs/heads/master
    - refs/tags/*
  event:
    - push
    - tag

steps:
  # 构建并推送 app-api 镜像（后端 API）；无外部依赖，与其他构建步骤并行。
  # 凭据：Drone secrets registry_username / registry_password。
  - name: build-api
    image: plugins/kaniko:1.13.7
    environment:
      DRONE_OUTPUT: *DRONE_OUTPUT
    settings:
      registry: *DOCKER_REGISTRY
      repo: *REPO_API
      username:
        from_secret: registry_username
      password:
        from_secret: registry_password
      tags:
        - *DOCKER_TAG
      dockerfile: *DOCKERFILE_BACKEND
      context: .
      build_args:
        - *BASE_REGISTRY_ARG
        - MODULE=app-api
      skip_tls_verify: true
    depends_on: [clone]                          # 无聚合步时显式触发 DAG 并行；有下游 depends_on 步时可省略
    when:
      event:
        - push
        - tag

  # 构建并推送 app-frontend 镜像（前端）；与后端步骤并行。
  - name: build-frontend
    image: plugins/kaniko:1.13.7
    environment:
      DRONE_OUTPUT: *DRONE_OUTPUT
    settings:
      registry: *DOCKER_REGISTRY
      repo: *REPO_FRONTEND
      username:
        from_secret: registry_username
      password:
        from_secret: registry_password
      tags:
        - *DOCKER_TAG
      dockerfile: *DOCKERFILE_FRONTEND
      context: .
      build_args:
        - *BASE_REGISTRY_ARG
        - *NPM_REGISTRY_ARG
      skip_tls_verify: true
    depends_on: [clone]
    when:
      event:
        - push
        - tag
```

Optional `.drone.yml` patterns (only when `deploy/README.md` requires):

- **Semi-offline archive upload**: add `tar_path: /drone/src/dist/images/<svc>-${DRONE_TAG:-latest}.tar` on Kaniko steps; wire downstream upload step with `depends_on: [build-api, build-frontend]` and drop `[clone]` on builds (`ci-drone-dag-parallelism`).
- **Non-plugin `commands:` secrets**: inject via `environment.<VAR>: { from_secret: <name> }`, reference `$VAR` in shell (`secret-ci-from-store-only`).
- **`promote` operational step**: add `promote` to top-level `trigger.event`; scope step with `when: { event: [promote], target: [<target>] }`, keep builds `[push, tag]` (`ci-explicit-event-scope`).

```yaml
# deploy/k8s/base/ingress.yaml
# HuaweiCloud CCE: https://support.huaweicloud.com/usermanual-cce/cce_10_0364.html
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  ingressClassName: nginx # nginx ingress
  rules:
    - host: app.example.com             # overridden per env in overlays/<env>/
      http:
        paths:
          - path: /                     # or service prefix (e.g. /api)
            pathType: Prefix
            backend:
              service:
                name: app-frontend
                port:
                  number: 80
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
patches:
  - target:
      kind: Ingress
      name: app-ingress
    patch: |-
      - op: replace
        path: /spec/rules/0/host
        value: uat.example.com
```

```yaml
# deploy/helm/chart/templates/ingress.yaml
# HuaweiCloud CCE: https://support.huaweicloud.com/usermanual-cce/cce_10_0364.html
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: {{ .Values.namespace }}
spec:
  ingressClassName: {{ .Values.ingress.className | default "nginx" }} # nginx ingress
  rules:
    - host: {{ .Values.ingress.host }}
      http:
        paths:
          - path: {{ .Values.ingress.path | default "/" }}
            pathType: Prefix
            backend:
              service:
                name: app-frontend
                port:
                  number: 80
```

```yaml
# deploy/helm/chart/values-uat.yaml — mirrors overlays/uat
namespace: app-uat
image:
  tag: latest
ingress:
  host: uat.example.com
  path: /
```
