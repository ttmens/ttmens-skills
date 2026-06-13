# MVP Code+Test — Inner Loop iter 1-3 (v6.0)

**Profile**: `pm-builder` | **Stages**: `mvp-iter1`, `mvp-iter2`, `mvp-iter3`

## Chain

TDD → opencode → ui-acceptance-review (journey) → dogfood

Workdir: `{PROJECT_ROOT}/04-mvp`

## Exit (iter1/3 on final pass)

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage mvp --task-id <this_task_id> --runtime --verify-goals
```

- iter1 fail → fix or dispatch iter2
- iter3 still fail → `kanban_block` + `harness-improvements.md`
