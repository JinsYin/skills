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

## 1. Overlays & Destructive Actions (overlay)

**Impact:** CRITICAL
**Description:** Confirmation dialogs, modal and drawer state. A delete without confirmation, or an overlay that reopens holding the previous record, leads straight to wrong deletions and wrong submissions.

## 2. Forms (form)

**Impact:** HIGH
**Description:** Validation timing, error display, autofill, read-only state and input affordances. The wrong validation strategy is the single largest cause of form abandonment.

## 3. Lists & Tables (list)

**Impact:** HIGH
**Description:** Pagination, alignment, empty values, toolbar order. Rendering every page number freezes the page once the dataset grows.

## 4. Formats & Wording (format)

**Impact:** MEDIUM
**Description:** Date, number and language presentation. Inconsistency makes users misread values.

## 5. Visual Consistency (consistency)

**Impact:** LOW
**Description:** Icons, toasts and page chrome. No functional impact, but a constant recognition tax.

## 6. Console Layout (console)

**Impact:** LOW
**Description:** Structure and header composition of the admin console.
