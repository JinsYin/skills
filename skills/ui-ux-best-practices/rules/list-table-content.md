---
title: Align table content and empty states
impact: HIGH
impactDescription: Empty cells and empty tables need distinct, predictable states
tags: list, table, alignment, empty-state
---

## Align table content and empty states

- Left-align **both** headers and cells, and add no extra left padding inside cells.
- Render `-` for empty cells and for missing values on detail pages.
- When a list table has no data, display `暂无数据` in Chinese UI or `No data` in English UI,
  centered across the table. This empty-state message is the exception to the default
  left-alignment rule.

A blank cell cannot be told apart from three different situations: there is no data, the load
failed, or the rendering is broken. `-` states plainly that there is no value. The explicit
empty state distinguishes “no records” from loading, failed rendering or a broken request.

A header aligned differently from its content blurs the column boundary and makes the eye jump
rows while scanning.

```jsx
<th className="text-left">机构名称</th>
<td className="text-left">{org.name || "-"}</td>
<tr><td colSpan={columns.length} className="text-center">暂无数据</td></tr>
```

If a numeric column is right-aligned so digits line up, right-align its header too.
