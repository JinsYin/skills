---
title: Hybrid validation — blur first, change after an error, submit as fallback
impact: HIGH
impactDescription: The largest cause of form abandonment
tags: form, validation, ux
---

## Hybrid validation: blur first, change after an error, submit as fallback

| Trigger | Behavior |
|---|---|
| `blur` | First validation of the field |
| `change` | Real-time revalidation **only after that field has errored** |
| `submit` | Validate every field as a fallback |
| `change` | Auxiliary feedback (password strength) — always live |

Both extremes fail. Validating only on submit tells the user about the first field after they
filled in ten. Validating on `change` from the start complains about input that is not finished
being typed.

The hybrid order avoids both: silent until the field errors, immediate confirmation afterwards
that the fix worked.

```js
useForm({ mode: "onBlur", reValidateMode: "onChange" });
```
