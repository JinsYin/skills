---
title: Reset overlay state on close
impact: CRITICAL
impactDescription: Stale values submitted as a new record
tags: overlay, modal, drawer, form, state
---

## Reset overlay state on close

A create/edit modal or drawer that is closed and opened again must come back clean: input
values cleared, validation errors cleared, defaults restored.

Leftover state is not a cosmetic issue — the user believes they are creating a record while
submitting fields carried over from the previous one. Manual testing rarely reproduces it,
because testers reload the page instead of closing and reopening the overlay.

**Wrong** — closing only hides the overlay, the form state survives:

```jsx
<Dialog open={open} onOpenChange={setOpen} />
```

**Right** — reset explicitly on close, or force a remount with `key`:

```jsx
<Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) form.reset(defaults); }} />

{open && <UserFormDialog key={editingId ?? "new"} />}
```
