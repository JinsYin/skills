
## Matt

- Commit after `/setup-matt-pocock-skills`, `/to-spec`, `/to-tickets`, `/implement`, `/tdd` or `/code-review`.
- Before writing files after `/grill-with-docs`, ask if I have clarifying questions.

### Spec Pipeline

- Forward UI feature (0→1, or a 1→2 big feature, new page or new look): `/grill-with-docs` → `/to-spec` → product prototype (0→1 designed from spec; 1→2 `/backfill-prototype` first, then iterate) → `/write-fspec <prototype>` → `/re-spec <spec>` → `stitch-extract-design-md` → `/design-to-code` → `/to-tickets <spec>` → `/implement-spec <spec>` → `/retro`.
- Reverse UI change (1→2, small): change frontend first; later, typically before next forward feature, `/backfill-prototype` → `/write-fspec <prototype>` → `stitch-extract-design-md` → `/design-to-code`.
- No UI: `/to-spec` → `/to-tickets <spec>`.
- Start every step in fresh session. `/re-spec <spec>` may instead run in resumed `/to-spec` session when spec reasoning lives only there.
- `/to-spec`: record agreed test seams under Testing Decisions.
- Product prototype means `products/prototype/` per Design, never `/prototype`.
- After each step, commit; with spec, also append spec comment: step, artifact path, commit. Spec body plus comments are the only handoff across sessions.
- `/to-tickets` after `/design-to-code`: UI exists, so tickets cover backend, mock→live and guards only; acceptance cites `products/fspec/` locators and a passing `scripts/visual-freeze.sh`.
- End each step by naming next command.

### Implement

- `/implement <ticket>` from `/to-tickets`: in implementation commit, tick each met acceptance box in ticket file, set its Status to `resolved`. Any box unmet → leave unticked, keep status, report why.
- `/implement` with no spec or ticket (quick task): commit code, then append row to `## Quick Tasks` in `.scratch/state.md` (create file or section if missing), commit that row alone:

  ```markdown
  ## Quick Tasks

  | ID | Description | Commit | Status |
  |---|---|---|---|
  | 261029-k3x | Fix login button on mobile Safari | a1b2c3d | resolved |
  ```

  - ID: `YYMMDD-xxx`, local date + seconds since midnight ÷ 2 in base36, zero-padded to 3 chars.
  - Commit: code commit's short hash.
  - Status: `resolved`; set `reverted` if commit later reverted.
