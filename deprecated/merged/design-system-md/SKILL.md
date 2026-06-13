---
name: design-system-md
description: >-
  Create and maintain docs/DESIGN.md as visual SSOT synced with theme.css. Use before
  UI implementation or when fixing design token drift.
version: 1.0.0
author: ttmens
license: MIT
---

# Design System (DESIGN.md)

维护 `docs/DESIGN.md` 为视觉 **唯一真相源**，与 `src/site/theme.css` 双向一致。

## When to use

- G2 设计方案阶段（token 草案）
- UI 改动前 pre-flight
- docs-hygiene 报告 token 漂移

## Step 1: Read sources

1. 现有 `docs/DESIGN.md`（若有）
2. `design/archive/DESIGN.md`（历史规范）
3. `src/site/theme.css`（实现 SSOT）
4. `docs/DECISIONS.md` — **零 CDN、单 theme.css、无 Tailwind**

## Step 2: Write DESIGN.md structure

必须包含：

### Colors

- 品牌色（紫/青渐变）
- 表面色（canvas-deep, canvas, surface）
- **A 股价格色**：`--price-up` 红涨、`--price-down` 绿跌
- **信号色**：`--signal-bull` / `--signal-bear`（与国际惯例一致，与价格色分离）

### Typography / Spacing / Components

从 theme.css 提取 `:root` 变量与组件 class 说明。

### Information architecture

- 金字塔 4 层（结论 → 原因 → 证据 → 上下文）
- 3 秒原则

### Constraints

- 禁止 Tailwind CDN
- 禁止页面级 inline style 漂移
- 改动顺序：**DESIGN.md → theme.css → templates**

## Step 3: Sync implementation

```bash
python3 scripts/check_docs_ssot.py --project-root . --fix
```

## Step 4: Deprecate old docs

确保 `UI-UX-Style.md` 指向 `DESIGN.md`。
