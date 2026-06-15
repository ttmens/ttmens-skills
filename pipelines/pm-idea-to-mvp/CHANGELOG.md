# Changelog

All notable changes to pm-idea-to-mvp pipeline will be documented in this file.

## [7.1.0] - 2026-06-15

### Overview

Battle-hardened release from pm-knowledge-platform E2E retrospective.

### Added

- Skill trigger routing (`assets/trigger-routing.yaml`) + quick scenario table
- Mandatory browser E2E verification at ship stage
- Rollback decision tree (`references/rollback-decision-tree.md`)
- Forced brownfield audit flow (`references/brownfield-audit.md`)
- Inner loop entry checks + PROGRESS.md update protocol

## [7.0.0] - 2026-06-15

### Overview

Agent behavior code fusion from addyosmani/agent-skills.

### Added

- `references/agent-behavior-code.md` — 6 non-negotiable behavior rules
- Anti-rationalization tables in all Hermes stage cards
- `requesting-code-review` v3.0 — 5-axis code review
- `stage-complete.py --check-behavior` validation

## [6.1.0] - 2026-06-06 — Hermes UX

### Overview

Feishu/Kanban integration fixes: trigger routing SSOT, grill preflight, brownfield/resume, observability.

### Added

- `assets/trigger-routing.yaml`, `references/hermes-integration.md`
- `scripts/feishu-grill-preflight.py`, `references/feishu-grill-protocol.md`
- `scripts/kanban-status-report.py`
- `decompose-pm-pipeline.py --scenario brownfield|optimize|refine`
- Stage cards: `feishu-grill.md`, `brownfield.md`
- `skills/scripts/feishu_notify.py` (webhook + checkpoint messages)

### Changed

- `pm_pipeline.py` v6.1.0: `handle_pm_gateway_message`, resume, scenario detection
- `gateway/run.py`: route audit logs
- `stage-complete.py`: align/spec/ship checkpoints + blocked Feishu notify
- pm-aligner SOUL: Feishu grill vs Kanban autonomous modes

## [6.2.1] - 2026-06-13

### 🎯 Overview

**Self-audit release** — comprehensive audit of all 22+ scripts, fixed 14 issues found during pm-knowledge-platform v6.2 alignment.

### ✨ New Scripts

- **`consume-feedback.py`** — Closes the feedback loop. Parses `feedback.jsonl`, generates retro summary, marks entries as consumed. Previously feedback was write-only (P0 fix).
- **`init-project.py`** — Initializes all 14 governance artifacts for new projects (goals/, debates/, feedback.jsonl, gates.json, harness-rules.yaml, PROGRESS.md, evolution-notes.md).
- **`pipeline_utils.py`** — Shared utilities: YAML parsing, file checks, URL counting, logging setup. Eliminates 3x code duplication.

### 🐛 Bug Fixes (P0)

- **`feishu_notify.py`** — Fixed SyntaxError (docstring missing newline before import)
- **`goal-check.py`** — Added `--goal <id>` parameter (was documented in SKILL.md but not implemented)
- **`validate-gates.py`** — Added `--all-stages` mode for full pipeline validation in one command
- **SKILL.md** — Fixed `--mode quick` → `--quick` for ui_acceptance.py
- **SKILL.md** — Fixed `--goal` parameter documentation (now matches actual CLI)
- **`validate-gates.py`** — Fixed operate stage `all_passed=false` when no checks defined (now defaults to true)

### 🔧 Improvements (P1)

- **Version consistency** — All 13 scripts with PIPELINE_VERSION updated to 6.2.0
- **Hardcoded paths** — Fixed 5 scripts (merge-retro-knowledge, validate-profile-env, decompose-refine-pipeline, sync-hermes-profiles, github_helpers) to use relative paths
- **Subprocess timeouts** — Added timeouts to build-run-report.py, publish_repo.py, git_push.py
- **Project initialization** — init-project.py creates complete governance artifact set

### 📝 Documentation (P2)

- **SKILL.md directory layout** — Added `07-ops-notes.md`, `06-growth.md`
- **SKILL.md validation commands** — Added `--all-stages`, `consume-feedback.py`, `init-project.py` examples
- **Argparse descriptions** — Added to merge-retro-knowledge, build-index, refine-decompose, git_push

### 📊 Verification

- 25/25 scripts pass syntax check
- pm-knowledge-platform: 43/43 gate checks PASS
- docs-hygiene: OK=True
- --all-stages: working correctly
- init-project.py: creates 14 artifacts
- consume-feedback.py: correctly parses and summarizes feedback

---

## [6.2.0] - 2026-06-13

### 🎯 Overview

**Enforced Governance version** — based on pm-knowledge-platform post-mortem analysis.

### ✨ Key Features

- Mandatory runtime verification for mvp/ship stages
- Cross-document consistency checks (tech-stack-conflict detection)
- G1/G2 debate gate enforcement (debates/ directory + debate_resolved marker)
- Inner loop prerequisites (goals/mvp.yaml + harness-rules.yaml required)
- Retro quantitative requirements (metrics + iteration analysis sections)
- RUNBOOK mandatory sections (deploy, rollback, monitor)
- Operate/Grow minimum artifacts (07-ops-notes.md required)
- Minimum line counts raised across all stages

---

**Version Format**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
