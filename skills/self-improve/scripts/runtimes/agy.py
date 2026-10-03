"""Antigravity (agy CLI and IDE): ~/.gemini/antigravity/conversations/<id>.db (SQLite).
`steps` rows hold protobuf blobs, decoded here without a schema by field number;
`gen_metadata` holds one row per model call (model, token usage). The index
conversation_summaries.db maps conversations to workspaces, titles and parents."""
import collections
import json
import os
import re
import sqlite3
import sys
from urllib.parse import quote

from .common import Session, clip, epoch, skill_reads, tool_key

ROOT = os.path.expanduser("~/.gemini/antigravity")
EXIT = re.compile(r"exited with code (-?\d+)")
# 已观察到的字段号（无官方 schema）：step_type 14 = 用户输入，15 = 模型回合（含工具调用），
# 带 field 140 的 step = 工具结果
USER, PLANNER = 14, 15


def varint(b, i):
    r = s = 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7F) << s
        s += 7
        if c < 0x80:
            return r, i


def fields(b):
    """[(field, value)] of one protobuf message; length-delimited values stay bytes."""
    out, i = [], 0
    try:
        while i < len(b):
            k, i = varint(b, i)
            f, w = k >> 3, k & 7
            if w == 0:
                v, i = varint(b, i)
            elif w == 2:
                n, i = varint(b, i)
                v, i = b[i:i + n], i + n
            elif w in (1, 5):
                n = 8 if w == 1 else 4
                v, i = b[i:i + n], i + n
            else:
                return out
            out.append((f, v))
    except IndexError:
        pass
    return out


def get(b, *path):
    """All values at a field path, e.g. get(payload, 20, 7)."""
    vals = [b]
    for f in path:
        vals = [v for x in vals if isinstance(x, bytes) for g, v in fields(x) if g == f]
    return vals


def one(b, *path, default=None):
    v = get(b, *path)
    return v[0] if v else default


def text(v):
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else (v or "")


def connect(path):
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def summaries(where, args):
    db = os.path.join(ROOT, "conversation_summaries.db")
    if not os.path.exists(db):
        return []
    c = connect(db)
    c.row_factory = sqlite3.Row
    return c.execute(f"select * from conversation_summaries where {where} order by last_modified_time desc", args).fetchall()


def find(cwd, ids):
    uri = "file://" + quote(os.path.abspath(cwd))
    rows = [r for r in summaries("nesting_depth = 0 and workspace_uris like ?", (f'%"{uri}"%',))
            if os.path.exists(os.path.join(ROOT, "conversations", r["conversation_id"] + ".db"))]
    if not ids:
        return [AgySession(rows[0])] if rows else []
    out = []
    for s in ids:
        hit = [r for r in rows if r["conversation_id"].startswith(s)]
        if len(hit) != 1:
            sys.exit(f"agy: conversation '{s}' matched {len(hit)} for {cwd}")
        out.append(AgySession(hit[0]))
    return out


def from_path(path):
    cid = os.path.basename(path)[:-3]
    rows = summaries("conversation_id = ?", (cid,))
    return AgySession(rows[0] if rows else {"conversation_id": cid, "title": ""})


def gens(path):
    """Model calls: (after_step_index, ts, model, in_tokens, out_tokens)."""
    out = []
    for (data,) in connect(path).execute("select data from gen_metadata order by idx"):
        g = one(data, 1, default=b"")
        kv = {text(one(e, 1)): text(one(e, 2)) for e in get(g, 20)}
        u = one(g, 4, default=b"")
        out.append((int(kv.get("last_step_index") or -1), epoch(one(g, 11, 1, default=0)),
                    text(one(g, 19)) or "unknown", one(u, 2, default=0), one(u, 3, default=0)))
    return out


class AgySession(Session):
    runtime = "Antigravity"

    def __init__(self, row):
        cid = row["conversation_id"]
        super().__init__(cid, os.path.join(ROOT, "conversations", cid + ".db"))
        self.title = row["title"]

    def meta(self):
        pairs, last = collections.Counter(), ""
        for _, _, model, _, _ in gens(self.path):
            # agy 不记录推理档位
            last = f"{model}/unknown"
            pairs[last] += 1
        return {"name": self.title, "runtime": "Antigravity (agy)", "pairs": pairs, "last": last}

    def events(self):
        by_step = collections.defaultdict(list)
        for g in gens(self.path):
            by_step[g[0]].append(g)
        pending = collections.deque()
        rows = connect(self.path).execute(
            "select idx, step_type, metadata, error_details, step_payload from steps order by idx")
        for idx, st, meta, err, p in rows:
            p = p or b""
            yield {"k": "tick", "ts": epoch(one(meta or b"", 1, 1, default=0), one(meta or b"", 1, 2, default=0))}
            if st == USER:
                t = text(one(p, 19, 2)).strip()
                if t:
                    yield {"k": "user", "text": t, "manual": [t[1:].split()[0]] if t.startswith("/") else []}
            elif st == PLANNER:
                for c in get(p, 20, 7):
                    cid, name, raw = text(one(c, 1)), text(one(c, 2)) or "?", text(one(c, 3))
                    try:
                        args = json.loads(raw or "{}")
                    except ValueError:
                        args = {"args": raw}
                    pending.append((cid, name))
                    ev = {"k": "call", "id": cid, "name": name, "key": tool_key(args), "sig": raw}
                    if "subagent" in name.lower() or name in ("invoke_subagent", "spawn_agent"):
                        ev["agent"] = clip(args.get("Description") or args.get("Task") or raw, 120)
                    yield ev
                    for path, _ in skill_reads(f"{name} {raw}"):
                        yield {"k": "skill_loaded", "path": path}
            elif get(p, 140):
                body = text(one(p, 140, 2, 1))
                cid = pending.popleft()[0] if pending else f"s{idx}"
                codes = [int(c) for c in EXIT.findall(body)]
                yield {"k": "result", "id": cid, "body": body, "error": bool(err) or any(c != 0 for c in codes)}
            for _, _, _, i, o in by_step.pop(idx, []):
                yield {"k": "usage", "ctx": i, "out": o}
        for gs in by_step.values():
            for _, _, _, i, o in gs:
                yield {"k": "usage", "ctx": i, "out": o}

    def subagents(self):
        out = []
        for r in summaries("parent_conversation_id = ?", (self.id,)):
            path = os.path.join(ROOT, "conversations", r["conversation_id"] + ".db")
            if not os.path.exists(path):
                continue
            g = gens(path)
            ts = [x[1] for x in g if x[1]]
            calls = sum(len(get(p or b"", 20, 7)) for (p,) in
                        connect(path).execute("select step_payload from steps where step_type = ?", (PLANNER,)))
            out.append({"desc": r["title"] or r["conversation_id"], "type": r["agent_name"] or "subagent",
                        "start": min(ts) if ts else None, "model": g[-1][2] if g else "unknown",
                        "tokens": sum(x[3] + x[4] for x in g), "calls": calls,
                        "wall": int((max(ts) - min(ts)).total_seconds()) if ts else 0})
        return out
