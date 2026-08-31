
## Superpowers

### Paths

- Never auto-invoke `using-superpowers`.
- Spec lives at `docs/superpowers/specs/<milestone>-<topic>.SPEC.md`; everything else under `docs/superpowers/plans/<milestone>/`.
- Name files `ROADMAP.md`, `<phase-num>-<plan-num>-<feature-name>.PLAN.md`, `<phase-num>-00.PATTERN.md`, `<plan-basename>.SUMMARY.md`.
- Write `<milestone>` as `m1`; write phase and plan numbers as 2 digits, plan number restarting each phase (`01-01`, `02-01`).
- Put `**Spec:** <path>` in the preamble of the roadmap and of every plan, plus `**Roadmap:** <path>` in every plan, anywhere before the first `##`.

### Roadmap

- Sections: target scope, confirmed decisions, plan checklist, global constraints, plus whatever the milestone needs.
- Checklist entry: phase · plan ID `<phase-num>-<plan-num>` · topic · modules · spec chapters · prerequisite plans · deliverables · completion status.
- `completion status` is `pending`, `planned` or `executed` — created as `pending`, advanced one step at a time, never reversed.

### Plan Flow

- After `brainstorming`, save the spec, run `writing-plans` for the roadmap in the same session, then recommend a new session for the phase plans.
- The approved spec is truth; the roadmap's scope and phase boundaries are fixed up front.
- No roadmap yet → write it this run and stop; otherwise plan exactly one phase, and only after the previous phase has executed.
- Draft against the code that phase landed, never an earlier plan's text.
- 2–5 tasks per plan, each a vertical slice, splitting any task that touches >5 files, spans two subsystems, or mixes discovery with implementation.
- End the run by flipping that phase's entries `pending` → `planned`, then fixing — not reporting — every check below.
- Require `grep -nE '^[[:space:]]*(package|import) ' <file>` to print nothing for every file the run wrote.
- Keep every `xml`/`yaml`/`properties`/`json` fence in a plan at 20 lines or fewer, exempting `<phase-num>-00.PATTERN.md` from that cap but never from the import ban.
- Require every `planned` entry to have a matching `.PLAN.md`, and every entry without one to read `pending`.

### Task Anatomy

- Order each task's headers `**Files:**`, `**Read first:**`, `**Interfaces:**`, `**Done:**`, then the steps.
- `**Read first:**` = files the task modifies, plus the spec chapters and upstream `Interfaces · Produces` that are truth.
- Keep `**Interfaces:**` exact, and put only verifiable assertions in `**Done:**` — source greps, observable behavior, test commands, CLI output — never subjective wording.
- Write every step as a `- [ ]` checkbox on the TDD cycle: run steps give the exact command and exact expected failure, implementation steps give signatures and the few non-obvious decisions but never a method body.
- Name concrete files, types, methods and constants throughout.
- Paste only what the executor cannot derive: test method bodies, frozen fixtures, one worked example per repeating pattern, the exact lines an existing build or config file gains.
- Write out test infrastructure in full — it is its own contract.
- Never paste a `package`, `import` or license-header line even inside test code — state package placement once in `**Interfaces:**`, and give a non-obvious static import one prose clause.
- For a newly created build or config file, give coordinates, a property/dependency/plugin table, and only the blocks `**Done:**` verifies verbatim.
- Hoist boilerplate skeletons and any snippet two tasks share into `<phase-num>-00.PATTERN.md`.
- Turn homogeneous cases into an input/expectation table, and describe a README as the sections it must cover.

### Execution

- Run `subagent-driven-development` over one plan or a whole phase, executing a phase's plans on one branch in checklist order with a single whole-branch review at the end.
- After that review and the required verification pass, synthesize — never copy — `.superpowers/sdd/<plan-basename>/` into `<plan-basename>.SUMMARY.md`, one per executed plan.
- Flip those entries `planned` → `executed` in `ROADMAP.md`, then commit the summaries and that edit and nothing else.
- Then invoke `finishing-a-development-branch` and choose `Merge back to <base-branch> locally` at `Present Options`, or `Keep as-is` on a detached HEAD where that option is absent.
- Commit after `brainstorming`, `writing-plans`, `executing-plans` or `subagent-driven-development`.
