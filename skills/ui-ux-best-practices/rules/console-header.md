---
title: Console header and global chrome
impact: LOW
tags: console, header, layout, auth, navigation
---

## Console header and global chrome

- Header, in order: the logo, then the Chinese platform name, then a `Console` label **on a new
  line** below it.
- Top right: the user avatar, with logout reachable from it.
- Unless a product requirement explicitly calls for them, do not include a **global search** or
  **notification center** by default. Add either only when a defined user task requires it.

`Console` sits on its own line so the platform name stays the primary title instead of growing
into one long string. Keeping optional global features out of the shell preserves focus and
avoids adding navigation that no defined task requires.

Logout must be reachable from every page — an admin session left open on a shared machine is
the failure this prevents.
