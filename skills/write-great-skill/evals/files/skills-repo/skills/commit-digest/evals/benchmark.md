# Eval run log

## 2026-10-20: initial skill

- Matrix: commit-digest vs no skill, `claude-sonnet-5-5`, one run per configuration; fixtures built inline.
- Totals: commit-digest 7/7; no skill 3/7; delta +57 pp.

| Eval | commit-digest | No skill |
|---|---|---|
| 0 group-by-type | 4/4 | 2/4 |
| 1 drop-merge-commits | 3/3 | 1/3 |

- Findings: without the skill the model listed commits flat and kept merge commits.
