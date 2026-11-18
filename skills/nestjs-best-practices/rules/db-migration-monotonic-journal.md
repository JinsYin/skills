---
title: Regenerate migrations after rebase so journal timestamps stay increasing
impact: HIGH
impactDescription: Migrations older than the last applied one are skipped silently
tags: db, migration, drizzle, journal, rebase, branch
---

## Regenerate migrations after rebase so journal timestamps stay increasing

The migrator runs a file only when its journal `when` is **strictly greater** than the latest `created_at` already stored. A migration rebased into history with an older `when` is skipped. The API then boots against a schema that is missing those columns, and no error names the skipped file.

After a rebase or a merge that reorders unapplied migrations, regenerate them so every new `when` is greater than the newest timestamp already applied on shared environments. Do not hand-edit `when` backwards to force an order. Do not "fix" a skip by deleting `__drizzle_migrations` rows.

Check before merge: the new journal entries sort after `max(created_at)` from the staging database.
