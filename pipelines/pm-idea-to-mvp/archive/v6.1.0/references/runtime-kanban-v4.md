# Kanban Runtime — v4 (Single Source of Truth)

**Decision (2026-06):** Hermes Kanban workers run the **v4 six-stage PM pipeline**, not the full v5.1 skill document stage table.

## Why

- Workspace scripts ([`D:/workspace/pipelines/pm-idea-to-mvp/scripts/`](D:/workspace/pipelines/pm-idea-to-mvp/scripts/)) implement v4 gates and `decompose-pm-pipeline.py` (6 children).
- Only **6 PM profiles** exist: `pm-aligner`, `pm-researcher`, `pm-analyst`, `pm-planner`, `pm-builder`, `pm-orchestrator`.
- v5.1 stages **ship / operate / grow** reference `pm-shipper`, `pm-operator`, `pm-growth` — profiles **not installed** until a future release.

## Kanban stage graph (runtime)

```
align → research → analysis (+ C4) → spec (+ journey) → mvp (+ UX review) → retro
Optional: hermes kanban refine (4 subtasks)
```

## Script paths (authoritative)

```
D:/workspace/pipelines/pm-idea-to-mvp/scripts/
  decompose-pm-pipeline.py
  decompose-refine-pipeline.py
  stage-complete.py
  validate-gates.py
```

## v5.1 skill document scope

The v5.1 `SKILL.md` is the **product/design reference** (borrowed skills, G1/G2/G3, platform notes). For **Kanban dispatch**, follow this file and profile-bundled `pm-idea-to-mvp` v4 copies.

## Feishu trigger (implemented)

```
/goal 产品想法：{描述}
```

Gateway creates Kanban triage + runs `decompose-pm-pipeline.py` automatically (not Ralph `/goal` loop).

Plain text containing `按 pm-idea-to-mvp` or `pm-idea-to-mvp` is also intercepted.
