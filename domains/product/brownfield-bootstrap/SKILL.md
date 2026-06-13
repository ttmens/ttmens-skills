---
name: brownfield-bootstrap
description: "Bootstrap existing repo into pm-{slug} pipeline: CONTEXT, stage skip map, delta PRD."
version: 1.0.0
---

# Brownfield Bootstrap

Use when **optimizing an existing product**, not greenfield 0→1.

## Steps

1. Scan repo: README, package manifests, main entrypoints, tests, deploy configs.
2. Write `CONTEXT.md` (简体中文): current state, users, constraints, tech stack.
3. Write `docs/brownfield-map.yaml`:

```yaml
scenario: brownfield
skip_stages: [brief, align, research]  # adjust per repo maturity
start_stage: analysis
existing_artifacts:
  prd: null  # or path if exists
  runbook: RUNBOOK.md
```

4. Run `docs-hygiene` + `{SKILLS_ROOT}/scripts/check_docs_ssot.py`.
5. Resume pipeline at `start_stage` from map.

## Hermes

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py --project-root {PROJECT_ROOT} --scenario brownfield
```

## Cursor

Say: **继续优化现有产品** + point to repo root; agent reads `docs/brownfield-map.yaml`.
