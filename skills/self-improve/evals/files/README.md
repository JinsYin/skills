# self-improve eval fixtures

Each fixture dir holds:

- `home/` — fake `HOME`; transcripts live at `home/.claude/projects/-work-demo/` (slug of cwd `/work/demo`).
- `project/` — the source project (`skills-lock.json`), standing in for cwd `/work/demo`.

Run the digest as `HOME=<fixture>/home python3 scripts/transcript.py <cmd> --cwd /work/demo`; the newest transcript is the "current session".

Non-Claude fixtures (`codex-*`, `cursor-*`, `agy-*`) store the session in that runtime's layout under `home/` (`.codex/sessions/`, `.cursor/projects/work-demo/`, `.gemini/antigravity/`); add `--runtime codex|cursor|agy`. The eval prompt names the runtime the session ran in.

GitHub reads (`gh repo view`, `gh issue list`, clone) hit the real `jinsyin/skills`. Exception: an eval whose `expected_output` names a stubbed read uses that stub. Stub every write (`gh issue create`, `gh issue comment`, `gh label create`, `gh pr create`, `git push`): save the command and body file to outputs instead.

Regenerate with `python3 evals/gen_fixtures.py evals/files`.
