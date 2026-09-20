# UI/UX Best Practices

> Generated from `rules/` by `scripts/build.sh`. Do not edit by hand.
> Generated at: 2026-09-19 19:34:26

## 1. Overlays & Destructive Actions


### Confirm destructive actions with a custom modal

Delete, disable and other irreversible actions must open a custom confirmation modal — never
the native `alert` / `confirm`.

Native dialogs cannot say *what* is being removed or how much it affects, and their styling is
out of your control, so users click through them by reflex.

**Wrong:**

```js
if (confirm("确定删除？")) deleteUser(id); // does not say who gets deleted
```

**Right — name the object and the consequence:**

```html
<h2>删除用户「张三」？</h2>
<p>该用户的 12 条授权记录将一并移除，此操作不可恢复。</p>
```

Give the confirm button the destructive color, and do **not** make it the default focus —
pressing Enter must not be able to delete.


### Keep overlay size and backdrop consistent

- The create / edit / view overlays of one resource share the same width and height.
- A drawer's backdrop color and opacity match the backdrop of a modal.

Size jumps make the user re-locate the content every time they switch action; a different
backdrop reads as a different layer of the interface.

Keep the size in one shared constant instead of per-overlay values:

```jsx
const DIALOG_SIZE = "sm:max-w-2xl min-h-[520px]"; // create / edit / view
```


### Reset overlay state on close

A create/edit modal or drawer that is closed and opened again must come back clean: input
values cleared, validation errors cleared, defaults restored.

Leftover state is not a cosmetic issue — the user believes they are creating a record while
submitting fields carried over from the previous one. Manual testing rarely reproduces it,
because testers reload the page instead of closing and reopening the overlay.

**Wrong** — closing only hides the overlay, the form state survives:

```jsx
<Dialog open={open} onOpenChange={setOpen} />
```

**Right** — reset explicitly on close, or force a remount with `key`:

```jsx
<Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) form.reset(defaults); }} />

{open && <UserFormDialog key={editingId ?? "new"} />}
```

## 2. Forms


### Turn off browser autofill

- Set `autocomplete="off"` on the form and its inputs.
- Set `autocomplete="new-password"` on password inputs.

In an admin console the browser guesses wrong constantly — it drops the login password into the
password field of a "create user" form, or a personal address into a customer email field, and
the user submits without checking.

Password fields need `new-password` rather than `off`: mainstream browsers ignore `off` on
password inputs.

```html
<form autocomplete="off">
  <input name="email" autocomplete="off" />
  <input name="password" type="password" autocomplete="new-password" />
</form>
```


### Field errors need a border, a message and live clearing

When a field fails validation, do all three — none of them is optional:

1. Switch the input border to the error color.
2. Show a specific message **directly below that input**.
3. Clear the field's error state **as the user types again**.

A colored border with no text tells the user something is wrong but not what. Errors collected
at the top of the form, or in a toast, leave them to map each message back to a field.

Be specific: `手机号需为 11 位数字`, not `格式不正确`.

```jsx
<input aria-invalid={!!error} className={error ? "border-destructive" : ""} />
{error && <p className="text-sm text-destructive mt-1">{error.message}</p>}
```


### Tell the user how to fill a field before they submit

- **Mark required fields** in create and edit forms.
- Explain special fields — code, password — in the **placeholder** (e.g. `6-20 位字母或数字`),
  not in an error message after submit.
- Use a custom **searchable** dropdown that shows all options by default; a native `select`
  cannot be searched once it holds more than a dozen entries.
- Password inputs carry an **eye icon** that toggles the value between plaintext and masked.

Each of these puts the information where the user needs it — before typing, not after a failed
submit. The eye toggle matters most where there is no "confirm password" field: it is the only
way to check what was typed.


### Gray out the text of a read-only field, not the input

When a field is not editable, gray the **text inside** the input, leave the input itself at
normal contrast, and show a `not-allowed` cursor on hover.

Graying the whole control makes it recede into the background and its value hard to read — yet
these values (a generated code, the current organization) are usually exactly what the user
came to read.

```jsx
<input readOnly value={code} className="text-muted-foreground cursor-not-allowed" />
```


### Hybrid validation: blur first, change after an error, submit as fallback

| Trigger | Behavior |
|---|---|
| `blur` | First validation of the field |
| `change` | Real-time revalidation **only after that field has errored** |
| `submit` | Validate every field as a fallback |
| `change` | Auxiliary feedback (password strength) — always live |

Both extremes fail. Validating only on submit tells the user about the first field after they
filled in ten. Validating on `change` from the start complains about input that is not finished
being typed.

The hybrid order avoids both: silent until the field errors, immediate confirmation afterwards
that the fix worked.

```js
useForm({ mode: "onBlur", reValidateMode: "onChange" });
```

## 3. Lists & Tables


### Use custom menus for filter dropdowns

Filter dropdowns must use a **custom menu** to display their options. Do not use the default
HTML `<select>` element directly.

The custom menu keeps option presentation, interaction and styling consistent across list pages.


### Paginate list pages and show total count

Every list page paginates and shows the **total count at the top right** — the user needs the
size of the result set to decide between paging through it and filtering it down.


### Align table content and empty states

- Left-align **both** headers and cells, and add no extra left padding inside cells.
- Render `-` for empty cells and for missing values on detail pages.
- When a list table has no data, display `暂无数据` in Chinese UI or `No data` in English UI,
  centered across the table. This empty-state message is the exception to the default
  left-alignment rule.

A blank cell cannot be told apart from three different situations: there is no data, the load
failed, or the rendering is broken. `-` states plainly that there is no value. The explicit
empty state distinguishes “no records” from loading, failed rendering or a broken request.

A header aligned differently from its content blurs the column boundary and makes the eye jump
rows while scanning.

```jsx
<th className="text-left">机构名称</th>
<td className="text-left">{org.name || "-"}</td>
<tr><td colSpan={columns.length} className="text-center">暂无数据</td></tr>
```

If a numeric column is right-aligned so digits line up, right-align its header too.


### Toolbar order: search → filters → reset → refresh

Fixed order: the search box first, filters next, **reset search and filters** next, and an
**icon-only** refresh button last. If horizontal space is insufficient, omit the reset and
refresh buttons.
With the order fixed, users moving between list pages never have to hunt for a control again.
Refresh goes last and stays icon-only because it is the least frequent action and should not
occupy the visual lead.

Keep each row's action cell in **one style** — all icons or all text, never mixed. Mixing makes
row height and visual weight uneven down the column.

## 4. Formats & Wording


### Date and number formats

| Type | Format | Example |
|---|---|---|
| Date | `YYYY-MM-DD` | `2026-04-23` |
| Datetime | `YYYY-MM-DD HH:mm:ss` | `2026-04-23 09:00:00` |
| Number | **no comma separators** | `1234567`, not `1,234,567` |

ISO order, not `04/23/2026` — the latter reads as April 23 in one region and as month 23
(invalid) in another, the most common misreading in cross-region work.

Numbers must not use comma separators because these values get copied into Excel or an API client,
where the separator breaks parsing. If one screen genuinely needs thousands separators for
readability, make it an explicit local exception rather than the global default.


### UI language and public naming

- The default UI language is **Chinese**.
- **Never expose internal project codenames** — always show the public Chinese platform name.
- Use `@shdatagroup.com` as the email domain in samples, defaults and generated addresses.

A leaked codename costs twice: it means nothing to the user, and it reveals how the internal
system is divided — useful information to anyone mapping the attack surface.

Codenames escape through the page title, error messages, displayed API paths, exported file
names and email templates. Check each of them when editing copy.

## 5. Visual Consistency


### Keep controls compact by default

Controls should use a **compact height** and **small corner radius** by default across the
product. Do not introduce tall controls or large rounded corners without an explicit design
requirement.


### One icon per function, everywhere

The same function uses the **same icon** across the whole product — same style, size, and color
unless stated otherwise: create, edit, delete, copy, refresh, close drawer/modal, search,
disable, publish/unpublish, password reveal.

Icons are visual vocabulary the user learns once and reuses. If "delete" is a trash can on one
page and a cross on another, they have to learn it again on every page.

Export icons from one module and reference them, instead of letting each page pick its own:

```ts
// icons.ts — single source of truth
export const ActionIcon = {
  create: Plus, edit: Pencil, delete: Trash2,
  copy: Copy, refresh: RotateCw, search: Search,
} as const;
```

Path values should display a **copy icon immediately after the value** by default. Use the
product-wide copy icon defined by this rule.


### Use a light theme by default

Unless a task or product requirement explicitly says otherwise, use a **light theme** by
default. Do not introduce a dark theme or dark-mode-specific styling without explicit
instruction.


### Every page carries a favicon and the logo

- Every page includes a **favicon**.
- Every page shows the logo at **32x32**.

A missing favicon has a concrete cost: with a dozen tabs open the user navigates by icon, and a
tab without one can only be found by opening it.

One logo size everywhere keeps the header from shifting as the user moves between pages.


### Place units at the bottom right of statistic values

Statistic cards must place the unit at the **bottom right of the displayed value**. Keep the
unit visually associated with its number without competing with the primary value.


### Toasts need an icon and text, colored by severity

A toast shows **both an icon and text**, and the icon color varies with severity level
(success / warning / error / info).

Text alone forces the user to read the whole message before knowing whether it worked. Color
alone is invisible to colorblind users — the icon shape is the second, color-independent
signal, an accessibility baseline rather than decoration.

```jsx
toast.success("保存成功", { icon: <CheckCircle className="text-green-600" /> });
toast.error("保存失败：机构编码已存在", { icon: <XCircle className="text-destructive" /> });
```

Error toasts state the **specific reason**, not just `操作失败`.

## 6. Console Layout


### Console header and global chrome

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


### Mask sensitive configuration values

Sensitive configuration values must be displayed only in **masked or redacted form**. Never
render full secrets, tokens, passwords or private keys in the UI.


### Use local mock data in interactive prototypes

Interactive prototypes must use **local mock data**. Do not connect them to production or live
external data sources by default.


### Build the console as a single HTML page

The admin console is one HTML page; menu entries jump to their section by **anchor** instead of
loading a separate document.

Navigation then costs no reload, and the whole console stays one artifact that can be reviewed
and handed over in a single file.

