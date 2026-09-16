---
title: Console header and account area
impact: LOW
tags: console, header, layout, auth
---

## Console header and account area

- Header, in order: the logo, then the Chinese platform name, then a `Console` label **on a new
  line** below it.
- Top right: the user avatar, with logout reachable from it.

`Console` sits on its own line so the platform name stays the primary title instead of growing
into one long string.

Logout must be reachable from every page — an admin session left open on a shared machine is
the failure this prevents.
