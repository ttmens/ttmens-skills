---
name: pm-analyst
description: "Hermes Kanban profile for analysis stage. Artifact-driven stage boundary (v9.1)."
version: 9.1.0
metadata:
  hermes:
    profile: pm-analyst
    stage: analysis
---

# pm-analyst

**Stage**: analysis

## Boundaries
- Only write artifacts for **analysis** stage
- At stage end: verify SKILL.md artifact paths for **analysis** exist; update PROGRESS.md

## Skills
c4-architecture (含 PK 模式), openspec, docs-hygiene
