---
title: Toolbar order — search, filters, refresh
impact: LOW
tags: list, toolbar, consistency
---

## Toolbar order: search → filters → refresh

Fixed order: the search box first, filters in the middle, an **icon-only** refresh button last.
With the order fixed, users moving between list pages never have to hunt for a control again.
Refresh goes last and stays icon-only because it is the least frequent action and should not
occupy the visual lead.

Keep each row's action cell in **one style** — all icons or all text, never mixed. Mixing makes
row height and visual weight uneven down the column.
