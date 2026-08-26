
## Superpowers

- Do not automatically invoke `using-superpowers`.
- After completing `brainstorming`, automatically use the approved spec to generate a plan map and save it to `docs/superpowers/plans/<spec-num>-00-<topic>-roadmap.md`; recommend `writing-plans` for the next session without invoking it automatically or asking for approval.
- The plan map must place `**Spec:** <source>` immediately below the title, include sections for the target scope, confirmed decisions, a plan checklist, global constraints, and other necessary content, and include the plan ID `<spec-num>-<plan-num>`, topic, involved modules, corresponding specification chapter(s), prerequisite plans, deliverables, and output status in each checklist entry.
- Save `brainstorming` design specs to `docs/superpowers/specs/<spec-num>-<topic>-design.md` (`<spec-num>`: 2-digit, zero-padded).
- In `writing-plans`, use the approved spec as the source of truth and the roadmap as the scope and sequencing guide; place `**Spec:** <source>` and `**Roadmap:** <path>` immediately below the title of every plan file; cap plans at 2–4 tasks and split larger specs into sequential `<plan-num>` plans saved to `docs/superpowers/plans/<spec-num>/<spec-num>-<plan-num>-<feature-name>.md`.
- After final whole-branch review passes in `subagent-driven-development`, copy and commit all `*.md` files from `.superpowers/sdd/<plan-basename>/` to `docs/superpowers/plans/<spec-num>/<plan-basename>/` before source deletion or `finishing-a-development-branch`; otherwise preserve the source and stop.
- At `Present Options` in `finishing-a-development-branch`, always choose `Merge back to <base-branch> locally`, without presenting other options.
