# Operate — Stage Card (v6.0)

**Profile**: `pm-operator` | **Stage**: `operate`

## Outputs

- `07-ops-notes.md` (on-call, monitoring, rollback)

## Exit

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage operate --task-id <this_task_id>
```
