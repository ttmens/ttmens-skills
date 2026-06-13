---
name: pm-builder
description: "Hermes Kanban profile for mvp stage. Run stage-complete at boundary."
version: 1.0.0
metadata:
  hermes:
    profile: pm-builder
    stage: mvp
---

# pm-builder

**Stage**: mvp

## Boundaries
- Only write artifacts for **mvp** stage
- At stage end run:
  `python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage mvp --project-root {PROJECT_ROOT} --task-id {TASK_ID} --verify-goals`

## Skills
subagent-driven-development, inner-loop-driver
