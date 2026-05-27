---
name: ui-acceptance-review
description: >-
  Fintech UI acceptance with quick/full modes, 100-point rubric, pre/post snapshots.
  Use at ship phase, Gate G3, or after UI changes in stock-copilot-like projects.
version: 1.0.0
author: ttmens
license: MIT
---

# UI Acceptance Review

Gate **G3** 执行 skill。分 **quick** / **full** 两级。

## Quick mode

每个含 UI 改动的 commit 或 Phase 中间检查：

```bash
python3 scripts/ui_acceptance.py --quick --project-root .
```

检查：theme sync、免责声明、无 CDN、DESIGN.md 关键 token。

## Full mode

Phase Ship 前，触发 G3 人工确认：

```bash
python3 scripts/ui_acceptance.py --full --project-root .
```

写入 `docs/ui-acceptance-report.md`。Pass：**≥85 分** 且 compliance critical 全过。

## Pre/Post snapshot ritual

1. UI 改动前：`docs/archive/YYYY-MM-DD-pre.html` 或 `docs/ui-snapshots/pre.png`
2. 改动后：`-post` 对应文件
3. 摘要写入 acceptance report

## Fix loop

未通过时自动修复（最多 3 轮，不打扰用户）：

1. 读 report 失败维度
2. 修复 token/sync/合规/交互
3. 重跑 `--full`
4. 70–84 分 → 加载 `frontend-polish` refinement
5. 仍失败 → 记录 blocker，到 G3 向用户汇报

## Cursor full mode

full 通过后，用 browser MCP：

1. 打开 `docs/index.html` 或 GitHub Pages URL
2. 截图 1280px 与 375px viewport
3. 保存到 `docs/ui-snapshots/`
4. 附到 acceptance report

Hermes 无 browser 时：依赖 pre/post HTML + 静态分析。

## Rubric

| 维度 | 分 |
|------|---|
| information_architecture | 20 |
| interaction | 15 |
| static_dynamic | 15 |
| design_token_sync | 15 |
| responsive | 10 |
| a11y | 10 |
| compliance (critical) | 10 |
| performance | 5 |
