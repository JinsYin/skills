---
name: write-fspec
description: "Derive the 功能规格说明书 (functional spec) from the product prototype and keep it versioned under products/fspec/: Flyway-style V files plus a merged CURRENT.md. Use when a prototype is finalized, changed or backfilled, when a draft V is confirmed or CURRENT.md lags, or when the user mentions 功能规格, 功能规格说明书 or fspec. Not for the feature spec (.scratch/*/spec.md) or DESIGN.md."
argument-hint: "[<prototype>]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# write-fspec

Maintain 功能规格说明书: per product line, which pages and features exist, how each behaves, how that evolved. Prototype is structural source of truth; fspec records what it shows plus what it cannot: preconditions, empty/error/no-permission states, extreme values, roles, terms, don'ts. Readers: `design-to-code` (undrawn states), whoever corrects feature spec or writes tickets, humans tracing history. Call document 功能规格说明书; reply in Chinese.

Codex: `$ARGUMENTS` = text after command. No interactive picker → print numbered options, stop for user's reply; never answer own question.

## Layout

```
products/fspec/
└── <line>/              # one V chain per product line, numbered independently
    ├── CURRENT.md       # merged current state, written only by step 6
    ├── V1__baseline.md  # full baseline
    └── V2__<slug>.md    # deltas
```

History needs deltas; consumers need full current state. Handing V1 + V2 to builder makes it draw V1 fields V2 already renamed, hence two tracks.

| File | Read when |
|---|---|
| `references/spec-format.md` | Before writing any V: naming, frontmatter, locators, operations, chapters |
| `references/templates.md` | Drafting: skeletons for V1, Vn, `CURRENT.md` |
| `references/merge.md` | Step 6: applying V to `CURRENT.md` |

## Rules

1. Only step 6 writes `CURRENT.md`; hand edit desyncs tracks, lost on next merge.
2. `active` V is frozen: changed requirement becomes next V. Only `draft` is edited.
3. Every locator resolves against `CURRENT.md` (`ADD`: must not exist). Unresolved → stop, ask; guess leaves phantom page nobody notices.
4. Write what exists and how it behaves. No hex, px, fonts or spacing: visuals live in `products/design/DESIGN.md`. No internal codenames or service names: use outward terms in project `CLAUDE.md`; builders copy text verbatim.

## Workflow

`$ARGUMENTS`: optional prototype path, default `products/prototype/` per Design convention; `<prototype>` below means it.

**1. Locate.**
- `products/specs/` without `products/fspec/` = legacy product-spec layout: propose `git mv products/specs products/fspec`, stop until confirmed.
- Product line: one dir → it; several, none named → ask; none → derive from prototype's app dirs, ask when ambiguous.
- No `V1__baseline.md` → baseline mode. Latest V `draft` → resume it at step 4. Else change mode, next version N+1.

**2. Gather evidence** before asking anything:
- Prototype. Baseline: all of `<prototype>`. Change: `git log -1 --format=%H -- products/fspec/<line>/V<N>__*.md`, then `git diff <hash> -- <prototype>` (includes uncommitted work) with this line's `## [Unreleased]` entries in `<prototype>/CHANGELOG.md`. Backfilled frontend drift in that range belongs to this V. Empty diff → report nothing to record, stop.
- `CURRENT.md` (change mode): current state; read it instead of replaying V chain.
- Feature spec (`.scratch/*/spec.md`), if user names one: 动机 and Out of Scope (→ 明确不做).
- Project `CLAUDE.md`: outward terms, banned codenames.

Reuse page ids from prototype or code (`apps`, `complianceStats`), never invent: only hard anchor between spec and implementation.

**3. Draft** `V<n>` with `status: draft` from skeleton. Baseline: seven chapters, six subsections per page. Change: every 变更清单 row has operation, locator, one-line note; new pages in full; modified pages as deltas naming subsection they replace. Prototype shows it → write it; cannot show → `<!-- TODO: 待确认 -->`, never invented.

**4. Resolve.** Check every locator (rule 3). Ask all TODOs in one round, fill in answers. Done when every locator resolves, no TODO remains.

**5. Confirm.** Show 变更摘要 and 变更清单. Only on user's confirmation:
- Set `status: active`.
- Cut prototype version, so prototype and spec versions match, in `<prototype>/CHANGELOG.md` (Keep a Changelog):
  - Add `## [V<n>] - <today>` right below `## [Unreleased]`; move `[Unreleased]` entries under it, keeping their `###` groups.
  - Several product lines share file: heading `## [<Line> V<n>] - <today>`, line capitalized (`Console V2`); move only entries prefixed `**<Line>**：`, dropping prefix; delete emptied groups.
  - No `## [Unreleased]`: leave file as is, say so in report.

Unconfirmed → stays `draft`; `CURRENT.md` and CHANGELOG untouched.

**6. Merge** per `references/merge.md`. Baseline: `CURRENT.md` = V1 under generated header. Change: apply only this V to `CURRENT.md`; full replay from V1 only when asked or when `synthesized_from` misses active V.

**7. Report** V path, operation counts, pages touched, whether `CURRENT.md` merged, prototype version cut.

## Related skills

- Markdown style: `doc-writing-best-practices`.
- Interaction conventions (validation timing, overlay reset, destructive confirmation, pagination, formats): `ui-ux-best-practices` wins over anything spec invents.
