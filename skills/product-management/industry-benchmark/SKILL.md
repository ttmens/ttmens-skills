---
name: industry-benchmark
description: "Deep-dive industry implementation patterns vs current MVP for targeted optimization."
version: 1.0.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, research, benchmark, refine]
    related_skills: [pm-idea-to-mvp, c4-architecture, user-journey]
---

# Industry Benchmark — Implementation Deep Dive

Go beyond `01-research.md` competitor tables. Study **how** similar products implement features, architecture, and UX — then gap-analyze **this project's current MVP**.

## Output

Write `01b-benchmark.md`:

```markdown
# 业界实现深研

## 当前实现基线
- 项目：pm-{slug}
- 对照目录：`04-mvp/`, `openspec/design.md`
- 已知差距摘要：...

## 案例 1：{产品名}
- 来源 URL：...
- 实现要点（功能/架构/UX）：...
- 可借鉴：...
- 对当前实现的差距：...

## 案例 2：...
## 案例 3：...

## 差距汇总表
| 维度 | 业界做法 | 我们现状 | 建议优化 | 优先级 |
|------|----------|----------|----------|--------|

## 建议反馈
（追加到 feedback.jsonl 的 proposed_delta）
```

## Process

1. Read `01-research.md`, `04-mvp/README.md`, key source files, `03-prd.md` AC gaps
2. Pick ≥3 **implementation** case studies (not marketing pages)
3. Tavily `web_search` + `web_extract`; browser for product docs/demos
4. Every claim needs URL
5. Append actionable items to `feedback.jsonl` with `stage: "benchmark"`

## Refine context

Used in **Refine-1** subtask when user triggers `hermes kanban refine`. Does not replace `01-research.md` — extends it.

## Verification

- ≥3 case studies with URLs
- 差距汇总表 ≥5 rows
- Each case has「对当前实现的差距」section
