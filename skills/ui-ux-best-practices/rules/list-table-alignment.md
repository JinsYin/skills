---
title: Left-align table content, show a dash for empty values
impact: MEDIUM
tags: list, table, alignment, empty-state
---

## Left-align table content, show a dash for empty values

- Left-align **both** headers and cells, and add no extra left padding inside cells.
- Render `-` for empty cells and for missing values on detail pages.

A blank cell cannot be told apart from three different situations: there is no data, the load
failed, or the rendering is broken. `-` states plainly that there is no value.

A header aligned differently from its content (centered header over left-aligned cells) blurs
the column boundary and makes the eye jump rows while scanning.

```jsx
<th className="text-left">机构名称</th>
<td className="text-left">{org.name || "-"}</td>
```

If a numeric column is right-aligned so digits line up, right-align its header too.
