---
name: pm-researcher
description: "Hermes Kanban profile for research stage. Run stage-complete at boundary."
version: 1.0.0
metadata:
  hermes:
    profile: pm-researcher
    stage: research
---

# pm-researcher

**Stage**: research

## Boundaries
- Only write artifacts for **research** stage
- At stage end run:
  `python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage research --project-root {PROJECT_ROOT} --task-id {TASK_ID} --verify-goals`

## Skills
pm-competitor-analysis
