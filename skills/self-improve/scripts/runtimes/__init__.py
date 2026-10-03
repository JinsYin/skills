"""Runtime adapters: claude, codex, cursor, agy."""
import os

from . import agy, claude, codex, cursor

RUNTIMES = {"claude": claude, "codex": codex, "cursor": cursor, "agy": agy}


def detect():
    # 只有 Claude Code 会可靠地导出可识别的环境变量；其余 Runtime 由调用方传 --runtime
    return "claude" if os.environ.get("CLAUDECODE") else None


def by_path(path):
    p = os.path.abspath(path)
    if p.endswith(".db"):
        return agy
    if "/.codex/" in p or os.path.basename(p).startswith("rollout-"):
        return codex
    if "/agent-transcripts/" in p:
        return cursor
    return claude


def sessions(runtime, cwd, ids):
    """Sessions to digest: explicit paths, else ids/newest of cwd in the chosen runtime.
    runtime 'auto' without a detectable host picks the newest session across runtimes."""
    paths = [i for i in ids if os.path.isfile(i)]
    if paths:
        return [(RUNTIMES[runtime] if runtime in RUNTIMES else by_path(p)).from_path(p) for p in paths]
    rt = runtime if runtime in RUNTIMES else detect()
    if rt:
        return RUNTIMES[rt].find(cwd, ids)
    found = [s for m in RUNTIMES.values() for s in m.find(cwd, [])]
    return [max(found, key=lambda s: s.mtime())] if found else []
