# Changelog

All notable changes to pm-idea-to-mvp pipeline will be documented in this file.

## [6.2.0] - 2026-06-13

### 🎯 Overview

**Enforced Governance version** — based on pm-knowledge-platform post-mortem analysis that revealed 7 critical gaps in pipeline execution quality.

### ✨ New Features

#### P0-1: Mandatory Runtime Verification
- `stage-complete.py` now auto-enables `--runtime` and `--goal` for mvp/ship stages
- No more self-reported task completion without actual verification
- New constants: `MANDATORY_RUNTIME_STAGES`, `MANDATORY_GOAL_STAGES`

#### P0-2: Cross-Document Consistency Checks
- `check_docs_ssot.py` enhanced with `tech-stack-conflict` detection
- Detects when different documents claim different database technologies
- Validates task completion claims against actual artifacts
- Pipeline governance checks (goals/, PROGRESS.md, harness-rules.yaml existence)

#### P0-3: G1/G2 Debate Gate Enforcement
- `validate-gates.py` now checks for `debates/` directory in align/spec stages
- Requires `debate_resolved` marker in debate artifacts
- New check type: `debate_required` in STAGE_FILES config

#### P1-4: Inner Loop Prerequisites
- `inner-loop-driver.py` validates `goals/mvp.yaml` and `harness-rules.yaml` before starting
- Logs iteration results to `feedback.jsonl` for cross-session memory
- Appends iteration history to `PROGRESS.md`
- Auto-generates `harness-improvements.md` on exhaustion

#### P1-5: Retro Quantitative Requirements
- Retro stage now requires `required_sections`: metrics data + iteration analysis
- Minimum lines raised from 15 to 50
- Content patterns enforce quantitative analysis

#### P1-6: RUNBOOK Mandatory Sections
- Ship stage validates three required sections: deploy steps, rollback plan, monitoring
- RUNBOOK minimum lines raised from 10 to 50

#### P2-7: Operate/Grow Minimum Artifacts
- Operate stage now requires `07-ops-notes.md` (was empty)
- Grow stage minimum lines raised from 15 to 30

### 📊 Minimum Lines Changes

| Stage | v6.0 | v6.2 | Reason |
|-------|------|------|--------|
| brief | 5 | 20 | Prevent stub briefs |
| align | 10 | 50 | CONTEXT.md was only 69 lines in real project |
| research | 20 | 50 | Ensure thorough research |
| analysis | 30 | 100 | Ensure deep analysis |
| spec | 20 | 50 | Ensure complete PRD |
| ship | 10 | 50 | Ensure usable RUNBOOK |
| retro | 15 | 50 | Ensure data-driven retro |

### 🐛 Bug Fixes

- Fixed `stage-complete.py` goal-check being optional (now mandatory for mvp/ship/retro)
- Fixed `validate-gates.py` not checking debate artifacts for G1/G2 gates
- Fixed `inner-loop-driver.py` not logging to feedback.jsonl

### 🔧 Technical Changes

- All scripts version bumped to 6.2.0
- `gates.template.json` updated with v6.2 enforcements map
- `goal.template.yaml` expanded with per-stage examples
- `harness-rules.template.yaml` version bumped to 6.2.0
- `SKILL.md` updated with v6.2 changes section and upgrade history

### ✅ Verification

All new checks verified against pm-knowledge-platform:
- `check_docs_ssot.py` correctly detects PostgreSQL/SQLite conflict
- `validate-gates.py` correctly detects missing debates/ directory
- `validate-gates.py` correctly detects missing goals/mvp.yaml
- `stage-complete.py` correctly auto-enables runtime/goal checks

---

## [6.1.0] - 2026-06-12

### Production-tested version

See v6.1.0/ directory for the production-tested variant with knowledge graph visualization, RAG fallback strategy, and tag management enhancements.

---

## [6.0.0] - 2026-06-12

### Initial Loop Engineering Release

- 9-stage pipeline with dual-loop framework
- MVP inner loop (Plan → Code → Test → Observe → Adjust)
- Goal primitives with `goal-check.py`
- On-the-loop human collaboration (risk-based)
- Fine-grained progress tracking with `progress-tracker.py`
- Self-improving harness with `harness-improvements.md`

---

**Version Format**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format, and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
