---
title: Toolbar order — search, filters, reset, refresh
impact: LOW
tags: list, toolbar, consistency
---

## Toolbar order: search → filters → reset → refresh

Fixed order: the search box first, filters next, **reset search and filters** next, and an
**icon-only** refresh button last. If horizontal space is insufficient, omit the reset and
refresh buttons.
With the order fixed, users moving between list pages never have to hunt for a control again.
Refresh goes last and stays icon-only because it is the least frequent action and should not
occupy the visual lead.

Keep each row's action cell in **one style** — all icons or all text, never mixed. Mixing makes
row height and visual weight uneven down the column.
