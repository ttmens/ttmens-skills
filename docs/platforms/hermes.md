# Hermes Agent

> Agent 安装与 decompose 流程：[AGENT_ONBOARDING.md](../AGENT_ONBOARDING.md)  
> 系统架构：[ARCHITECTURE.md](../ARCHITECTURE.md)

## Install

```bash
./install.sh --core --profile debate --platform hermes --profile hermes-kanban
./install.sh --core --profile hermes --platform hermes   # plan + opencode delegate
```

Skills install to `~/.hermes/skills/` (or `HERMES_HOME/skills/`) including **pm-aligner … pm-growth** Kanban profiles.

Override paths with env vars: `HERMES_HOME`, `PROJECTS_ROOT`, `SKILLS_ROOT`.

**v7.2 架构**：本地 Hermes Gateway + Kanban + OpenCode 为唯一编排；远端 VPS 仅 SSH deploy target（不跑独立 Gateway）。

## Detect environment

```bash
python {SKILLS_ROOT}/scripts/detect_agent_env.py --json
python {SKILLS_ROOT}/scripts/validate_skills.py
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/pm-e2e-smoke.py
```

## Entry

Default orchestration: `pm-idea-to-mvp` v7.2.0 + Kanban decompose.

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py \
  --project-root /path/to/pm-{slug} --scenario greenfield
hermes kanban dispatch
```

### Feishu grill + trigger routing

Before decompose on Feishu-triggered ideas:

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/feishu-grill-preflight.py start \
  --session-key KEY --text "产品想法：..." --slug SLUG
```

SSOT: [`assets/trigger-routing.yaml`](../../pipelines/pm-idea-to-mvp/assets/trigger-routing.yaml), [`references/feishu-grill-protocol.md`](../../pipelines/pm-idea-to-mvp/references/feishu-grill-protocol.md), [`references/hermes-integration.md`](../../pipelines/pm-idea-to-mvp/references/hermes-integration.md).

### Human checkpoints (v7.2: align + ship only)

| Checkpoint | Stage | Unblock |
|------------|-------|---------|
| Direction | align | Feishu `确认 t_xxx` or `hermes kanban unblock t_xxx` |
| Deploy | ship | Same |

spec G2 debate is **script-gated** (`goal-check.py`), not a human unblock.

### Feishu notifications + artifacts

`stage-complete.py` order: build-run-report → git_push → `feishu_notify.py`.

Message SSOT: [`scripts/pipeline_notify.py`](../../pipelines/pm-idea-to-mvp/scripts/pipeline_notify.py) — includes:

- GitHub Pages deep link (tab anchors)
- `artifacts.manifest.yaml` deliverable checklist
- Unblock instructions

Gateway Kanban notifier uses the same builder via companion `pm_pipeline.py`.

### Deploy (ship stage only)

Per-project [`deploy.yaml`](../../pipelines/pm-idea-to-mvp/assets/deploy.template.yaml) + server registry:

1. Copy [`templates/hermes/config/deploy-servers.template.yaml`](../../templates/hermes/config/deploy-servers.template.yaml) → `HERMES_HOME/config/deploy-servers.yaml`
2. Set passwords in `HERMES_HOME/.env` as `SSH_PASSWORD_*`
3. Preflight: `python .../ssh_preflight.py --project-root /path/to/pm-{slug}`

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
| `pipeline_notify.py` | Unified Feishu/Kanban message builder |
| `deploy_servers.py` | Merge deploy.yaml + server registry |
| `ssh_preflight.py` | Paramiko SSH preflight (Windows-safe) |

Install `plan` with `--profile hermes` → `.hermes/plans/`.

See [runtime-kanban-v7.1.md](../../pipelines/pm-idea-to-mvp/references/runtime-kanban-v7.1.md) (v7.2 behavior: align+ship checkpoints).

Legacy: [runtime-kanban-v6.0.md](../../pipelines/pm-idea-to-mvp/references/runtime-kanban-v6.0.md) — deprecated, kept for history.

**Live pipeline only:** use `pipelines/pm-idea-to-mvp/` — not `archive/v6.1.0/` snapshot.

## Companion Gateway

Pipeline scripts live in ttmens-skills; routing/HITL cards live in `hermes-agent`:

- `hermes_cli/pm_pipeline.py`
- `hermes_cli/feishu_pipeline_cards.py`

See [`references/hermes-integration.md`](../../pipelines/pm-idea-to-mvp/references/hermes-integration.md).
