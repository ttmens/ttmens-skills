# Retro — Stage Card (v6.0)

**Profile**: `pm-builder` | **Stage**: `retro`

## Outputs

- `05-retro.md`, `harness-improvements.md`, `evolution-notes.md`

## Exit

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage retro --task-id <this_task_id>
```

Merge retro knowledge if `merge-retro-knowledge` skill available.
