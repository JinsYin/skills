---
title: UI language and public naming
impact: MEDIUM
tags: format, i18n, naming, security
---

## UI language and public naming

- The default UI language is **Chinese**.
- **Never expose internal project codenames** — always show the public Chinese platform name.
- Use `@shdatagroup.com` as the email domain in samples, defaults and generated addresses.

A leaked codename costs twice: it means nothing to the user, and it reveals how the internal
system is divided — useful information to anyone mapping the attack surface.

Codenames escape through the page title, error messages, displayed API paths, exported file
names and email templates. Check each of them when editing copy.
