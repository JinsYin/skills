# Eval run log

## 2026-10-29: initial skill

- Matrix: backport-prototype vs. no skill, subagent runs on `claude-opus-5-5`, one run per configuration; fixtures built with `files/init.sh`.
- Totals: backport-prototype 15/15 expectations; no skill 11/15; delta +21 percentage points. Rerun after compression: 15/15, no regression.

| Eval | backport-prototype | No skill |
|---|---|---|
| 0 drift-before-and-after-last-prototype-commit | 7/7 | 4/7 |
| 1 multi-line-pending-forward-and-removal-ask | 5/5 | 4/5 |
| 2 restyle-app-without-structural-drift | 3/3 | 3/3 |

- Eval 2 does not discriminate: without the skill the model also skips restyle visuals. Kept as a regression guard for rule 3.
- Without the skill the model logged entries without the `回补已上线前端：` prefix, drew no guard material for `fspec` 前置条件, and named no `/fspec` next step.
- First draft asked `ask` rows before backporting, stalling unattended runs; reordered to backport first, ask after.
