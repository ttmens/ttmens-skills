---
name: pm-aligner
description: "Hermes Kanban profile for align stage. Run stage-complete at boundary."
version: 1.0.0
metadata:
  hermes:
    profile: pm-aligner
    stage: align
---

# pm-aligner

**Stage**: align

## Boundaries
- Only write artifacts for **align** stage
- At stage end run:
  `python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage align --project-root {PROJECT_ROOT} --task-id {TASK_ID} --verify-goals`

## Skills
grill-me, grill-with-docs (含 G1 辩论协议)
