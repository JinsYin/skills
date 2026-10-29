# Eval run log

## 2026-10-29: initial skill

- Matrix: re-spec vs. no skill, subagent runs on `claude-opus-5-5`, one run per configuration; fixtures built with `files/init.sh`, `github` with the `bin/gh` stub on `PATH`.
- Totals: re-spec 21/21 expectations; no skill 14/21; delta +33 percentage points. Rerun after compression: 21/21, no regression.

| Eval | re-spec | No skill |
|---|---|---|
| 0 matt-local-preapproved-alignment | 8/8 | 5/8 |
| 1 superpowers-confirm-with-questions | 6/6 | 4/6 |
| 2 draft-v-stops | 2/2 | 0/2 |
| 3 github-issue-spec-reads-via-gh | 3/3 | 3/3 |
| 4 already-aligned-noop | 2/2 | 2/2 |

- Evals 3 and 4 do not discriminate: without the skill the model also reads the issue via `gh` and confirms first, and reports no change on an aligned spec. Kept as regression guards.
- Without the skill the model edited a spec against a draft V, rewrote Testing Decisions, left no `CURRENT.md` pointer, grouped changes by question instead of spec section, and never mentioned the original `/brainstorming` session.
- First draft scored 3/8 on eval 0: pre-approved yet held every edit for open questions. Rule 6 now writes unambiguous edits first; the fixture's `CURRENT.md` was also fixed to really merge V2.
