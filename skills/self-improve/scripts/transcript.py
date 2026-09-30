#!/usr/bin/env python3
"""Compact Claude Code session transcripts into retrospective evidence.

  transcript.py list   [--cwd DIR] [--limit N]    # sessions of a project, newest first
  transcript.py digest [--cwd DIR] [ID|PATH ...]  # signal digest; default = newest session
  transcript.py meta   [--cwd DIR] [ID|PATH ...]  # session id/name, runtime, most-used and last model/effort

Transcripts live at ~/.claude/projects/<slug>/<session-id>.jsonl, where slug is
the project path with every non-alphanumeric char replaced by '-'.
Output is deliberately small: raw transcripts are huge, the digest keeps only
what a retrospective needs (prompts, skill loads, errors, corrections, retries).
"""
import argparse
import collections
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.expanduser("~/.claude/projects")
CLIP = 280
BIG_RESULT = 20_000  # 单个工具结果字符数阈值，超过视为可能浪费上下文
HEAVY_AGENT = 200_000  # 子 Agent Token 阈值
HEAVY_SKILL = 0.25  # skill 占全会话 Token 或耗时的比例阈值

# 用户纠正/否定的常见措辞（中英），只作为候选提示，最终由模型判断
CORRECTION = re.compile(
    r"(^|\b)(no|nope|wrong|actually|instead|don'?t|stop|again|not what|why did you|revert|undo)\b"
    r"|不对|不是|错了|应该|别|不要|重新|又|还是|怎么没|没有按|回滚|撤销",
    re.I,
)
NOISE = ("<local-command", "<command-name>", "<command-message>", "<system-reminder>", "Caveat:")
BUILTIN = {"clear", "compact", "resume", "model", "config", "cost", "exit", "help", "init", "status"}
INTERRUPT = ("[Request interrupted", "doesn't want to proceed", "user rejected", "was rejected")


def project_dir(cwd):
    return os.path.join(ROOT, re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd)))


def clip(s, n=CLIP):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            b.get("text", "") if b.get("type") == "text" else text_of(b.get("content"))
            for b in content
            if isinstance(b, dict)
        )
    return ""


def records(path):
    # 逐行流式读取，避免一次性载入大文件
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def human_prompt(d):
    """Return the text of a genuine user-typed message, else None."""
    if d.get("type") != "user" or d.get("isMeta") or d.get("isSidechain"):
        return None
    c = (d.get("message") or {}).get("content")
    if isinstance(c, list) and any(b.get("type") == "tool_result" for b in c if isinstance(b, dict)):
        return None
    # IDE 附带的选区/打开文件提示不是用户意图，剔除以省 Token
    t = re.sub(r"<ide_\w+>.*?</ide_\w+>|</?pasted_content[^>]*>", "", text_of(c), flags=re.S).strip()
    m = re.search(r"<command-name>/?([^<]+)</command-name>(?:.*?<command-args>(.*?)</command-args>)?", t, re.S)
    if m:
        # 斜杠命令：保留命令名与参数（无参数时没有 command-args 标签），内置的清屏等命令无复盘价值
        return None if m.group(1) in BUILTIN else f"/{m.group(1)} {(m.group(2) or '').strip()}".rstrip()
    if not t or t.startswith(NOISE) or t.startswith("Base directory for this skill"):
        return None
    return t


def skill_loaded(d):
    """Path of a skill whose body was injected into this user record, if any."""
    if d.get("type") != "user":
        return None
    m = re.match(r"\s*Base directory for this skill: (\S+)", text_of((d.get("message") or {}).get("content")))
    return m and m.group(1)


def cmd_list(a):
    pdir = project_dir(a.cwd)
    if not os.path.isdir(pdir):
        sys.exit(f"no transcripts for {a.cwd} ({pdir})")
    files = sorted(
        (os.path.join(pdir, f) for f in os.listdir(pdir) if f.endswith(".jsonl")),
        key=os.path.getmtime,
        reverse=True,
    )[: a.limit]
    for i, p in enumerate(files, 1):
        title, first, prompts = "", "", 0
        for d in records(p):
            if d.get("type") in ("custom-title", "ai-title"):
                title = d.get("customTitle") or d.get("aiTitle") or d.get("title") or title
            t = human_prompt(d)
            if t:
                prompts += 1
                first = first or t
        when = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
        sid = os.path.basename(p)[:-6]
        print(f"{i:>2}. {sid[:8]}  {when}  {prompts:>3} prompts  {clip(title or first, 90)}")


def resolve(ids, cwd):
    pdir = project_dir(cwd)
    if not ids:
        files = [os.path.join(pdir, f) for f in os.listdir(pdir) if f.endswith(".jsonl")]
        return [max(files, key=os.path.getmtime)]
    out = []
    for s in ids:
        if os.path.isfile(s):
            out.append(s)
            continue
        hit = [f for f in os.listdir(pdir) if f.startswith(s) and f.endswith(".jsonl")]
        if len(hit) != 1:
            sys.exit(f"session '{s}' matched {len(hit)} files in {pdir}")
        out.append(os.path.join(pdir, hit[0]))
    return out


def meta(path):
    """One-line provenance: id, name, runtime, most-used and last model/effort."""
    name, ai, ver, entry, last = "", "", "", "", ""
    # model 与 effort 会话中途都可能被切换：按对计数，最后一对才是当前档位
    pairs = collections.Counter()
    for d in records(path):
        # 手动 /rename 的 customTitle 优先于自动生成的 aiTitle，取最后一次
        name = d.get("customTitle") or name
        ai = d.get("aiTitle") or ai
        ver, entry = d.get("version") or ver, d.get("entrypoint") or entry
        m = (d.get("message") or {}).get("model")
        if m and not m.startswith("<"):
            last = f"{m}/{d.get('effort') or 'unknown'}"
            pairs[last] += 1
    most = pairs.most_common(1)[0][0] if pairs else "unknown"
    runtime = f"Claude Code {ver} ({entry})".replace(" ()", "") if ver else "Claude Code"
    return (f"session={os.path.basename(path)[:-6]} name={name or ai or '-'} "
            f"runtime={runtime} most={most} last={last or 'unknown'}")


def digest(path):
    print(f"## {meta(path)}")
    tools = {}  # tool_use_id -> (name, short input)
    calls = collections.Counter()
    errors = collections.Counter()
    turn = 0
    # 按用户轮次累计开销；同一 message.id 会拆成多条记录，usage 只计一次
    cost = collections.defaultdict(lambda: {"in": 0, "out": 0, "calls": 0, "ms": 0, "skills": set(), "manual": set(), "prompt": ""})
    seen, peak, span = set(), 0, {}
    for d in records(path):
        ts = stamp(d)
        if ts:
            # 每轮耗时 = 该轮首末记录的时间差（turn_duration 记录并非总存在）
            a, _ = span.get(turn, (ts, ts))
            span[turn] = (a, ts)
        u = (d.get("message") or {}).get("usage")
        mid = (d.get("message") or {}).get("id")
        if u and mid not in seen and not d.get("isSidechain"):
            seen.add(mid)
            ctx = sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
            cost[turn]["in"] += ctx
            cost[turn]["out"] += u.get("output_tokens") or 0
            peak = max(peak, ctx)
        if d.get("isCompactSummary"):
            print(f"[compact-summary] {clip(text_of((d.get('message') or {}).get('content')), 600)}")
            continue
        msg = d.get("message") or {}
        content = msg.get("content")
        loaded = skill_loaded(d)
        if loaded:
            print(f"[{turn}] SKILL-LOADED: {loaded}")
            cost[turn]["skills"].add(os.path.basename(loaded.rstrip("/")).split(":")[-1])
            continue
        t = human_prompt(d)
        if t:
            turn += 1
            tag = "USER*" if CORRECTION.search(t) else "USER"
            cost[turn]["prompt"] = t
            if t.startswith("/"):
                # 用户手敲的斜杠命令 = 手动触发；Skill 工具调用则是模型或其他 skill 自动触发
                cost[turn]["manual"].add(t[1:].split()[0].split(":")[-1])
            print(f"[{turn}] {tag}: {clip(t, 400)}")
            continue
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                name, inp = b.get("name", "?"), b.get("input") or {}
                key = inp.get("skill") or inp.get("command") or inp.get("file_path") or inp.get("description") or ""
                tools[b.get("id")] = (name, clip(str(key), 120))
                cost[turn]["calls"] += 1
                if name == "Skill":
                    cost[turn]["skills"].add(str(inp.get("skill")).split(":")[-1])
                    print(f"[{turn}] SKILL: {inp.get('skill')} {clip(str(inp.get('args') or ''), 120)}")
                elif name in ("Agent", "Task"):
                    print(f"[{turn}] AGENT: {clip(inp.get('description') or '', 120)}")
                # 同一文件的不同 Edit、不同段落的 Read 不是重试：签名带上改动内容或偏移
                calls[(name, key, str(inp.get("old_string") or inp.get("offset") or ""))] += 1
            elif b.get("type") == "tool_result":
                name, key = tools.get(b.get("tool_use_id"), ("?", ""))
                body = text_of(b.get("content"))
                if any(m in body for m in INTERRUPT):
                    print(f"[{turn}] REJECTED {name}: {key}")
                elif b.get("is_error"):
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
    for t, (a, b) in span.items():
        cost[t]["ms"] = int((b - a).total_seconds() * 1000)
    cost_report(cost, peak, subagents(path), span)
    print()


def stamp(d):
    try:
        return datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
    except (KeyError, ValueError, AttributeError):
        return None


def subagents(path):
    """Per-subagent totals from <session>/subagents/agent-*.jsonl (sync and async alike)."""
    sdir = os.path.join(path[:-6], "subagents")
    out = []
    for f in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
        if not f.endswith(".jsonl"):
            continue
        tok, calls, seen, model, ts = 0, 0, set(), "", []
        for d in records(os.path.join(sdir, f)):
            m = d.get("message") or {}
            t = stamp(d)
            if t:
                ts.append(t)
            if m.get("id") and m.get("usage") and m["id"] not in seen:
                seen.add(m["id"])
                u = m["usage"]
                tok += sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens",
                                                     "cache_read_input_tokens", "output_tokens"))
                model = m.get("model") or model
            if isinstance(m.get("content"), list):
                calls += sum(1 for b in m["content"] if isinstance(b, dict) and b.get("type") == "tool_use")
        try:
            info = json.load(open(os.path.join(sdir, f[:-6] + ".meta.json")))
        except (OSError, ValueError):
            info = {}
        wall = int((max(ts) - min(ts)).total_seconds()) if ts else 0
        out.append({"desc": info.get("description") or f[:-6], "type": info.get("agentType"),
                    "start": min(ts) if ts else None,
                    "model": model, "tokens": tok, "calls": calls, "wall": wall})
    return out


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
    # 占总输入 ≥15% 的轮次为热点，附带所用 skill 便于定位过长流程
    for t, c in sorted(cost.items(), key=lambda x: -x[1]["in"])[:3]:
        if tin and c["in"] / tin >= 0.15:
            sk = ",".join(sorted(filter(None, c["skills"]))) or "-"
            print(f"[heavy-turn {t}] in={fmt(c['in'])} ({c['in'] * 100 // tin}%) calls={c['calls']} "
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
    l = sub.add_parser("list")
    l.add_argument("--cwd", default=os.getcwd())
    l.add_argument("--limit", type=int, default=20)
    g = sub.add_parser("digest")
    g.add_argument("--cwd", default=os.getcwd())
    g.add_argument("ids", nargs="*")
    m = sub.add_parser("meta")
    m.add_argument("--cwd", default=os.getcwd())
    m.add_argument("ids", nargs="*")
    a = ap.parse_args()
    if a.cmd == "list":
        cmd_list(a)
    else:
        for p in resolve(a.ids, a.cwd):
            print(meta(p)) if a.cmd == "meta" else digest(p)


if __name__ == "__main__":
    main()
