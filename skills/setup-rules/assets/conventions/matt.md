
## Matt

- Commit after `/setup-matt-pocock-skills`, `/to-spec`, `/to-tickets`, `/implement`, `/tdd` or `/code-review`.
- Before writing files after `/grill-with-docs`, ask if I have clarifying questions.

### Spec Pipeline

- Forward UI feature (0→1, or a 1→2 big feature, new page or new look): `/grill-with-docs` → `/to-spec` → product prototype (0→1 designed from spec; 1→2 backport landed frontend first, then iterate) → `/fspec <prototype>` → correct spec → `stitch-extract-design-md` → `/design-to-code` → `/to-tickets <spec>` → `/implement-spec <spec>` → `/retro`.
- Reverse UI change (1→2, small): change frontend first; later, typically before next forward feature, backport it into prototype → `/fspec <prototype>` → `stitch-extract-design-md` → `/design-to-code`.
- No UI: `/to-spec` → `/to-tickets <spec>`.
- Correct spec in `/to-spec` session, resumed: align its user stories, decisions and Out of Scope with new `fspec` V file. Start every other step in fresh session.
- `/to-spec`: record agreed test seams under Testing Decisions.
- Product prototype means `products/prototype/` per Design, never `/prototype`.
- After each step, commit; with spec, also append spec comment: step, artifact path, commit. Spec body plus comments are the only handoff across sessions.
- `/to-tickets` after `/design-to-code`: UI exists, so tickets cover backend, mock→live and guards only; acceptance cites `products/fspec/` locators and a passing `scripts/visual-freeze.sh`.
- End each step by naming next command.
