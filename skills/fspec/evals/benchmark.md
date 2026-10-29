# Eval run log

## 2026-10-27: fspec rewrite (product-spec → fspec)

Eval ids below predate the 2026-10-28 renumbering.

- Matrix: fspec vs. no skill, `claude -p` with `claude-opus-5-5`, one run per configuration; fixtures built with `files/init.sh`.
- Totals: fspec 45/45 expectations; no skill 21/45; delta +53 percentage points.

| Eval | fspec | No skill |
|---|---|---|
| 0 greenfield-baseline-from-prototype | 9/9 | 2/9 |
| 1 incremental-change-with-backport | 9/9 | 1/9 |
| 2 confirmed-draft-merges-incrementally | 7/7 | 5/7 |
| 3 stale-locator-stops | 6/6 | 6/6 |
| 4 multi-line-asks-which-line | 3/3 | 0/3 |
| 5 legacy-dir-proposes-migration | 3/3 | 1/3 |
| 6 no-prototype-change-writes-nothing | 3/3 | 2/3 |
| 7 stale-current-full-replay | 5/5 | 4/5 |

- Eval 3 does not discriminate: without the skill the model also stops on unresolved locators. Kept as a regression guard for rule 3.
- Eval 4 first ran as `/fspec`; the no-skill run asked because the command was missing. Switched to a natural prompt, where the no-skill run synced both lines unasked.
- Eval 3 first had one stale locator; an ambiguous `禁用` row was added to tempt guessing. Still non-discriminating.
- Without the skill the model wrote a new path (`products/spec/console.md`), split the backport into its own V, merged without confirmation, and wrote into the legacy `products/specs/`.

## 2026-10-28: prototype CHANGELOG versions, English fixtures

- Change: confirming V<n> cuts the prototype CHANGELOG `[Unreleased]` into `[V<n>]` (`[<Line> V<n>]` with several lines); fixtures renamed to English slugs, fixture `CLAUDE.md` in English.
- Matrix as above. Totals (evals 0–6): fspec 40/40; no skill 16/40.

| Eval | fspec | No skill |
|---|---|---|
| 0 greenfield-baseline-from-prototype | 9/9 | 2/9 |
| 1 incremental-change-with-backport | 9/9 | 1/9 |
| 2 confirmed-draft-merges-incrementally | 8/8 | 6/8 |
| 3 multi-line-asks-which-line | 3/3 | 0/3 |
| 4 legacy-dir-proposes-migration | 3/3 | 1/3 |
| 5 no-prototype-change-writes-nothing | 3/3 | 2/3 |
| 6 stale-current-full-replay | 5/5 | 4/5 |
| 7 legacy-changelog-left-as-is | not run | not run |

- The first run leaked: the fixture CHANGELOG header said versions match the fspec V files, and the no-skill model cut versions from that line. The header was cut to the standard Keep a Changelog line and the matrix rerun.
- The cut alone does not discriminate: without the skill the model infers `[V2]` from an existing `[V1]`. Cutting before confirmation (eval 1) and on a baseline (eval 0) does.
- Eval 2: the fspec run read V1's first 9 lines for the version precondition; the expectation now allows frontmatter-only reads.
- Removed on user request, both non-discriminating: `stale-locator-stops` and `multi-line-confirm-cuts-line-version`. Rule 3 and the multi-line cut have no eval.
- Not yet measured, by user decision: eval 7 (its first run hit the usage limit), the switch to `/fspec [<prototype>]`, and the writing-for-agents and compression edits.

## 2026-10-29: `/fspec [<prototype>]`, polished and compressed text

- Change: argument is the prototype path (default `products/prototype/`); writing-for-agents and compression edits. Matrix as above, all 8 evals.
- Totals: fspec 43/43; no skill 16/43; delta +63 percentage points. No regressions.

| Eval | fspec | No skill |
|---|---|---|
| 0 greenfield-baseline-from-prototype | 9/9 | 2/9 |
| 1 incremental-change-with-backport | 9/9 | 1/9 |
| 2 confirmed-draft-merges-incrementally | 8/8 | 5/8 |
| 3 multi-line-asks-which-line | 3/3 | 0/3 |
| 4 legacy-dir-proposes-migration | 3/3 | 1/3 |
| 5 no-prototype-change-writes-nothing | 3/3 | 2/3 |
| 6 stale-current-full-replay | 5/5 | 3/5 |
| 7 legacy-changelog-left-as-is | 3/3 | 2/3 |

- Eval 7 discriminates only on the report: without the skill the model also leaves the legacy CHANGELOG untouched but never says why no prototype version was cut.
