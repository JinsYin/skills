---
title: Tell the user how to fill a field before they submit
impact: MEDIUM
tags: form, placeholder, required, dropdown, password
---

## Tell the user how to fill a field before they submit

- **Mark required fields** in create and edit forms.
- Explain special fields — code, password — in the **placeholder** (e.g. `6-20 位字母或数字`),
  not in an error message after submit.
- Use a custom **searchable** dropdown that shows all options by default; a native `select`
  cannot be searched once it holds more than a dozen entries.
- Password inputs carry an **eye icon** that toggles the value between plaintext and masked.

Each of these puts the information where the user needs it — before typing, not after a failed
submit. The eye toggle matters most where there is no "confirm password" field: it is the only
way to check what was typed.
