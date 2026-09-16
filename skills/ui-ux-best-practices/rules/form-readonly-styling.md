---
title: Gray out the text of a read-only field, not the input
impact: MEDIUM
tags: form, readonly, disabled, ux
---

## Gray out the text of a read-only field, not the input

When a field is not editable, gray the **text inside** the input, leave the input itself at
normal contrast, and show a `not-allowed` cursor on hover.

Graying the whole control makes it recede into the background and its value hard to read — yet
these values (a generated code, the current organization) are usually exactly what the user
came to read.

```jsx
<input readOnly value={code} className="text-muted-foreground cursor-not-allowed" />
```
