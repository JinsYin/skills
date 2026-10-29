---
name: re-spec
description: "Revise feature spec to match newly confirmed 功能规格说明书 (fspec) V file: align user stories, decisions and Out of Scope with what prototype settled, for matt /to-spec specs (.scratch/<feature>/spec.md or a GitHub issue) and superpowers specs (docs/superpowers/specs/*.SPEC.md). Use after /fspec <prototype> activates V, or when user says 修订 spec, 对齐 spec or re-spec. Not for writing fspec itself (fspec) or new spec (/to-spec, brainstorming)."
argument-hint: "[<spec>] [<fspec V>]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# Re-spec

Feature spec precedes prototype; prototype iteration settles what UI really does, `fspec` records it as V file. Downstream `/to-tickets` and `writing-plans` read spec, so spec still promising dropped stories or old field names breaks tickets and plans. This skill pulls spec back in line. Reply in Chinese.

Codex: `$ARGUMENTS` = text after command. No interactive picker → print numbered options, stop for user's reply; never answer own question.

## Rules

1. Active fspec V is truth for what UI shows and how it behaves; spec keeps everything fspec cannot say: problem, motivation, backend, data, API, test seams.
2. Spec stays at story and decision level. Cite fspec, never copy its tables: one line in Further Notes (superpowers: closest notes section) `界面细节以 products/fspec/<line>/CURRENT.md 为准（V<n>）`. Duplicated detail drifts.
3. Use fspec 术语表 terms verbatim; rename every old term in spec.
4. Touch only what V changes for this feature. V rows marked backport (`回补`), or unrelated to spec's feature, stay out of spec.
5. Testing Decisions stay byte-identical: test seams were agreed with user. New behavior no seam covers → suggest in reply, don't block on it.
6. Write nothing before user confirms change list. User pre-approved in request → write every unambiguous edit at once, then ask open questions; answers land as follow-up edit. Never hold back whole revision for one question.

## Spec forms

| Form | Read | Write | Revision record |
|---|---|---|---|
| matt local | `.scratch/<feature>/spec.md`, incl. `## Comments` | edit file | append `## Comments` entry |
| matt GitHub | `gh issue view <n> --comments` | `gh issue edit <n> --body-file <tmp>` | `gh issue comment <n>` |
| superpowers | `docs/superpowers/specs/<milestone>-<topic>.SPEC.md` | edit file | none; commit carries it |

Revision record body: `re-spec：依据 products/fspec/<line>/V<n>__<slug>.md 修订 <sections>`.

## Workflow

**1. Locate spec.** `$ARGUMENTS` path, issue number or URL. None → candidates from spec forms above whose feature matches recent fspec V; one → use it, several → ask.

**2. Pick V.** `$ARGUMENTS` V path wins. Else per line in `products/fspec/`: newest V committed after spec's last change (`git log -1 --format=%ct` on each; GitHub spec: last revision comment time, else creation time).
- Newest such V `status: draft` → stop: confirm it with `/fspec` first.
- None → report "spec 已与 fspec 对齐", stop.

**3. Read** V (变更摘要, 变更清单, page sections, 明确不做, 术语表), `CURRENT.md` for context, spec body and comments. Current session is the spec's `/to-spec` or `/brainstorming` session → reuse its discussion too.

**4. Map** each relevant V change to spec edit:
- New page, action, field, state, flow → add or extend user story; UI-driven decision (e.g. read-only page, confirmation required) → Implementation Decisions.
- Rename or changed behavior → rewrite matching story or decision.
- V 明确不做 item spec promised or omitted → Out of Scope, with V's reason.
- Spec UI story V drops, or `CURRENT.md` lacks and 明确不做 doesn't mention → ask: descope to Out of Scope, or prototype missed it (then fix prototype, rerun `/fspec`).
- Conflict with non-UI decision (retention, API, data) → ask; never resolve by guess.

Done when every V 变更清单 row maps to edit, rule 4 skip or question.

**5. Confirm.** Show change list grouped by spec section (before → after) plus all questions in one round. Fresh session → add one line: spec reasoning absent from spec body and comments lives only in original `/to-spec` (superpowers: `/brainstorming`) session; rerun there if answers need it. Unconfirmed → spec untouched. Pre-approved → skip to step 6 for unambiguous edits; questions go in report.

**6. Write** confirmed edits plus rule 2 pointer and revision record per form. Keep spec template and section order; don't add sections. Superpowers spec marked `reviewed` stays so; say it was revised after review.

**7. Report** spec path, V used, edits per section, questions left open. End with next command per project rules; default `stitch-extract-design-md`.
