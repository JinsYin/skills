---
title: Paginate with windowed page numbers
impact: HIGH
impactDescription: Rendering every page number freezes the page on large datasets
tags: list, pagination, performance
---

## Paginate with windowed page numbers

Every list page paginates and shows the **total count at the top right** — the user needs the
size of the result set to decide between paging through it and filtering it down.

Page numbers must be windowed: **always show the first and the last page**, the current page
with one page on each side, and a **non-clickable** ellipsis at every gap.

```text
< 1 … 49 50 51 … 103 >
```

Rendering all pages is not merely ugly: 103 pages is 103 DOM nodes with listeners, and one
order of magnitude more data freezes the page — which the few dozen rows of a dev database will
never reveal.

The ellipsis must not be clickable. Making it jump somewhere turns it into a page number whose
destination the user cannot predict.
