#!/usr/bin/env python3
"""Compact agent session transcripts into retrospective evidence.

  transcript.py digest [--runtime RT] [--cwd DIR] [ID|PATH ...]  # signal digest; default = newest session
  transcript.py meta   [--runtime RT] [--cwd DIR] [ID|PATH ...]  # session id/name, runtime, most-used and last model/effort

RT = claude | codex | cursor | agy | auto (default: Claude Code if detected, else the
newest session of cwd across runtimes). Each runtime's storage is read by an adapter
in runtimes/; see their docstrings for paths.
Output is deliberately small: raw transcripts are huge, the digest keeps only
what a retrospective needs (prompts, skill loads, errors, corrections, retries).
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runtimes import RUNTIMES, sessions  # noqa: E402
from runtimes.common import clip  # noqa: E402

BIG_RESULT = 20_000  # 单个工具结果字符数阈值，超过视为可能浪费上下文
HEAVY_AGENT = 200_000  # 子 Agent Token 阈值
HEAVY_SKILL = 0.25  # skill 占全会话 Token 或耗时的比例阈值

# 用户纠正/否定的常见措辞（中英），只作为候选提示，最终由模型判断
CORRECTION = re.compile(
    r"(^|\b)(no|nope|wrong|actually|instead|don'?t|stop|again|not what|why did you|revert|undo)\b"
    r"|不对|不是|错了|应该|别|不要|重新|又|还是|怎么没|没有按|回滚|撤销",
    re.I,
)


def skill_name(path):
    p = path.rstrip("/")
    return os.path.basename(os.path.dirname(p) if p.endswith("SKILL.md") else p).split(":")[-1]


def meta_line(s):
    m = s.meta()
    most = m["pairs"].most_common(1)[0][0] if m["pairs"] else "unknown"
    return (f"session={s.id} name={m['name'] or '-'} "
            f"runtime={m['runtime']} most={most} last={m['last'] or 'unknown'}")


def digest(s):
    print(f"## {meta_line(s)}")
    tools = {}  # tool call id -> (name, short input)
    calls = collections.Counter()
    errors = collections.Counter()
    turn = 0
    # 按用户轮次累计开销
    cost = collections.defaultdict(lambda: {"in": 0, "out": 0, "calls": 0, "ms": 0, "skills": set(), "manual": set(), "prompt": "",
                                         "compact": 0, "peak": 0, "res": 0})
    peak, span, has_usage = 0, {}, False
    pend = None  # 记录的 tick 先于其事件发出：暂存，等看清是否新一轮提问再记，免得把两轮间的空闲算进上一轮

    def stamp(t):
        # 每轮耗时 = 该轮首末记录的时间差
        if t:
            a, _ = span.get(turn, (t, t))
            span[turn] = (a, t)

    for e in s.events():
        k, ts = e["k"], e.get("ts")
        if k == "tick":
            stamp(pend)
            pend = ts
            continue
        if k == "user":
            turn += 1
        stamp(pend)
        stamp(ts)
        pend = None
        if k == "usage":
            has_usage = True
            cost[turn]["in"] += e["ctx"]
            cost[turn]["out"] += e["out"]
            cost[turn]["peak"] = max(cost[turn]["peak"], e["ctx"])
            peak = max(peak, e["ctx"])
        elif k == "compact":
            cost[turn]["compact"] += 1
            print(f"[compact-summary] {clip(e['text'], 600)}")
        elif k == "skill_loaded":
            print(f"[{turn}] SKILL-LOADED: {e['path']}")
            cost[turn]["skills"].add(skill_name(e["path"]))
        elif k == "user":
            t = e["text"]
            cost[turn]["prompt"] = t
            # 用户手动点名的 skill（斜杠命令、$skill、附加 skill）= 手动触发；工具调用加载的为自动触发
            cost[turn]["manual"].update(n.split(":")[-1] for n in e.get("manual") or [])
            print(f"[{turn}] {'USER*' if CORRECTION.search(t) else 'USER'}: {clip(t, 400)}")
        elif k == "note":
            print(f"[{turn}] {e['text']}")
        elif k == "call":
            name, key = e["name"], e["key"]
            tools[e["id"]] = (name, key)
            cost[turn]["calls"] += 1
            if e.get("skill"):
                sk, args = e["skill"]
                cost[turn]["skills"].add(str(sk).split(":")[-1])
                print(f"[{turn}] SKILL: {sk} {args}")
            elif e.get("agent") is not None:
                print(f"[{turn}] AGENT: {e['agent']}")
            calls[(name, key, e.get("sig") or "")] += 1
        elif k == "result":
            name, key = tools.get(e["id"], ("?", ""))
            body = e["body"] or ""
            cost[turn]["res"] += len(body)
            if e.get("rejected"):
                print(f"[{turn}] REJECTED {name}: {key}")
            elif e["error"]:
                errors[(name, clip(body, 80))] += 1
                print(f"[{turn}] ERROR {name}: {key} -> {clip(body, 200)}")
            if len(body) > BIG_RESULT:
                print(f"[{turn}] BIG-RESULT {name}: {key} -> {len(body) // 1000}k chars")
    # 同一调用重复多次 = 重试/绕路的候选信号
    retries = [(k, n) for k, n in calls.items() if n >= 3 and k[1]]
    for (name, key, _), n in sorted(retries, key=lambda x: -x[1])[:10]:
        print(f"[retry x{n}] {name}: {key}")
    for (name, body), n in errors.items():
        if n >= 2:
            print(f"[repeat-error x{n}] {name}: {body}")
    stamp(pend)
    for t, (a, b) in span.items():
        cost[t]["ms"] = int((b - a).total_seconds() * 1000)
    agents = s.subagents()
    if has_usage:
        cost_report(cost, peak, agents, span)
    else:
        # 无 token 数据时不臆造成本信号
        print(f"[cost] unavailable: {s.runtime} transcripts record no token usage; "
              f"subagents={len(agents)} calls={sum(c['calls'] for c in cost.values())}")
        for a in agents:
            print(f"[agent] {a['type']} calls={a['calls']}: {clip(a['desc'], 80)}")
    print()


def fmt(n):
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k"


def cost_report(cost, peak, agents, span):
    """Token/time hotspots of the main agent and its subagents."""
    tin = sum(c["in"] for c in cost.values())
    tout = sum(c["out"] for c in cost.values())
    ms = sum(c["ms"] for c in cost.values())
    sub = sum(a["tokens"] for a in agents)
    print(f"[cost] main in={fmt(tin)} out={fmt(tout)} peak-ctx={fmt(peak)} wall={ms // 60000}m "
          f"subagents={len(agents)} ({fmt(sub)})")
    # 占总输入 ≥15% 的轮次为热点；其余调用了 skill 的轮次记为 skill-run。
    # 每行即一次调用的完整开销，复盘时可直接按行列成 Issue 证据表
    for t, c in sorted(cost.items(), key=lambda x: -x[1]["in"])[:10]:
        heavy = tin and c["in"] / tin >= 0.15
        sks = sorted(filter(None, c["skills"] | c["manual"]))
        if not heavy and (not sks or not c["calls"]):  # 无工具调用的 /plugin、/effort 等内置命令不算
            continue
        sk = ",".join(f"{s}({'manual' if s in c['manual'] else 'auto'})" for s in sks) or "-"
        ags = [a for a in agents if t in span and a["start"] and span[t][0] <= a["start"] <= span[t][1]]
        print(f"[{'heavy-turn' if heavy else 'skill-run'} {t}] in={fmt(c['in'])} ({c['in'] * 100 // max(tin, 1)}%) "
              f"out={fmt(c['out'])} calls={c['calls']} compactions={c['compact']} peak-ctx={fmt(c['peak'])} "
              f"subagents={len(ags)} ({fmt(sum(a['tokens'] for a in ags))}) results={c['res'] // 1000}k chars "
              f"wall={c['ms'] // 60000}m skills={sk}: {clip(c['prompt'], 100)}")
    for a in agents:
        tag = "HEAVY-AGENT" if a["tokens"] >= HEAVY_AGENT else "agent"
        print(f"[{tag}] {a['type']}/{a['model']} tokens={fmt(a['tokens'])} calls={a['calls']} "
              f"wall={a['wall']}s: {clip(a['desc'], 80)}")
    skill_report(cost, agents, span, tin + sub, ms)


def skill_report(cost, agents, span, ttok, tms):
    """Per-skill totals: main-agent input and wall time of the turns it was active in,
    plus subagents started within those turns. A turn with several skills counts for each."""
    per = collections.defaultdict(lambda: {"tok": 0, "ms": 0, "manual": False})
    for t, c in cost.items():
        for sk in filter(None, c["skills"] | c["manual"]):
            p = per[sk]
            p["tok"] += c["in"] + sum(a["tokens"] for a in agents
                                      if t in span and a["start"] and span[t][0] <= a["start"] <= span[t][1])
            p["ms"] += c["ms"]
            p["manual"] |= sk in c["manual"]
    for sk, p in sorted(per.items(), key=lambda x: -x[1]["tok"])[:5]:
        tp, mp = p["tok"] * 100 // max(ttok, 1), p["ms"] * 100 // max(tms, 1)
        tag = "HEAVY-SKILL" if max(tp, mp) >= HEAVY_SKILL * 100 else "skill-cost"
        print(f"[{tag}] {sk} via={'manual' if p['manual'] else 'auto'} tokens={fmt(p['tok'])} ({tp}%) "
              f"wall={p['ms'] // 60000}m ({mp}%)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("digest", "meta"):
        p = sub.add_parser(cmd)
        p.add_argument("--runtime", choices=[*RUNTIMES, "auto"], default="auto")
        p.add_argument("--cwd", default=os.getcwd())
        p.add_argument("ids", nargs="*")
    a = ap.parse_args()
    found = sessions(a.runtime, a.cwd, a.ids)
    if not found:
        sys.exit(f"no {a.runtime} session found for {a.cwd}")
    for s in found:
        print(meta_line(s)) if a.cmd == "meta" else digest(s)


if __name__ == "__main__":
    main()
