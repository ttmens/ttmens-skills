# Spec — Stage Card (v6.0)

**Profile**: `pm-planner` | **Stage**: `spec` | **Checkpoint**: human (two-phase)

## Outputs

- `03b-user-journey.md`, `02b-prototype/`, `03-prd.md`, `openspec/tasks.md`

## Exit

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage spec --task-id <this_task_id> --runtime
```

**First run**: `kanban_block` `等待用户确认 PRD/原型范围`. **Resume**: `kanban_complete`.
