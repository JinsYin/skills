---
title: Standardize Kubernetes Ingress on networking.k8s.io/v1 with Nginx ingressClassName
impact: CRITICAL
impactDescription: Legacy Ingress API or kubernetes.io/ingress.class annotation fails apply or routes to wrong controller (CCE ELB instead of Nginx); unrequested spec.tls breaks HTTP when TLS Secret missing
tags: deploy, k8s, ingress, nginx, cce, kustomize, helm
---

## Standardize Kubernetes Ingress on networking.k8s.io/v1 with Nginx ingressClassName

Write Kubernetes Ingress manifests with `networking.k8s.io/v1` and `spec.ingressClassName: nginx` (HuaweiCloud CCE reference: https://support.huaweicloud.com/usermanual-cce/cce_10_0364.html). Omitting `spec.ingressClassName` or using legacy `kubernetes.io/ingress.class` annotation fails on newer clusters or lets CCE provision default ELB Ingress instead of Nginx, leaving routes unreachable even after `kubectl apply` succeeds.

**Required fields and defaults:**

- **Header comment** — put `# HuaweiCloud CCE: https://support.huaweicloud.com/usermanual-cce/cce_10_0364.html` at top of every generated `ingress.yaml`.
- **API and class** — `apiVersion: networking.k8s.io/v1`, `kind: Ingress`, `spec.ingressClassName: nginx` (team default; override only per `deploy/README.md`). Replace legacy `kubernetes.io/ingress.class` annotation with `spec.ingressClassName`.
- **HTTP-only default** — omit `spec.tls` (TLS terminates upstream or stays internal); add `spec.tls` only when `deploy/README.md` requires in-cluster TLS.
- **Rules and backend** — set explicit `host`, `<path>`, `pathType: Prefix` (or `Exact` when needed), and numeric `backend.service.port.number` matching target Service `port`.
- **Kustomize and Helm dual-track** — omit env `metadata.namespace` in `k8s/base/ingress.yaml` (`overlays/<env>/kustomization.yaml` injects `namespace:`) and patch per-env `host` in overlays (`deploy-base-overlay-diff-only`); render `metadata.namespace` and `spec.rules` from `values-<env>.yaml` in Helm (`deploy-kustomize-helm-parity`).

**Wrong** — legacy annotation, unrequested `spec.tls`, hardcoded env namespace in Kustomize base:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: app-prod                       # hardcoded in k8s/base; breaks overlay reuse
  annotations:
    kubernetes.io/ingress.class: "nginx"    # deprecated; use spec.ingressClassName
spec:
  tls:                                      # unrequested TLS; breaks HTTP if Secret missing
    - hosts: [app.example.com]
      secretName: app-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app-frontend
                port:
                  number: 80
```

**Right** — rendered Ingress shape (Kustomize overlay and Helm template outputs match):

```yaml
# HuaweiCloud CCE: https://support.huaweicloud.com/usermanual-cce/cce_10_0364.html
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: <name>
  namespace: <namespace>
spec:
  ingressClassName: nginx # nginx ingress
  rules:
    - host: <host>
      http:
        paths:
          - path: <path>
            pathType: Prefix
            backend:
              service:
                name: <service_name>
                port:
                  number: <service_port>
```

Kustomize base, overlay patch, and Helm template skeletons: see `references/delivery.md`.
