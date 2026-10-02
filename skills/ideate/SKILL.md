---
name: ideate
description: Clarify product ideas into docs/ideas/idea.md, migrating legacy requirement docs.
disable-model-invocation: true
---

# ideate

Turn product ideas and context into a traceable product concept: every fact traces to a source. Read [references/idea-structure.md](references/idea-structure.md) before working; it defines the four sections, required fields, and template.

## Rules

- Sources: user statements, the current conversation, explicitly named local materials, and existing concept documents. Record only facts from these; ask about anything else instead of guessing features, choices, deliverables, competitors, or links.
- Carry over the user's qualifiers, constraints, exclusions, and reference-only wording with their meaning intact.
- Keep product intent, delivery forms, research targets, and technical references in their own sections: internal modules are not deliverables, references are not selected technology, and 待调研 is not 已支持.
- Research competitors or select technology only when the user asks.
- Missing values: write `> 无` when the user confirms none or not applicable; write `待定：<事项>` when the user confirms it is undecided. Every heading carries content or one of these markers.

## Workflow

1. Project root: the Git root, else the current directory. Target: `<project-root>/docs/ideas/idea.md`; create only `docs/ideas/` when needed.
2. Legacy sources: read every existing `<project-root>/docs/requirements/raw.md` and `<project-root>/REQUIREMENTS.md` and migrate all confirmed content. When sources conflict, record both positions as questions for the user.
3. Existing target: read it fully and decide whether the user wants an update, restructure, replacement, or migration; when unclear, ask before writing. Keep its confirmed content unless the user supersedes it.
4. Sort each input fact as confirmed, proposal, or open question, then place it in its single best section.
5. Audit every required field in the reference. Ask at most four related questions per round, then wait. Write only after every required field is answered or carries a missing-value marker.
6. Write the target with the reference title, note, and all four numbered sections. Use readable link text and only user-provided or explicitly requested URLs.
7. Reread the target against Validation. Only then delete each migrated legacy source; if deletion would discard unrelated uncommitted edits, stop and ask.
8. Report the target path, removed legacy paths, and remaining `> 无` / `待定` items. Commit only when asked.

## Validation

- Title, note, four numbered sections, and required subsections match the reference.
- Every Rule holds; every fact appears once, traces to a source, and every conflict is resolved by the user or listed as a question.
