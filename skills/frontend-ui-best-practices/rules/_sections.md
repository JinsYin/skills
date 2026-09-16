# Sections

Defines every category, its order, impact level and scope. The ID in parentheses is the
filename prefix of that category's rules.

Impact is graded by **what a violation costs the user**:

| Level | Meaning |
|---|---|
| CRITICAL | Data loss, or an irreversible wrong action |
| HIGH | The user cannot finish the task, or is actively misled |
| MEDIUM | The task is doable, but at extra cognitive cost |
| LOW | Inconsistent look and feel |

---

## 1. Stack & Structure (stack)

**Impact:** LOW
**Description:** Dependency choices, project structure and module documentation. Breaks no single screen, but decides whether a newcomer or an agent can tell what belongs in a package and why a dependency is there.
