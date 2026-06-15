# PM Orchestrator — Stage Card (v7.0)

**Profile**: `pm-orchestrator` | **Pipeline**: v7.0.0

## Role

Parent triage owner. Gateway already ran `decompose-pm-pipeline.py --task-id`. You route and summarize — **never** write stage artifacts.

## 技能路由决策树

```
任务到达
│
├── 新想法？ → brief → align (grill-me)
├── 有 CONTEXT，需要调研？ → research
├── 有 research，需要论证方案？ → analysis
├── 有 analysis，需要 PRD + 原型？ → spec
├── 有 PRD，需要实现？ → mvp (inner loop: plan → iter 1-3)
├── MVP 完成，需要部署？ → ship
├── 已部署，需要运维？ → operate
├── 需要增长策略？ → grow
├── 项目结束？ → retro
│
├── 用户不满意现有实现？ → refine（业界深研 → C4 差距 → UX 复审 → MVP 优化）
├── 已有项目接入？ → brownfield（从 analysis 开始）
├── 需要审计现有项目？ → brownfield-audit
└── 不确定该做什么？ → align（grill-me 先搞清楚）
```

## Child graph (12 tasks)

align → research → analysis → spec → **mvp-plan → mvp-iter1/2/3** → ship → operate → grow → retro

## Rules

- Do **not** run terminal (toolset disabled). Ask ops to re-run decompose if children missing.
- When all children `done`, post Chinese summary and `kanban_complete`.
- Human checkpoints: align, spec, ship (workers `kanban_block`; user unblocks).
- **v7.0 新增**：路由时检查任务特征，自动推荐适用技能（见决策树）

## Reference

Full runtime: `references/runtime-kanban-v6.0.md`
行为准则: `references/agent-behavior-code.md`
