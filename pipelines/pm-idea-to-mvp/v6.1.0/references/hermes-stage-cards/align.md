# Align — Stage Card (v6.0)

**Profile**: `pm-aligner` | **Stage**: `align` | **Checkpoint**: human (two-phase)

## Outputs

- `CONTEXT.md`, `decisions.md` under `{PROJECT_ROOT}`

## Skills

`grill-me`, `grill-with-docs`

## Exit (mandatory)

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage align --task-id <this_task_id> --runtime
```

**First run**: exit 0 → `kanban_block` reason `等待用户确认 align 产物` → **do NOT** `kanban_complete`.  
**Resume** (after unblock): verify gates → `kanban_complete`.
