---
name: ideate
description: Turn a user's product ideas, conversations, and referenced context into a clarified product concept under the project root at docs/ideas/idea.md. Separate confirmed direction, constraints, research targets, and implementation references; ask about missing, ambiguous, or conflicting facts before writing. Use for product ideation, concept capture, updates, and migration of legacy docs/requirements/raw.md or REQUIREMENTS.md.
---

# ideate

Turn product ideas and context into a traceable product concept document.

## Rules

- Treat user statements, the current conversation, explicitly named local materials, and existing concept documents as sources of truth.
- Separate confirmed product intent from context proposals, research targets, and technical references. Do not invent features, choices, deliverables, competitors, or links.
- Preserve qualifiers and surface missing, ambiguous, or conflicting facts. Never guess.
- Do not perform unsolicited competitor research or technical selection.

Read [references/idea-structure.md](references/idea-structure.md) before working.

## Workflow

1. Use the triggering message and explicitly referenced context as input.
2. Find the project root: prefer the Git root; otherwise use the current directory.
3. Use `<project-root>/docs/ideas/idea.md` as the target. Create only `docs/ideas/` when needed.
4. Check for legacy sources at `<project-root>/docs/requirements/raw.md` and `<project-root>/REQUIREMENTS.md`. Read every source that exists and migrate all confirmed content into the target. If multiple sources conflict, preserve both positions as items to confirm; never choose silently.
5. If the target already exists, read it fully and determine whether the user wants an update, restructure, replacement, or migration. Do not overwrite it when intent is unclear.
6. Classify input as confirmed product intent, context proposals, external research, or open questions before writing.
7. Map the input to the four sections defined in the reference. Keep each fact in its best section; do not present internal modules as deliverables or references as selected technology.
8. Audit every required field in the reference. Ask no more than four related questions per round, then wait. Proceed only after required fields are answered or explicitly marked none, not applicable, or undecided.

## Output

Write `docs/ideas/idea.md` using the reference template:

- Use `# <项目名称> - 产品构想` as the title.
- Use the reference note explaining that this is an early product exploration record and that unresolved items are marked for later conversion into a formal product specification.
- Keep all four numbered sections and their required subsections.
- Mark confirmed undecided items as `待定：...`; do not leave empty headings, `TODO`, or placeholders.
- Use readable Markdown link text and only user-provided or explicitly requested URLs.
- Preserve existing confirmed content unless the user supersedes it.

After writing, reread and validate the target. Remove each legacy source only after its content has been successfully migrated and the target passes validation. If removal would discard unrelated uncommitted edits, stop and ask the user. Report the target path, migrated legacy paths, and remaining `无` / `不适用` / `待定` items. Do not commit unless the user explicitly asks.

## Validation

- All four numbered sections and the required heading hierarchy are present.
- No empty sections, placeholders, unshown inferences, duplicated facts, or unresolved silent conflicts remain.
- Product intent, delivery form, research, and technical references stay separate.
- User constraints, exclusions, and reference-only wording are preserved.
- The target path is correct and legacy files were removed only after successful migration.
