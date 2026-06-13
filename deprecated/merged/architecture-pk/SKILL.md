---
name: architecture-pk
description: "Analysis-stage PK: 2-3 architecture options with mini-ADRs; Judge picks recommendation."
version: 1.0.0
---

# Architecture PK

Run during **analysis**, after draft `02-analysis.md`, alongside `c4-architecture`.

## Protocol

1. Assign **Option A / B / C** agents (or sequential roles): each writes `debates/analysis-option-{A|B|C}.md` with mini-ADR (context, decision, consequences).
2. **Judge** reads all options + `01-research.md`; writes `debates/analysis-synthesis.md` with:
   - Recommended option
   - Rejected options + why
   - Top 3 risks + mitigations
3. Update `02-analysis.md` recommendation section and `architecture/c4-*.md` to match winner.

## Gate

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/goal-check.py --stage analysis --project-root {PROJECT_ROOT}
```

Require ≥2 option files + synthesis before analysis complete.
