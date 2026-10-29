# Merge

Step 6: apply one active V to `CURRENT.md`.

## Preconditions

- Versions contiguous; filename `V<n>__` matches `version`; `product` matches dir.
- `synthesized_from` lists every active version below n; otherwise run full replay below.

Any failure → stop, report, write nothing: half-right `CURRENT.md` gets treated as fact.

## Apply 变更清单 rows in table order

| Op | Do | Target check fails |
|---|---|---|
| `ADD` | Insert V's full content; pages go into 页面规格 in nav order | Exists → ask whether it should be `MODIFY` |
| `MODIFY` | Replace named subsection or row wholesale; never append | Missing → list nearest locators |
| `RENAME` | Change name only | Same |
| `MOVE` | Cut, insert at new position; update 信息架构 nav tree | Same |
| `REMOVE` | Delete node and its children (`page.x` takes its fields and actions) | Same |

Rows hitting same target run in table order; `MODIFY` after `RENAME` uses new name.

## Cascades (`MOVE` / `REMOVE`)

| Trigger | Also |
|---|---|
| Group left empty | Delete group from 信息架构 |
| `REMOVE page.x` | Delete its column or row in role matrix |
| `REMOVE page.x` still mentioned by 关键流程 or 影响面 | Report as dangling; user decides |
| `REMOVE` / `RENAME` of term | Delete or rename it in 术语表 |

Apply only structural cascades; semantic edits to flows or terms go to user.

## Rename aliases

- `term.x` → rename, note `历史别名：<old>` in 术语表 备注 column.
- Field or action → no 术语表 entry; old name lives only in that V's 变更清单.

## Edge cases

- Chained rename: V2 renames A → B, so V3 must target B. Targeting A → error 「A 已在 V2 更名为 B」.
- `REMOVE` then `ADD` of same name: allowed, new node; provenance `V1 → V3（删除后重建）`.

## Write

- Generated comment on line 1, then frontmatter; update `synthesized_from` and `generated`.
- End each touched page section with provenance: `> 来源：V1 → V2（移动分组、字段改名）`, stating what happened to that page in each V, not V's title. Untouched pages keep theirs.
- Keep 明确不做 wording verbatim, adding and removing only V's items.

## Full replay

When asked, or sent here by preconditions: start from V1, apply every active V in ascending `version` order, not filename order (V10 sorts before V2).
