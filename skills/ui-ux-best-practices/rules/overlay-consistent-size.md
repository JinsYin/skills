---
title: Keep overlay size and backdrop consistent
impact: LOW
tags: overlay, modal, drawer, consistency
---

## Keep overlay size and backdrop consistent

- The create / edit / view overlays of one resource share the same width and height.
- A drawer's backdrop color and opacity match the backdrop of a modal.

Size jumps make the user re-locate the content every time they switch action; a different
backdrop reads as a different layer of the interface.

Keep the size in one shared constant instead of per-overlay values:

```jsx
const DIALOG_SIZE = "sm:max-w-2xl min-h-[520px]"; // create / edit / view
```
