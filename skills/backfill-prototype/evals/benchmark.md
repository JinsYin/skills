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

## 2026-10-29: rename to backfill-prototype

- Matrix: with-skill subagent runs on `claude-opus-5-5`; no-skill results above still apply.
- Totals before fix: 13/15. Eval 2 failed twice: the model read `confirm: true` on 重置密钥/停用 as a missing overlay and drew a confirmation dialog; the pre-rename skill skipped it on the same fixture. Eval 1 drew the same dialog, outside its expectations.
- Fix: rule 3 skips interaction conventions `ui-ux-best-practices` owns. Rerun: eval 2 3/3 twice, eval 1 5/5 with no dialog; eval 0 7/7. Eval 2 now asserts no confirmation dialog.
