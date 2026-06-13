---
name: prd-red-team-panel
description: "G2 red-team panel on PRD. Requires --profile debate for pm-strategy-red-team + pm-pre-mortem."
version: 1.1.0
---

# PRD Red Team Panel (G2)

Run during **spec**, after `03-prd.md` draft.

## Dependencies (not in core --core install)

Install phuryn panel roles with:

```bash
./install.sh --profile debate --all
```

| Install as | Role |
|------------|------|
| `pm-strategy-red-team` | Red Team — load-bearing assumptions, failure modes |
| `pm-pre-mortem` | Pre-mortem — imagine launch failed; root causes |

If vendor skills are unavailable, emulate the same roles inline (do not skip the debate artifacts).

## Panel roles

| Role | Skill / focus |
|------|----------------|
| Red Team | `pm-strategy-red-team` — load-bearing assumptions, failure modes |
| Pre-mortem | `pm-pre-mortem` — imagine launch failed; root causes |
| Builder | Feasibility vs `openspec/tasks.md` scope |
| Judge | Synthesis → `debates/spec-synthesis.md` |

## Outputs

- `debates/spec-round1-redteam.md`
- `debates/spec-round1-premortem.md`
- `debates/spec-synthesis.md`
- `03-prd.md` section `## Red Team Findings` with prioritized fixes

## Gate

Must pass `debate_resolved` for `stage_prefix: spec` before G2 human/auto checkpoint.

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/goal-check.py --stage spec --project-root {PROJECT_ROOT}
```
