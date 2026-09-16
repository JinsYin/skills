---
title: Toasts need an icon and text, colored by severity
impact: MEDIUM
tags: consistency, toast, feedback, accessibility
---

## Toasts need an icon and text, colored by severity

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
