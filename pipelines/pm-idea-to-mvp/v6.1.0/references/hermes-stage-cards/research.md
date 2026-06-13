# Research — Stage Card (v6.0)

**Profile**: `pm-researcher` | **Stage**: `research`

## Outputs

- `01-research.md` (≥5 URLs, competitor table)

## Exit

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage research --task-id <this_task_id>
```

Gate fail → `kanban_block`. Pass → `kanban_complete`.
