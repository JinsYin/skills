---
title: 链接多或有重复目标时用参考链接
impact: MEDIUM
impactDescription: 长 URL 撑乱源码，同一目标多处内联时改地址易漏成死链
tags: struct, markdown, link
---

## 链接多或有重复目标时用参考链接

判据：**全文链接超过约 5 个，或同一目标被引用不止一次**——改用参考链接；少量一次性链接保留行内形式。

长 URL 混在正文里会把列表项撑成好几行，源码难读、diff 难审；同一目标内联多处时，改地址要改多处，漏一处就是死链。

**正文**用折叠式 `[文本][]`，链接文本即标签；同一文本指向不同目标、或不同文本指向同一目标时，才用完整式 `[文本][标签]`：

```markdown
- 调研记录：[API 网关产品能力调研][]、[多环境隔离调研][]
- 文档链接：[Envoy Gateway Concepts][]
```

**定义**集中放在文末，用 HTML 注释分组（渲染时不可见）：本地文件在前，外部 URL 在后；组内按首次出现排序，便于对照正文核对：

```markdown
<!-- 文件链接（调研记录） -->
[API 网关产品能力调研]: ../research/api-gateway-product-capabilities.md
[多环境隔离调研]: ../research/api-gateway-multi-env-isolation.md

<!-- URL 链接（技术参考） -->
[Envoy Gateway Concepts]: https://gateway.envoyproxy.io/docs/concepts/
```

**两个静默失效**：未定义的引用会原样渲染成 `[文本][]` 字面量；删正文时漏删的定义不报错，只会堆积。改完核对引用与定义一一对应，markdownlint 的 MD052 / MD053 可查。
