"""Shared helpers for runtime adapters.

Each adapter module exposes `find(cwd, ids)` returning Session objects. A Session
yields normalized events from `events()` so `transcript.py` digests every runtime
the same way:

  {"k": "tick"}                              any record, only advances the turn clock
  {"k": "user", "text": str, "manual": [skill names]}
  {"k": "skill_loaded", "path": str}         skill body injected or SKILL.md read
  {"k": "call", "id", "name", "key", "sig", "skill"?, "agent"?}
  {"k": "result", "id", "body", "error": bool}
  {"k": "usage", "ctx": int, "out": int}     one model response, input incl. cache
  {"k": "compact", "text": str}
  {"k": "note", "text": str}                 turn-level marker, e.g. INTERRUPTED

Every event may carry "ts" (aware datetime) used for turn wall time.
"""
import json
import os
import re
from datetime import datetime, timezone

# 读取类命令打开 SKILL.md 即视为模型自动加载了该 skill
SKILL_READ = re.compile(r"""\b(?:cat|sed|head|tail|nl|less|bat|Get-Content|view_file|read_file)\b[^|;&]*?([^\s"'`]*/([\w.-]+)/SKILL\.md)""")


def clip(s, n=280):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def records(path):
    # 逐行流式读取，避免一次性载入大文件
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def first_record(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        try:
            return json.loads(f.readline())
        except ValueError:
            return {}


def iso(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def epoch(sec, nanos=0):
    return datetime.fromtimestamp(sec + nanos / 1e9, tz=timezone.utc) if sec else None


def same_dir(a, b):
    return bool(a) and os.path.realpath(a) == os.path.realpath(b)


def tool_key(inp):
    """Short, human-meaningful identity of a tool call's input."""
    if not isinstance(inp, dict):
        return clip(str(inp), 120)
    for k in ("skill", "command", "cmd", "CommandLine", "file_path", "path", "AbsolutePath",
              "TargetFile", "pattern", "query", "Query", "url", "description"):
        v = inp.get(k)
        if v:
            return clip(" ".join(v) if isinstance(v, list) else str(v), 120)
    return clip(json.dumps(inp, ensure_ascii=False), 120)


def skill_reads(text):
    """(path, name) of every SKILL.md a read-like command or tool input opens."""
    return [(m.group(1), m.group(2)) for m in SKILL_READ.finditer(text or "")]


class Session:
    runtime = "unknown"

    def __init__(self, sid, path):
        self.id, self.path = sid, path

    def meta(self):
        """dict(name, runtime, pairs: Counter of model/effort, last)."""
        raise NotImplementedError

    def events(self):
        raise NotImplementedError

    def subagents(self):
        """[{desc, type, start, model, tokens, calls, wall}]"""
        return []

    def mtime(self):
        return os.path.getmtime(self.path)
