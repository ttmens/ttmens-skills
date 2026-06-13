# Ship — Stage Card (v6.0)

**Profile**: `pm-shipper` | **Stage**: `ship` | **Checkpoint**: human (G3)

## Outputs

- `RUNBOOK.md`, `docs/ui-acceptance-report.md`

## Exit

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage ship --task-id <this_task_id> --runtime
```

**First run**: `kanban_block` `等待用户确认部署范围`. **Resume**: `kanban_complete`.
