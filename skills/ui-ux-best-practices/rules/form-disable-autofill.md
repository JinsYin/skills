---
title: Turn off browser autofill
impact: MEDIUM
tags: form, autocomplete, security
---

## Turn off browser autofill

- Set `autocomplete="off"` on the form and its inputs.
- Set `autocomplete="new-password"` on password inputs.

In an admin console the browser guesses wrong constantly — it drops the login password into the
password field of a "create user" form, or a personal address into a customer email field, and
the user submits without checking.

Password fields need `new-password` rather than `off`: mainstream browsers ignore `off` on
password inputs.

```html
<form autocomplete="off">
  <input name="email" autocomplete="off" />
  <input name="password" type="password" autocomplete="new-password" />
</form>
```
