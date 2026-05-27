---
name: docs-hygiene
description: >-
  Enforce documentation SSOT rules — single CURRENT-STATUS, DESIGN.md sync with
  theme.css, DECISIONS on architecture changes. Run at phase start/end or via hook.
version: 1.0.0
author: ttmens
license: MIT
---

# Docs Hygiene

自动化 docs 维护规则，防止 SSOT 漂移。

## When to use

- product-orchestrator Phase 开始/结束
- 用户说「检查文档」「SSOT 漂移」
- pre-commit hook 触发

## Step 1: Run checker

```bash
python3 scripts/check_docs_ssot.py --project-root /path/to/project
python3 scripts/check_docs_ssot.py --project-root . --fix
```

## Rules enforced

| 规则 | 检测 | 修复 |
|------|------|------|
| 单一 CURRENT-STATUS | 多个 `*-CURRENT-STATUS*.md` 并存 | 归档旧版到 `design/archive/` |
| DESIGN SSOT | `docs/DESIGN.md` 缺失或与 theme.css 变量严重偏离 | 提示运行 design-system-md |
| src↔docs sync | `src/site/theme.css` hash ≠ `docs/assets/theme.css` | `--fix` 复制 sync |
| 废弃文档 | UI-UX-Style 未指向 DESIGN.md | 加 deprecation banner |
| DECISIONS | 架构文件变更但 DECISIONS 未更新 | warning |

## Step 2: Fix drift

若 `--fix` 可用：
- 复制 canonical theme.css 到 docs/assets（若 src 更新）
- 为重复 STATUS 文件写 redirect stub

## Step 3: Report

输出 JSON 或 markdown 摘要，可选写入 `workflow_state.yaml` → `last_docs_hygiene`
