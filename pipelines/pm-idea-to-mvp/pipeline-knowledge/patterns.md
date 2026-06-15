# PM Pipeline — Effective Patterns

Patterns distilled from successful runs. Updated by Retro stage.

## Alignment

- Start with `grill-me` when brief is one paragraph; switch to `grill-with-docs` once CONTEXT.md has ≥3 glossary terms.
- Lock non-goals in CONTEXT before research — reduces scope creep in PRD.

## Research

- Tavily `web_search` + competitor table in first pass; browser only for paywalled or JS-heavy pages.
- Tag confidence (`high`/`medium`/`low`) on every market-size claim.

## Analysis

- Force ≥3 options including "do nothing" or "manual spreadsheet" baseline.
- Write ADR for chosen direction before planner starts.

## Spec

- `02b-prototype` with ≤3 screens validates PRD stories before OpenCode spend.
- `openspec/tasks.md` vertical slices map 1:1 to user stories.

## MVP

- Generate `04-mvp/DESIGN.md` before OpenCode — avoids generic purple-gradient UI.
- Dogfood smoke on localhost before `kanban_complete`.



### competitor-radar (2026-06-07)

- Tavily research produced rich competitor table
- OpenCode MVP delivered Flask demo

### Misses

- v2.1 run skipped align/openspec/prototype — backfilled for v3 gates



### kl-management (2026-06-07)

管线 v3.0.0 首次完整运行（6 阶段全通）：

- **Stage 0-1**: brief → research（7 竞品 × 3 维度，29 来源，含 DDD/AI 上下文工程深度调研）
- **Stage 2**: analysis 产出 5 个 ADR + CONTEXT.md 术语表
- **Stage 2b**: 原型验证 PRD stories
- **Stage 3**: openspec 生成 4 specs + 15 tasks（垂直切片映射用户故事）
- **Stage 4**: OpenCode 一次性生成 18+ 文件（FastAPI + SQLite + HTMX），39 pytest 通过，18 smoke 端点 200
- **Stage 5-6**: retro 全链路回顾 + 假设验证 + skill patch proposals

关键经验：
- OpenCode 生成质量优秀但需要防御性 prompt 约束（函数命名、参数校验、格式验证）
- 手动 patch 修复（~5min）> 二次 OpenCode 调用
- 全链路 ~60-70 min，从 brief 到可运行 MVP

### Misses


### feishu-pipeline-test (2026-06-07)

The pipeline evolved from a theoretical framework to a proven execution path. The key evolution was:

- **Stage 0-2 (Discovery)** → Framed the problem space and validated feasibility
- **Stage 3 (Planning)** → Converted ambiguity into 13 actionable tasks with clear acceptance criteria
- **Stage 4 (Building)** → Executed the plan, verified outputs, produced a working dashboard MVP
- **Stage 5 (Retro)** → Captured learnings for pipeline self-improvement

The biggest evolutionary leap was the transition from planning to building — the task decomposition held up under execution, and the validation gates prevented quality regressions. The network failure on push was a reminder that operational resilience is as important as technical correctness.