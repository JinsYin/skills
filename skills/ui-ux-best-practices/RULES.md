---
description: Frontend form UI/UX. All React / Vue files.
paths:
  - "**/*.vue"
  - "**/*.jsx"
  - "**/*.tsx"
  - "**/*.css"
---
# UI/UX Rules

## Global

- Default UI language: Chinese.
- Use a 32x32 logo on every page.
- Email domain: `@shdatagroup.com`.
- Do not use comma separators in numbers.
- Never expose internal project codenames; show the Chinese platform name.
- Date format: `2026-04-23`; datetime format: `2026-04-23 09:00:00`.
- List pages must paginate and show the total count at top right.
- Pagination must use windowed page numbers — never render all pages. Always show the first and last page, the current page with 1 page on each side, and a non-clickable `…` ellipsis at any gap (e.g. `< 1 … 49 50 51 … 103 >`).
- Every page must include a favicon.

- Validation: validate on `blur`; once invalid, revalidate on `change`; validate all fields on `submit`. Live hints, such as password strength, use `change`.
- Errors: use an error border, show a specific message below the field, and clear the field error as the user types.
- Disable browser autofill: set form/input `autocomplete="off"` and password fields `autocomplete="new-password"`.
- Form validation behavior: use the mainstream hybrid validation strategy: first validate on blur, switch to real-time validation on change after an error appears, validate again on submit as a fallback, and use on change directly for auxiliary feedback such as password strength hints.
- Form error messages: for inputs that fail validation, (1) switch the border to the error-state color; (2) show a specific error message directly below the input; (3) clear that field's error state in real time when the user types again.
- Form autocomplete: disable autocomplete and prevent the browser from autofilling form data.
- When a form field is not editable, gray out the text inside the input, not the input itself, and show a not-allowed cursor on hover.
- Toast notifications must show both an icon and text, and the icon color must vary by severity level.
- Password inputs must have an eye icon that toggles the value between plaintext and masked on click.

## Console / Admin

- Build the console as one HTML page; use anchors for menu sections.
- List toolbar order: search first, filters next, icon-only refresh last.
- Left-align all table headers and cells; avoid extra left padding in cell content.
- Show `-` for empty table cells and missing detail values.
- Use a custom confirmation modal for destructive actions; never use `alert`.
- Mark required fields in create/edit forms.
- Explain special fields, such as code or password, in placeholders.
- Dropdowns must use custom searchable menus and default to all options.
- Keep each table action cell consistent: icons or text, not a mixed style.
- Header: logo, Chinese platform name, then a new-line `Console` label.
- Top right must show the user avatar and provide logout.
- The backdrop color/opacity outside a drawer must match the backdrop color/opacity outside a modal.
- Create, edit, and view modals/drawers must share the same width and height.
- After closing a create/edit modal/drawer, reopening it must reset the form state (clear input values and error messages).
- Buttons or actions with the same function must use a consistent icon (style specifically, and size too unless otherwise noted) — including create, edit, delete, copy, refresh, close drawer/modal, search, disable, publish/unpublish, password reveal, etc.
