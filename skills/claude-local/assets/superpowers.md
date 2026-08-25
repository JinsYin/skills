
## Superpowers

- After completing the spec review in `brainstorming`, do not automatically invoke or ask for approval to invoke `writing-plans`; instead, recommend invoking it in a new session.
- Save `brainstorming` design specs to `docs/superpowers/specs/<spec-num>-<topic>-design.md` (`<spec-num>`: 2-digit, zero-padded).
- In `writing-plans`, cap plans at 2–4 tasks and split larger specs into sequential `<plan-num>` plans saved to `docs/superpowers/plans/<spec-num>-<plan-num>-<feature-name>.md`; for multiple plans, first save `docs/superpowers/plans/<spec-num>-00-<topic>-roadmap.md` defining their scope.
- After final whole-branch review passes in `subagent-driven-development`, copy and commit all `*.md` files from `.superpowers/sdd/<plan-basename>/` to `docs/superpowers/plans/<plan-basename>/` before source deletion or `finishing-a-development-branch`; otherwise preserve the source and stop.
- At `Present Options` in `finishing-a-development-branch`, always choose `Merge back to <base-branch> locally`, without presenting other options.
