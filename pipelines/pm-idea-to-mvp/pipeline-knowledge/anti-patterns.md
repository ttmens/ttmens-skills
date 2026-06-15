# PM Pipeline — Anti-Patterns

Failures to avoid. Updated by Retro stage.

## Alignment

- Skipping align → research produces off-target competitor lists.
- Leaving `TBD` in brief → downstream gates fail at spec stage.

## Research

- Fewer than 5 source URLs → gate fail; do not complete task.
- Competitor table with unnamed "竞品A" rows — require real product names.

## Analysis

- Single-option "analysis" — must compare ≥3 paths.
- Recommendation without "why not others" section.

## Spec

- PRD with >5 user stories — split to phase 2 or cut scope.
- Empty `openspec/tasks.md` — builder must not start.

## MVP

- Hand-writing large codebase in Hermes terminal instead of OpenCode.
- Missing README run steps — Pages reviewers cannot reproduce locally.
- OpenCode 生成的代码存在边界 Bug（函数名互换、未使用参数、校验不严）—— prompt 需增加防御性约束。
- Windows Python 环境不一致（venv 缺 pytest/httpx）—— 需统一环境或预装测试依赖。
- 测试辅助函数包含未使用的参数导致调用方传参错位 —— 生成时应校验参数使用。

## Retro

- 不跟踪 brief 中的 open assumptions 验证状态 —— 应在 retro 中逐项标注（已验证/未验证/被推翻）。



### competitor-radar (2026-06-07)

- v2.1 run skipped align/openspec/prototype — backfilled for v3 gates