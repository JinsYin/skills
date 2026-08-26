## Superpowers

- No auto-invoke `using-superpowers`.
- After `brainstorming` done: auto use approved spec → generate plan map → save `docs/superpowers/plans/<spec-num>-00-<topic>-roadmap.md`. Recommend `writing-plans` for next session. No auto-invoke it, no ask approval.
- Plan map must: put `**Spec:** <source>` right below title; have sections for target scope, confirmed decisions, plan checklist, global constraints, other needed content. Each checklist entry carry: plan ID `<spec-num>-<plan-num>`, topic, modules involved, matching spec chapter(s), prerequisite plans, deliverables, output status.
- Save `brainstorming` design specs → `docs/superpowers/specs/<spec-num>-<topic>-design.md` (`<spec-num>`: 2-digit, zero-padded).
- In `writing-plans`: approved spec = source of truth, roadmap = scope + sequencing guide. Put `**Spec:** <source>` and `**Roadmap:** <path>` right below title of every plan file. Cap 2–4 tasks per plan; split bigger specs into sequential `<plan-num>` plans → `docs/superpowers/plans/<spec-num>/<spec-num>-<plan-num>-<feature-name>.md`.
- After final whole-branch review passes in `subagent-driven-development`: copy + commit all `*.md` from `.superpowers/sdd/<plan-basename>/` → `docs/superpowers/plans/<spec-num>/<plan-basename>/`, before source deletion or `finishing-a-development-branch`. Else keep source, stop.
- At `Present Options` in `finishing-a-development-branch`: always pick `Merge back to <base-branch> locally`. Show no other options.
