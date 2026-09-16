---
title: Build the console as a single HTML page
impact: LOW
tags: console, structure, navigation
---

## Build the console as a single HTML page

The admin console is one HTML page; menu entries jump to their section by **anchor** instead of
loading a separate document.

Navigation then costs no reload, and the whole console stays one artifact that can be reviewed
and handed over in a single file.
