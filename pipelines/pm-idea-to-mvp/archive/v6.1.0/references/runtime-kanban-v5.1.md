# Kanban Runtime — v5.1 (Single Source of Truth)

**Decision (2026-06):** Hermes Kanban workers run the **v5.1 nine-stage PM pipeline**.

## Kanban stage graph (runtime)

```
align → research → analysis (+ C4) → spec (+ journey) → mvp (+ UX review)
  → ship (+ G3 checkpoint) → operate → grow → retro
Optional: hermes kanban refine (4 subtasks)
```

## Profiles (9 workers + orchestrator)

| Stage | Profile |
|-------|---------|
| align | pm-aligner |
| research | pm-researcher |
| analysis | pm-analyst |
| spec | pm-planner |
| mvp | pm-builder |
| ship | pm-shipper |
| operate | pm-operator |
| grow | pm-growth |
| retro | pm-builder |
| orchestration | pm-orchestrator |

## Script paths (authoritative)

Primary (skills tree):

```
D:/hermes-data/skills/pipelines/pm-idea-to-mvp/scripts/
  decompose-pm-pipeline.py
  decompose-refine-pipeline.py
  stage-complete.py
  validate-gates.py
```

Legacy fallback: `D:/workspace/pipelines/pm-idea-to-mvp/scripts/`

## Human checkpoints

- **align** (G1), **spec** (G2), **ship** (G3 deploy) — two-phase block/unblock
- operate, grow — auto complete

## Feishu trigger

```
/goal 产品想法：{描述}
```

Gateway creates Kanban triage + runs `decompose-pm-pipeline.py` (9 children).
