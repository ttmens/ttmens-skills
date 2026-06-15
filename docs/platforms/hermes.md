# Hermes Agent

> Agent 安装与 decompose 流程：[AGENT_ONBOARDING.md](../AGENT_ONBOARDING.md)

## Install

```bash
./install.sh --core --profile debate --platform hermes --profile hermes-kanban
./install.sh --core --profile hermes --platform hermes   # plan + opencode delegate
```

Skills install to `~/.hermes/skills/` including **pm-aligner … pm-growth** Kanban profiles.

Override paths with env vars: `HERMES_HOME`, `PROJECTS_ROOT`, `SKILLS_ROOT`.

## Detect environment

```bash
python {SKILLS_ROOT}/scripts/detect_agent_env.py --json
python {SKILLS_ROOT}/scripts/validate_skills.py
```

## Entry

Default orchestration: `pm-idea-to-mvp` v7.1.0 + Kanban decompose.

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py \
  --project-root /path/to/pm-{slug} --scenario greenfield
hermes kanban dispatch
```

### Feishu grill + trigger routing (v6.1 Hermes UX)

Before decompose on Feishu-triggered ideas:

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/feishu-grill-preflight.py start \
  --session-key KEY --text "产品想法：..." --slug SLUG
```

SSOT: [`assets/trigger-routing.yaml`](../../pipelines/pm-idea-to-mvp/assets/trigger-routing.yaml), [`references/feishu-grill-protocol.md`](../../pipelines/pm-idea-to-mvp/references/feishu-grill-protocol.md), [`references/hermes-integration.md`](../../pipelines/pm-idea-to-mvp/references/hermes-integration.md).

### Brownfield / resume

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py \
  --project-root /path/to/pm-{slug} --scenario brownfield
```

See [`references/brownfield-audit.md`](../../pipelines/pm-idea-to-mvp/references/brownfield-audit.md).

## Kanban ↔ Runtime

- MVP split: **T5a Plan → T5b Inner Loop → T5c G3 Verify**
- `stage-complete.py` → `kanban-sync.py` block/complete
- Refine: `refine-decompose.py --project-root ...`
- Status: `kanban-status-report.py --slug {slug}`

## Stage scripts

| Script | Use |
|--------|-----|
| `harness-runner.py` | Risk-based decisions |
| `inner-loop-driver.py` | MVP Plan→Test→Observe |
| `phase-transition.py` | Backtrack mvp→spec |
| `kanban-sync.py` | block/complete/comment |
| `sync-hermes-profiles.py` | Re-bundle stage cards to profiles |

Install `plan` with `--profile hermes` → `.hermes/plans/`.

See [runtime-kanban-v6.0.md](../../pipelines/pm-idea-to-mvp/references/runtime-kanban-v6.0.md).

**Live pipeline only:** use `pipelines/pm-idea-to-mvp/` — not `v6.1.0/` snapshot.
