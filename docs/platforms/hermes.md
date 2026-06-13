# Hermes Agent

> Agent 安装与 decompose 流程：[AGENT_ONBOARDING.md](../AGENT_ONBOARDING.md)

## Install

```bash
./install.sh --core --platform hermes --profile hermes-kanban
./install.sh --profile hermes --hermes   # plan + opencode
```

Skills install to `~/.hermes/skills/` including **pm-aligner … pm-growth** Kanban profiles.

## Entry

Default orchestration: `pm-idea-to-mvp` v6.1 + Kanban decompose.

```bash
python pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py \
  --project-root /path/to/pm-{slug} --scenario greenfield
hermes kanban dispatch
```

## Kanban ↔ Runtime

- MVP split: **T5a Plan → T5b Inner Loop → T5c G3 Verify**
- `stage-complete.py` → `kanban-sync.py` block/complete
- Refine: `refine-decompose.py --project-root ...`

## Stage scripts

| Script | Use |
|--------|-----|
| `harness-runner.py` | Risk-based decisions |
| `inner-loop-driver.py` | MVP Plan→Test→Observe |
| `phase-transition.py` | Backtrack mvp→spec |
| `kanban-sync.py` | block/complete/comment |

Install `plan` with `--profile hermes` → `.hermes/plans/`.

See [runtime-kanban-v6.0.md](../../pipelines/pm-idea-to-mvp/references/runtime-kanban-v6.0.md).
