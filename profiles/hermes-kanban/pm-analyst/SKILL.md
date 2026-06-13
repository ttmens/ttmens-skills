---
name: pm-analyst
description: "Hermes Kanban profile for analysis stage. Run stage-complete at boundary."
version: 1.0.0
metadata:
  hermes:
    profile: pm-analyst
    stage: analysis
---

# pm-analyst

**Stage**: analysis

## Boundaries
- Only write artifacts for **analysis** stage
- At stage end run:
  `python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage analysis --project-root {PROJECT_ROOT} --task-id {TASK_ID} --verify-goals`

## Skills
c4-architecture (含 PK 模式), openspec, docs-hygiene
