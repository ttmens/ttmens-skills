---
name: openspec
description: "Spec-driven development: proposal, delta specs, design, tasks — Hermes markdown workflow."
version: 1.0.0
author: PM Pipeline (adapted from Fission-AI/OpenSpec)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, spec, requirements, sdd]
    related_skills: [plan, grill-with-docs, pm-idea-to-mvp]
---

# OpenSpec — Spec-Driven Workflow (SKILL mode)

Persist requirements in-repo. No OpenSpec CLI required — use markdown templates.

## Directory layout

```
openspec/
  proposal.md       # Why / what change
  design.md         # How — must link architecture/c4-*.md (no ASCII-only substitute)
  tasks.md          # Checklist for builder
  specs/
    capability.md   # ADDED/MODIFIED/REMOVED deltas
```

## Workflow (OPSX fluid — stage内可迭代)

Actions, not rigid phases. Within the **spec** Kanban task you may:

1. **Propose** — Draft/update `openspec/proposal.md`
2. **Spec delta** — Write/revise `openspec/specs/*.md` (ADDED, MODIFIED, REMOVED)
3. **Design** — Update `openspec/design.md` (reference `architecture/c4-context.md`, `c4-container.md`, `c4-component.md`)
4. **Tasks** — Update `openspec/tasks.md` vertical slices
5. **Prototype** — Iterate `02b-prototype/` alongside specs
6. **Verify** — Builder checks tasks.md before MVP; planner re-opens specs if scope shifts

Run `verify spec artifacts (03-prd.md, openspec/)` only when proposal + PRD + prototype + tasks are ready.

## proposal.md template

```markdown
# Proposal: {title}
## Why
## What changes
## Impact
## Acceptance scenarios
```

## tasks.md rules

- Each task: file paths, verification step, done-when
- Max 15 tasks for MVP scope
- Reference `03-prd.md` user stories by ID

## Who uses this

- **pm-analyst**: draft proposal after recommendation
- **pm-planner**: finalize specs + tasks from PRD
- **pm-builder**: implement against tasks.md; verify before kanban_complete
