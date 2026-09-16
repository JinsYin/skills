---
title: Confirm destructive actions with a custom modal
impact: CRITICAL
impactDescription: Irreversible deletion by reflex
tags: overlay, modal, destructive, confirm
---

## Confirm destructive actions with a custom modal

Delete, disable and other irreversible actions must open a custom confirmation modal — never
the native `alert` / `confirm`.

Native dialogs cannot say *what* is being removed or how much it affects, and their styling is
out of your control, so users click through them by reflex.

**Wrong:**

```js
if (confirm("确定删除？")) deleteUser(id); // does not say who gets deleted
```

**Right — name the object and the consequence:**

```html
<h2>删除用户「张三」？</h2>
<p>该用户的 12 条授权记录将一并移除，此操作不可恢复。</p>
```

Give the confirm button the destructive color, and do **not** make it the default focus —
pressing Enter must not be able to delete.
