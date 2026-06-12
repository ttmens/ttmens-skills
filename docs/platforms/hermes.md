# Hermes Agent

## Install

```bash
./install.sh --core --hermes
./install.sh --profile hermes --hermes   # plan + opencode
.\install.ps1 -Target Hermes
```

Skills install to `~/.hermes/skills/`.

## Entry

Default orchestration skill: `pm-idea-to-mvp` (metadata.hermes tags).

## Kanban pipeline

1. New idea → decompose into stages (align → research → … → retro)
2. Profiles: `pm-aligner`, `pm-researcher`, `pm-analyst`, `pm-planner`, `pm-builder`, `pm-shipper`, `pm-operator`, `pm-growth`
3. Human checkpoints: **align**, **spec** — `kanban_block` + Feishu notify
4. MVP coding: `opencode run` via `opencode` skill

## Commands

```bash
hermes kanban create "Stage 1: 对齐" --assignee pm-aligner --body "..."
hermes kanban dispatch
hermes kanban show <task_id>
```

See `pipelines/pm-idea-to-mvp/SKILL.md` § Platform notes (Hermes).

## Plans

Install `plan` with `--profile hermes` → writes to `.hermes/plans/` (`profiles/hermes-plan/plan`).
