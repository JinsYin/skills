---
title: Field errors need a border, a message and live clearing
impact: HIGH
tags: form, validation, error, accessibility
---

## Field errors need a border, a message and live clearing

When a field fails validation, do all three — none of them is optional:

1. Switch the input border to the error color.
2. Show a specific message **directly below that input**.
3. Clear the field's error state **as the user types again**.

A colored border with no text tells the user something is wrong but not what. Errors collected
at the top of the form, or in a toast, leave them to map each message back to a field.

Be specific: `手机号需为 11 位数字`, not `格式不正确`.

```jsx
<input aria-invalid={!!error} className={error ? "border-destructive" : ""} />
{error && <p className="text-sm text-destructive mt-1">{error.message}</p>}
```
