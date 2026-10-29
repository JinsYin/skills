#!/usr/bin/env python3
"""Kustomize 与 Helm 双轨一致性校验（rule: deploy-kustomize-helm-parity）。

对每个环境分别渲染 `kubectl kustomize <deploy>/k8s/overlays/<env>` 与
`helm template <deploy>/helm/chart -f values-<env>.yaml`，比较：
  - 资源 Kind/name 集合
  - ConfigMap data 键、Secret data/stringData 键（只比键，永不输出值）
  - 每个工作负载容器的 env 变量名与 containerPort

用法：
  python3 k8s-parity.py [--deploy deploy] [--env uat ...] [--ignore [ENV:]Kind/name ...]
退出码：0 一致；1 存在差异；2 环境或依赖错误。依赖 kubectl、helm、PyYAML。
"""
import argparse
import os
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("k8s-parity: PyYAML missing — run `pip3 install pyyaml`")

WORKLOADS = {"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"}


def render(cmd):
    try:
        out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    except FileNotFoundError:
        sys.exit(f"k8s-parity: `{cmd[0]}` not found on PATH")
    except subprocess.CalledProcessError as e:
        # 渲染失败本身就是不一致：任一轨道跑不通都应阻断
        print(f"render failed: {' '.join(cmd)}\n{e.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return [d for d in yaml.safe_load_all(out) if isinstance(d, dict) and d.get("kind")]


def pod_spec(doc):
    spec = doc.get("spec") or {}
    if doc["kind"] == "CronJob":
        spec = ((spec.get("jobTemplate") or {}).get("spec")) or {}
    return ((spec.get("template") or {}).get("spec")) or {}


def summarize(docs):
    """把渲染结果压成可比较的摘要：{Kind/name: {facet: set}}。"""
    out = {}
    for d in docs:
        key = f"{d['kind']}/{(d.get('metadata') or {}).get('name')}"
        facets = {}
        if d["kind"] == "ConfigMap":
            facets["data keys"] = set((d.get("data") or {}).keys())
        elif d["kind"] == "Secret":
            facets["data keys"] = set((d.get("data") or {}).keys()) | set((d.get("stringData") or {}).keys())
        elif d["kind"] in WORKLOADS:
            for c in pod_spec(d).get("containers") or []:
                facets[f"container {c.get('name')} env"] = {e.get("name") for e in c.get("env") or []}
                facets[f"container {c.get('name')} ports"] = {str(p.get("containerPort")) for p in c.get("ports") or []}
        out[key] = facets
    return out


def ignored(env, key, ignores):
    return key in ignores or f"{env}:{key}" in ignores


def compare(env, k, h, ignores):
    problems = []
    for key in sorted(set(k) | set(h)):
        if ignored(env, key, ignores):
            continue
        if key not in h:
            problems.append(f"{key}: only in kustomize")
            continue
        if key not in k:
            problems.append(f"{key}: only in helm")
            continue
        for facet in sorted(set(k[key]) | set(h[key])):
            a, b = k[key].get(facet, set()), h[key].get(facet, set())
            if a - b:
                problems.append(f"{key} {facet}: only in kustomize {sorted(a - b)}")
            if b - a:
                problems.append(f"{key} {facet}: only in helm {sorted(b - a)}")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--deploy", default="deploy")
    ap.add_argument("--env", action="append", help="limit to these envs (default: all)")
    ap.add_argument("--ignore", action="append", default=[], help="[ENV:]Kind/name, e.g. pre:Secret/app-secret")
    args = ap.parse_args()

    overlays = os.path.join(args.deploy, "k8s", "overlays")
    chart = os.path.join(args.deploy, "helm", "chart")
    if not os.path.isdir(overlays) or not os.path.isfile(os.path.join(chart, "Chart.yaml")):
        sys.exit(f"k8s-parity: need {overlays}/ and {chart}/Chart.yaml")

    k_envs = {e for e in os.listdir(overlays) if os.path.isfile(os.path.join(overlays, e, "kustomization.yaml"))}
    h_envs = {f[len("values-"):-len(".yaml")] for f in os.listdir(chart) if f.startswith("values-") and f.endswith(".yaml")}
    failed = False
    # 环境集合本身也要一致：多出的一侧意味着另一种工具部署不了该环境
    for e in sorted(k_envs ^ h_envs):
        print(f"[{e}] env only in {'kustomize' if e in k_envs else 'helm'}")
        failed = True

    for env in sorted(set(args.env or (k_envs & h_envs))):
        k = summarize(render(["kubectl", "kustomize", os.path.join(overlays, env)]))
        h = summarize(render(["helm", "template", "parity", chart, "-f", os.path.join(chart, f"values-{env}.yaml")]))
        problems = compare(env, k, h, set(args.ignore))
        for p in problems:
            print(f"[{env}] {p}")
        failed |= bool(problems)
        if not problems:
            print(f"[{env}] ok ({len(k)} resources)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
