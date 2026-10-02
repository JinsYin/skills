---
name: Skill improvement
about: Improve an existing skill or propose a new one, backed by session evidence
title: "<fix|feat>(<skill>): <summary>"
labels: self-improve
---

## Target

- Skill: `<name>` (existing | new)
- Change type: fix wording | add instruction | cut tokens | shorten flow | new skill | other

## Context

<!-- Where the lessons came from and who proposed the change. Unknown → `unknown`. -->

- Source project: `<name>`
- Agent runtime: Claude Code | Codex | Cursor | Antigravity | … (version / surface if known)
- Retrospected sessions: `<session-id>` (`<name>`), most `<model>/<effort>`, last `<model>/<effort>`; …
- Improvement run (`self-improve`): session `<session-id>`, `<model>/<effort>` (`meta` last)

## Evidence

<!-- Quote the session turns that show the problem. Mark strong (user correction / rework / skill-caused cost hotspot) or weak (detour, retry, error; needs ≥2). For cost, add one row per run with its digest `[heavy-turn]`/`[skill-run]` fields. -->

| # | Step where it went wrong | What happened | Signal |
|---|---|---|---|
| 1 |  |  | strong |

## Root cause

<!-- Which rule / instruction / config should have steered the agent, and why it did not take effect (missing, wording, placement, precedence, discoverability). -->

## Proposed change

<!-- Minimal, concise diff: the passage before and after, why it prevents a recurrence, and the expected token / step saving if any. -->

## Checked

- [ ] No duplicate open/closed Issue or PR
- [ ] Latest default branch does not already cover it
- [ ] Reusable beyond the originating project

## Below the gate (optional)

<!-- Observations not strong or frequent enough to act on yet. -->
