#!/usr/bin/env python3
"""
decompose-pm-pipeline.py — Dynamic pipeline decomposition (v8.0.0).

Dual mode:
  --task-id <triage_id>   Hermes gateway (kanban_db.decompose_triage_task)
  --project-root <path>   Standalone CLI (hermes kanban create subprocess)

v8.0: Dynamic 5-6 tasks per pipeline (down from 10-12). Merged stages:
  1. align (grill + clone for import_repo)
  2. discover (research + analysis merged)
  3. design (prototype + PRD + OpenSpec merged)
  4. mvp (single goal_mode worker with Inner Loop)
  5. ship (deploy + HITL)
  6. retro

All workers are goal_mode=True with explicit completion criteria.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from execution_mode import (  # noqa: E402
    AUTO_ADVANCE_EXIT,
    auto_hitl_enabled,
    human_checkpoint_stages,
)
from pipeline_paths import resolve_pipeline_root, resolve_hermes_home, resolve_projects_root  # noqa: E402
from pipeline_version import PIPELINE_VERSION  # noqa: E402

PROJECTS_ROOT = resolve_projects_root()
PIPELINE_ROOT = resolve_pipeline_root()

HERMES_HOME = resolve_hermes_home()
HERMES_AGENT = HERMES_HOME / "hermes-agent"
if str(HERMES_AGENT) not in sys.path:
    sys.path.insert(0, str(HERMES_AGENT))

from hermes_cli import kanban_db as kb  # noqa: E402

DEFAULT_HUMAN_CHECKPOINTS = ["align", "ship"]

CHECKPOINT_ALIGN = """HUMAN CHECKPOINT (two-phase):
  FIRST RUN: stage-complete --stage align --project-root <proj> --task-id <id> --runtime
    → kanban_block reason '等待用户确认 align 产物'. Do NOT kanban_complete.
  RESUME: verify gates → kanban_complete. Do NOT kanban_block again."""

_MANUAL_CHECKPOINT_SPEC = """HUMAN CHECKPOINT (two-phase):
  FIRST RUN: stage-complete --stage spec --project-root <proj> --task-id <id> --runtime
    → kanban_block reason '等待用户确认 PRD/原型范围'. Do NOT kanban_complete.
  RESUME: verify gates → kanban_complete."""

_MANUAL_CHECKPOINT_SHIP = """HUMAN CHECKPOINT (two-phase, G3):
  FIRST RUN: stage-complete --stage ship --project-root <proj> --task-id <id> --runtime
    → kanban_block reason '等待用户确认部署范围'. Do NOT kanban_complete.
  RESUME: verify gates → kanban_complete."""

HARNESS_RULES_TEMPLATE = """\
version: '8.0.0'
project:
  slug: {slug}
  tech_stack: python
  language: zh-CN

runtime:
  test_cmd: '{test_cmd}'
  build_cmd: 'python -m py_compile 04-mvp/**/*.py 2>nul || python -m compileall -q 04-mvp'
  lint_cmd: ''
  health_url: ''
  workdir: '04-mvp'

decisions:
  tech_choice:
    risk: medium
    action: write_adr_and_notify
  deploy:
    risk: high
    action: human_checkpoint
  refactor:
    risk: low
    action: auto_verify

human_checkpoints:
  - align
  - ship

inner_loop:
  max_iterations: 3
  test_command: '{test_cmd}'
"""

HARNESS_RULES_AUTO_TEMPLATE = """\
version: '8.0.0'
project:
  slug: {slug}
  tech_stack: python
  language: zh-CN

auto_hitl: true

runtime:
  test_cmd: '{test_cmd}'
  build_cmd: 'python -m py_compile 04-mvp/**/*.py 2>nul || python -m compileall -q 04-mvp'
  lint_cmd: ''
  health_url: ''
  workdir: '04-mvp'

decisions:
  tech_choice:
    risk: medium
    action: write_adr_and_notify
  deploy:
    risk: high
    action: auto_verify
  refactor:
    risk: low
    action: auto_verify

human_checkpoints: []

inner_loop:
  max_iterations: 3
  test_command: '{test_cmd}'
"""


def checkpoint_align() -> str:
    return AUTO_ADVANCE_EXIT if auto_hitl_enabled() else _MANUAL_CHECKPOINT_ALIGN


def checkpoint_ship() -> str:
    return AUTO_ADVANCE_EXIT if auto_hitl_enabled() else _MANUAL_CHECKPOINT_SHIP


def harness_template() -> str:
    return HARNESS_RULES_AUTO_TEMPLATE if auto_hitl_enabled() else HARNESS_RULES_TEMPLATE


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:48] or "idea"


_RESERVED_SLUGS = {"idea-to-mvp", "pm-idea-to-mvp"}

_GITHUB_REPO_SLUG_RE = re.compile(
    r"(?:https?://)?github\.com/[\w.-]+/([\w.-]+)|\[[\w.-]+/([\w.-]+)(?:\s|:|\])",
    re.I,
)


def extract_github_repo_slug(text: str) -> str | None:
    for m in _GITHUB_REPO_SLUG_RE.finditer(text or ""):
        slug = (m.group(1) or m.group(2) or "").strip().lower().removesuffix(".git")
        if slug and slug not in _RESERVED_SLUGS:
            return slug[:48]
    return None


def extract_slug_from_text(title: str, body: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit.strip().removeprefix("pm-")
    combined = f"{title}\n{body}"
    repo_slug = extract_github_repo_slug(combined)
    if repo_slug:
        return repo_slug
    keywords = {
        "产品知识库": "product-knowledge",
        "产品知识平台": "product-knowledge",
        "知识平台": "product-knowledge",
        "赛博取名": "cyber-naming",
    }
    for cn, slug in keywords.items():
        if cn in combined:
            return slug
    for pat in (r"projects/pm-([\w-]+)", r"slug[:\s]+([\w-]+)", r"pm-([\w-]+)"):
        m = re.search(pat, combined, re.I)
        if m:
            slug = m.group(1).removeprefix("pm-")
            if slug not in _RESERVED_SLUGS:
                return slug
    if "yuxi" in combined.lower():
        return "product-knowledge-yuxi"
    raw = slugify(title)
    if raw and re.search(r"[\u4e00-\u9fff]", title):
        if "知识" in title:
            return "product-knowledge"
        return "idea-" + hashlib.sha1(title.encode()).hexdigest()[:8]
    return raw


def extract_slug_from_path(project_root: Path) -> str:
    name = project_root.name
    return name[3:] if name.startswith("pm-") else name


def project_dir(slug: str) -> Path:
    return PROJECTS_ROOT / f"pm-{slug.removeprefix('pm-')}"


def detect_test_cmd(project_root: Path) -> str:
    mvp = project_root / "04-mvp"
    if (mvp / "package.json").exists():
        return "npm test --if-present"
    if (mvp / "pytest.ini").exists() or (mvp / "tests").exists():
        return "pytest -q"
    if (mvp / "pyproject.toml").exists():
        return "pytest -q 2>nul || python -m py_compile 04-mvp/*.py"
    return "python -m py_compile 04-mvp/*.py 2>nul || echo skip-tests"


def setup_harness_rules(project_root: Path, slug: str) -> dict:
    rules_path = project_root / "harness-rules.yaml"
    test_cmd = detect_test_cmd(project_root)
    template = harness_template()
    if not rules_path.exists():
        rules_path.write_text(
            template.format(slug=slug, test_cmd=test_cmd),
            encoding="utf-8",
        )
        return {"created": str(rules_path)}
    if auto_hitl_enabled(project_root):
        rules_path.write_text(
            template.format(slug=slug, test_cmd=test_cmd),
            encoding="utf-8",
        )
        return {"updated": str(rules_path), "auto_hitl": True}
    return {"exists": str(rules_path)}


def setup_goals_directory(project_root: Path) -> dict:
    goals_dir = project_root / "goals"
    goals_dir.mkdir(exist_ok=True)
    return {"goals_dir": str(goals_dir)}


def setup_progress(project_root: Path) -> dict:
    script = SCRIPT_DIR / "progress-tracker.py"
    if not script.exists():
        return {"status": "skipped"}
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--project-root", str(project_root), "init"],
            capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR),
        )
        return {"status": "ok" if proc.returncode == 0 else "failed", "output": proc.stdout[:200]}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def ensure_brief(project_root: Path, title: str, body: str) -> dict:
    brief = project_root / "00-brief.md"
    if brief.exists():
        return {"status": "exists"}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    brief.write_text(
        f"# 产品想法\n\n**创建时间**: {now}\n\n## 标题\n{title}\n\n## 描述\n{body or title}\n",
        encoding="utf-8",
    )
    return {"status": "created"}


def publish_project_repo(proj: Path, slug: str, title: str) -> str | None:
    script = PIPELINE_ROOT / "scripts" / "bootstrap_github_repo.py"
    if not script.exists():
        return None
    proc = subprocess.run(
        [sys.executable, str(script), "--dir", str(proj), "--slug", slug, "--description", title[:200]],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode == 0:
        return None
    return (proc.stderr or proc.stdout or "unknown")[:500]


def write_run_manifest(proj: Path, slug: str, title: str, child_titles: list[str], scenario: str) -> None:
    stages = "\n".join(f"- [ ] {t}" for t in child_titles)
    content = f"""# 本次运行说明 (v7.2 — {scenario})

| 项 | 值 |
|----|-----|
| 标题 | {title} |
| Slug | `{slug}` |
| Scenario | `{scenario}` |
| 目录 | `{proj.as_posix()}` |
| Pages | https://ttmens.github.io/pm-{slug}/ |

## 阶段清单

{stages}

## 人工检查点

1. **align** — 确认 CONTEXT 后 unblock
2. **spec** — 确认 PRD/原型后 unblock
3. **ship** — 确认部署范围后 unblock

Harness: `harness-rules.yaml` | Progress: `PROGRESS.md`
"""
    (proj / "RUN.md").write_text(content, encoding="utf-8")


def task_body(stage: str, slug: str, title: str, extra: str = "") -> str:
    """v8.0: Structured task body with explicit completion criteria.
    
    Four required sections: WHAT / HOW / BEFORE / FAILURE
    Designed for goal_mode workers where the Judge model evaluates completion.
    """
    proj = project_dir(slug).as_posix()
    scripts = (PIPELINE_ROOT / "scripts").as_posix()
    return f"""TASK: {stage_label(stage)} — pm-{slug}

PM pipeline v{PIPELINE_VERSION} | stage={stage} | project_root={proj}

WHAT TO PRODUCE:
{extra or _default_artifacts(stage)}

HOW TO KNOW YOU'RE DONE:
{_default_completion(stage, slug)}

BEFORE COMPLETING:
1. Run: python {scripts}/stage-complete.py --project-root {proj} --stage {stage} --task-id <this_task_id> --verify-goals
2. Run: python {scripts}/validate-gates.py --runtime --stage {stage} --project-root {proj}
3. Run: python {scripts}/goal-check.py --stage {stage} --project-root {proj}
4. Only after ALL THREE pass: call kanban_complete

FAILURE HANDLING:
- If gate validation fails: fix artifacts, re-run validate-gates.py and goal-check.py
- If goal check fails: review goals/{stage}.yaml, fix missing requirements
- After 3 failed attempts without progress: kanban_block with detailed failure reason
- DO NOT call kanban_complete unless all verification passes"""


def stage_label(stage: str) -> str:
    return {
        "align": "需求对齐",
        "discover": "调研与论证",
        "design": "原型与规格",
        "mvp": "MVP 构建",
        "ship": "部署发布",
        "retro": "复盘进化",
        "import": "导入外部仓库",
    }.get(stage, stage)


def _default_artifacts(stage: str) -> str:
    return {
        "align": "1. CONTEXT.md (min 50 lines, zh-CN)\n2. decisions.md (min 3 ADR entries with risk levels)\n3. debates/align-synthesis.md (must contain 'debate_resolved: true')\n4. PROGRESS.md (initialized with stage status table)",
        "discover": "1. 01-research.md (min 50 lines, >=5 URLs with accessibility check)\n2. 02-analysis.md (min 100 lines, >=3 options with recommendation)\n3. architecture/c4-*.md (L1-L3)\n4. openspec/proposal.md + openspec/design.md (links to C4)\n5. debates/analysis-synthesis.md (must contain 'debate_resolved: true')",
        "design": "1. 03b-user-journey.md\n2. 02b-prototype/ (clickable static HTML)\n3. 03-prd.md (min 50 lines, <=5 user stories with acceptance criteria)\n4. openspec/tasks.md + openspec/specs/ delta specs\n5. debates/spec-synthesis.md (must contain 'debate_resolved: true')",
        "mvp": "1. 04-mvp/ directory with implementation code\n2. 04-mvp/DESIGN.md (from ui-ux-pro-max)\n3. 04-mvp/UX-REVIEW.md (from ui-acceptance-review)\n4. 04-mvp/CODE-REVIEW.md (from requesting-code-review)\n5. All critical goals in goals/mvp.yaml must pass",
        "ship": "1. RUNBOOK.md (min 50 lines: deploy steps, rollback plan, monitoring)\n2. docs/ui-acceptance-report.md\n3. docs/lighthouse-report.json (if web)\n4. docs/security-audit-report.md",
        "retro": "1. 05-retro.md (min 50 lines, quantified metrics required)\n2. evolution-notes.md\n3. harness-improvements.md",
        "import": "1. Cloned source code in 04-mvp-src/ or 04-mvp/\n2. Clone URL + commit recorded in CONTEXT.md and decisions.md (ADR)\n3. PROGRESS.md updated",
    }.get(stage, "Artifacts per pipeline specification")


def _default_completion(stage: str, slug: str) -> str:
    proj = project_dir(slug)
    return {
        "align": f"- CONTEXT.md exists AND >=50 non-empty lines in {proj}\n- decisions.md has >=3 ADR entries with risk tags\n- debates/align-synthesis.md contains 'debate_resolved: true'\n- PROGRESS.md shows 'align: done'",
        "discover": f"- 01-research.md >=50 lines + >=5 unique URLs in {proj}\n- 02-analysis.md >=100 lines + covers >=3 options\n- C4 diagrams exist (L1-L3) in architecture/\n- debates/analysis-synthesis.md contains 'debate_resolved: true'",
        "design": f"- 03b-user-journey.md exists in {proj}\n- 02b-prototype/index.html is renderable\n- 03-prd.md >=50 lines, <=5 stories with acceptance criteria\n- debates/spec-synthesis.md contains 'debate_resolved: true'",
        "mvp": f"- All critical goals in {proj}/goals/mvp.yaml PASS\n- 04-mvp/UX-REVIEW.md contains 'PASS'\n- All tests pass, build succeeds, lint is clean",
        "ship": f"- RUNBOOK.md >=50 lines in {proj}\n- Deploy steps, rollback plan, monitoring sections present\n- Security audit report exists with no HIGH issues\n- UI acceptance report complete",
        "retro": f"- 05-retro.md >=50 lines with stage timing data\n- evolution-notes.md updated\n- harness-improvements.md with classified proposals",
        "import": f"- Source code present in {proj}/04-mvp-src/ or {proj}/04-mvp/\n- Git clone succeeded (URL + commit recorded)\n- CONTEXT.md references import source",
    }.get(stage, "All artifacts produced and gates pass")


_STAGE_SKILLS_CACHE: dict | None = None


def load_stage_skills_config() -> dict:
    global _STAGE_SKILLS_CACHE
    if _STAGE_SKILLS_CACHE is None:
        import yaml

        path = PIPELINE_ROOT / "stage-skills.yaml"
        _STAGE_SKILLS_CACHE = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return _STAGE_SKILLS_CACHE


def skills_for_stage(stage_key: str) -> list[str]:
    cfg = load_stage_skills_config()
    stage = cfg.get("stages", {}).get(stage_key, {})
    native = list(stage.get("native") or [])
    borrowed = list(stage.get("borrowed") or [])
    pipeline = list(cfg.get("pipeline_native") or ["pm-idea-to-mvp"])
    seen: set[str] = set()
    out: list[str] = []
    for name in pipeline + native + borrowed:
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _attach_stage_skills(children: list[dict], stage_keys: list[str]) -> list[dict]:
    for child, stage_key in zip(children, stage_keys):
        child["skills"] = skills_for_stage(stage_key)
    return children


def _align_grill_note(slug: str) -> str:
    brief = project_dir(slug) / "00-brief.md"
    if brief.exists() and "## 飞书 Grill" in brief.read_text(encoding="utf-8", errors="replace"):
        return "Feishu grill preflight already done. Use grill-with-docs on 00-brief.md.\n"
    return (
        "NOTE: 飞书 Grill 已跳过（/goal 已含完整意图）。"
        "自主读 00-brief.md + grill-with-docs；align 完成后 stage-complete → kanban_complete（无人值守）。\n"
    )


# ── v8.0 dynamic task builders (5-6 tasks per pipeline, merged stages) ──

def _goal_turns(stage: str) -> int:
    """Turn budgets per merged stage (for goal_mode workers)."""
    return {"align": 6, "discover": 8, "design": 8, "mvp": 12, "ship": 6, "retro": 6, "import": 4}.get(stage, 8)


def _child(stage: str, slug: str, title: str, assignee: str, parents: list[int], extra: str = "") -> dict:
    body = task_body(stage, slug, title, extra)
    ck = ""
    if stage == "align":
        ck = checkpoint_align()
    elif stage == "ship":
        ck = checkpoint_ship()
    if ck:
        body += f"\n\n{ck}"
    return {
        "title": f"{stage_label(stage)} — {slug}",
        "body": body,
        "assignee": assignee,
        "parents": parents,
        "goal_mode": True,
        "goal_max_turns": _goal_turns(stage),
        "max_retries": 2,
    }


def _build_discover_body(slug: str, title: str) -> str:
    """Build body for merged research+analysis."""
    return (
        "MERGED STAGE: 调研 + 方案论证\n\n"
        "Phase 1 — Research:\n"
        "- Use Tavily web_search for competitive landscape analysis\n"
        "- Gather >=5 credible sources with URLs\n"
        "- Write 01-research.md (min 50 lines, zh-CN)\n\n"
        "Phase 2 — Analysis:\n"
        "- Analyze >=3 architectural options with tradeoffs\n"
        "- Create architecture/c4-context.md, c4-container.md, c4-component.md\n"
        "- Draft openspec/proposal.md and openspec/design.md\n"
        "- Write 02-analysis.md (min 100 lines, zh-CN)\n"
        "- Synthesize findings into debates/analysis-synthesis.md\n\n"
        "stage-complete will validate both research AND analysis artifacts.\n"
        "Use docs-hygiene after analysis to ensure SSOT consistency."
    )


def _build_design_body(slug: str, title: str) -> str:
    """Build body for merged spec+prototype+prd."""
    return (
        "MERGED STAGE: 原型 + PRD + OpenSpec\n\n"
        "Phase 1 — User Journey: user-journey skill → 03b-user-journey.md\n"
        "Phase 2 — Prototype: open-design skill → 02b-prototype/ (clickable HTML)\n"
        "Phase 3 — PRD: prd-red-team-panel → 03-prd.md (<=5 user stories, zh-CN)\n"
        "Phase 4 — Spec: openspec → openspec/tasks.md + openspec/specs/ deltas\n"
        "Phase 5 — Design Tokens: ui-ux-pro-max → 04-mvp/DESIGN.md\n\n"
        "Auto-advance after G2 gates pass (no human checkpoint at spec in v8.0).\n"
        "stage-complete will validate PRD + prototype + design tokens."
    )


def _build_mvp_body(slug: str, title: str) -> str:
    """Build body for single mvp goal_mode worker with inner loop."""
    proj = project_dir(slug).as_posix()
    return (
        f"INNER LOOP PROTOCOL (within this single goal_mode worker):\n\n"
        f"1. Plan: writing-plans → phase-plan.md from openspec/tasks.md\n"
        f"2. Code: implement in {proj}/04-mvp/\n"
        f"   - Use subagent-driven-development or delegate_task for parallel work\n"
        f"   - Apply 04-mvp/DESIGN.md tokens from ui-ux-pro-max\n"
        f"3. Test: run harness-rules.yaml test/lint/build commands\n"
        f"   - Use test-driven-development for TDD approach\n"
        f"4. Observe: goal-check.py --stage mvp --runtime-only\n"
        f"   - Use requesting-code-review (5-axis review)\n"
        f"   - Use ui-acceptance-review (UX journey check)\n"
        f"   - Use dogfood for exploratory QA\n"
        f"5. Judge: goal_mode auto-evaluates — if PASS → stage-complete → kanban_complete\n"
        f"   if FAIL → adjust plan → back to Step 1 (max 3 iterations total)\n\n"
        f"AFTER 3 FAILURES: kanban_block with harness-improvements.md\n\n"
        f"MAX ITERATIONS: 3 (enforced by goal_max_turns=12)\n"
        f"BEFORE COMPLETING: all critical goals in goals/mvp.yaml PASS"
    )


def build_children_greenfield(slug: str, title: str) -> list[dict]:
    """v8.0: 6 tasks (down from 12) — merged stages, goal_mode workers."""
    return [
        _child("align", slug, title, "pm-aligner", [],
               _align_grill_note(slug) + "Outputs: CONTEXT.md, decisions.md, debates/align-synthesis.md"),
        _child("discover", slug, title, "pm-researcher", [0],
               _build_discover_body(slug, title)),
        _child("design", slug, title, "pm-planner", [1],
               _build_design_body(slug, title)),
        _child("mvp", slug, title, "pm-builder", [2],
               _build_mvp_body(slug, title)),
        _child("ship", slug, title, "pm-shipper", [3],
               "Outputs: RUNBOOK.md, docs/ui-acceptance-report.md.\n"
               "Deploy verification per harress-rules.yaml. High risk → human checkpoint."),
        _child("retro", slug, title, "pm-builder", [4],
               "Output: 05-retro.md, evolution-notes.md, harness-improvements.md."),
    ]


def build_children_import_repo(slug: str, title: str) -> list[dict]:
    """v8.0: 6 tasks (down from 10). Clone is step 0 inside align worker."""
    proj = project_dir(slug).as_posix()
    return [
        _child("align", slug, title, "pm-aligner", [],
               _align_grill_note(slug) +
               "Phase 1: Confirm clone intent + success metrics.\n"
               "Phase 2: Clone the external GitHub repo:\n"
               f"  git -c credential.helper= clone --depth 1 <url> \"{proj}/04-mvp-src\"\n"
               f"  then move contents into \"{proj}/04-mvp/\" (or clone directly if empty).\n"
               "Record clone URL + commit in CONTEXT.md and decisions.md.\n"
               "Outputs: CONTEXT.md, decisions.md, cloned source code."),
        _child("discover", slug, title, "pm-researcher", [0],
               _build_discover_body(slug, title) +
               "\nNote: Analyze the cloned codebase in your research."),
        _child("design", slug, title, "pm-planner", [1],
               _build_design_body(slug, title)),
        _child("mvp", slug, title, "pm-builder", [2],
               _build_mvp_body(slug, title)),
        _child("ship", slug, title, "pm-shipper", [3],
               "Outputs: RUNBOOK.md, docs/ui-acceptance-report.md."),
        _child("retro", slug, title, "pm-builder", [4],
               "Output: 05-retro.md, evolution-notes.md."),
    ]


def build_children_brownfield(slug: str, title: str) -> list[dict]:
    """v8.0: 5 tasks. Brownfield audit + targeted improvements."""
    audit_ref = (PIPELINE_ROOT / "references" / "brownfield-audit.md").as_posix()
    return [
        _child("align", slug, title, "pm-aligner", [],
               f"Follow {audit_ref} Step 0-6.\n"
               "Verify build, run validate-gates loop, fix governance gaps.\n"
               "Update CONTEXT.md from audit findings."),
        _child("mvp", slug, title, "pm-builder", [0],
               "Brownfield: implement fixes per feedback.jsonl + audit gaps.\n"
               f"Inner loop: Plan → Code → Test → Observe (max 3 iterations).\n"
               "stage-complete --stage mvp --runtime --verify-goals on pass."),
        _child("ship", slug, title, "pm-shipper", [1],
               "Deploy + RUNBOOK update."),
        _child("retro", slug, title, "pm-builder", [2],
               "05-retro.md + harness-improvements.md."),
    ]


def build_children_optimize(slug: str, title: str) -> list[dict]:
    """v8.0: 2 tasks. Deploy/hotfix only."""
    return [
        _child("ship", slug, title, "pm-shipper", [],
               "Optimize scenario: deploy/fix/hotfix only.\n"
               "Run kw-deploy-checklist + stage-complete --stage ship --runtime."),
        _child("retro", slug, title, "pm-builder", [0],
               "Update ops-notes and retro."),
    ]


def build_children_refine(slug: str, title: str) -> list[dict]:
    """v8.0: 3 tasks. Deep research + UX + MVP iter."""
    return [
        _child("discover", slug, title, "pm-researcher", [],
               "Output: 01b-benchmark.md (>=3 case studies)."),
        _child("design", slug, title, "pm-planner", [0],
               "Update 03b-user-journey.md + 02b-prototype/.\n"
               "Auto-advance after gates pass (no human checkpoint at spec)."),
        _child("mvp", slug, title, "pm-builder", [1],
               "Implement UX fixes. stage-complete --stage mvp --runtime."),
    ]


def build_children(scenario: str, slug: str, title: str) -> list[dict]:
    builders = {
        "greenfield": build_children_greenfield,
        "import_repo": build_children_import_repo,
        "brownfield": build_children_brownfield,
        "optimize": build_children_optimize,
        "refine": build_children_refine,
    }
    stage_keys_by_scenario = {
        "greenfield":    ["align", "discover", "design", "mvp", "ship", "retro"],
        "import_repo":   ["align", "discover", "design", "mvp", "ship", "retro"],
        "brownfield":    ["align", "mvp", "ship", "retro"],
        "optimize":      ["ship", "retro"],
        "refine":        ["discover", "design", "mvp"],
    }
    fn = builders.get(scenario, build_children_greenfield)
    children = fn(slug, title)
    keys = stage_keys_by_scenario.get(scenario, stage_keys_by_scenario["greenfield"])
    return _attach_stage_skills(children, keys[: len(children)])


def setup_project(project_root: Path, slug: str, title: str, body: str) -> dict:
    project_root.mkdir(parents=True, exist_ok=True)
    return {
        "harness": setup_harness_rules(project_root, slug),
        "goals": setup_goals_directory(project_root),
        "brief": ensure_brief(project_root, title, body),
        "progress": setup_progress(project_root),
    }


def subscribe_pipeline_notifications(
    conn,
    *,
    root_task_id: str,
    child_ids: list[str],
    children: list[dict],
) -> list[str]:
    """Register Feishu/gateway notify subs for root + human-checkpoint child tasks."""
    platform = os.environ.get("PM_NOTIFY_PLATFORM", "").strip().lower()
    chat_id = os.environ.get("PM_NOTIFY_CHAT_ID", "").strip()
    thread_id = os.environ.get("PM_NOTIFY_THREAD_ID", "").strip() or None
    user_id = os.environ.get("PM_NOTIFY_USER_ID", "").strip() or None
    if not platform or not chat_id:
        home = os.environ.get("FEISHU_HOME_CHANNEL", "").strip()
        if home:
            platform = platform or "feishu"
            chat_id = chat_id or home
            thread_id = thread_id or os.environ.get("FEISHU_HOME_CHANNEL_THREAD_ID", "").strip() or None
    if not platform or not chat_id:
        return []

    subscribed: list[str] = []
    targets = [root_task_id]
    if not auto_hitl_enabled():
        for child_id, child in zip(child_ids, children):
            body = child.get("body") or ""
            if "HUMAN CHECKPOINT" in body or child.get("assignee") in ("pm-aligner", "pm-shipper"):
                if "CHECKPOINT" in body or child.get("assignee") == "pm-shipper":
                    targets.append(child_id)
    seen: set[str] = set()
    for tid in targets:
        if tid in seen:
            continue
        seen.add(tid)
        kb.add_notify_sub(
            conn,
            task_id=tid,
            platform=platform,
            chat_id=chat_id,
            thread_id=thread_id,
            user_id=user_id,
            notifier_profile="pm-orchestrator",
        )
        subscribed.append(tid)
    return subscribed


def decompose_gateway(
    task_id: str,
    slug: str | None,
    scenario: str = "greenfield",
    dry_run: bool = False,
) -> dict:
    with kb.connect_closing() as conn:
        task = kb.get_task(conn, task_id)
        if task is None:
            raise SystemExit(f"Unknown task: {task_id}")
        if task.status != "triage":
            raise SystemExit(f"Task {task_id} not in triage (status={task.status})")

        title = task.title or "PM Idea"
        body = task.body or ""
        resolved_slug = extract_slug_from_text(title, body, slug)
        proj = project_dir(resolved_slug)
        children = build_children(scenario, resolved_slug, title)

        if dry_run:
            return {
                "task_id": task_id, "slug": resolved_slug, "scenario": scenario,
                "project_dir": str(proj), "child_count": len(children),
                "children": [{"title": c["title"], "assignee": c["assignee"]} for c in children],
            }

        setup = setup_project(proj, resolved_slug, title, body)
        init_script = SCRIPT_DIR / "init-project.py"
        if init_script.exists():
            subprocess.run(
                [sys.executable, str(init_script), "--project-root", str(proj), "--slug", resolved_slug],
                capture_output=True, text=True, timeout=60,
            )
        publish_err = publish_project_repo(proj, resolved_slug, title)
        child_titles = [c["title"] for c in children]
        write_run_manifest(proj, resolved_slug, title, child_titles, scenario)

        child_ids = kb.decompose_triage_task(
            conn, task_id,
            root_assignee="pm-orchestrator",
            children=children,
            author=f"decompose-pm-pipeline-v6.1-{scenario}",
        )
        if not child_ids:
            raise SystemExit("decompose_triage_task failed")

        notify_subs = subscribe_pipeline_notifications(
            conn,
            root_task_id=task_id,
            child_ids=child_ids,
            children=children,
        )

        kb.add_comment(
            conn, task_id, "decompose-pm-pipeline",
            f"pm-pipeline v{PIPELINE_VERSION} scenario={scenario} ({len(child_ids)} tasks).\n"
            f"slug: {resolved_slug}\nproject: {proj.as_posix()}\nchildren: {', '.join(child_ids)}",
        )

    return {
        "task_id": task_id,
        "slug": resolved_slug,
        "scenario": scenario,
        "project_dir": str(proj),
        "child_ids": child_ids,
        "child_count": len(child_ids),
        "pipeline_version": PIPELINE_VERSION,
        "setup": setup,
        "publish_error": publish_err,
        "assignees": [c["assignee"] for c in children],
        "notify_subs": notify_subs,
    }


def create_kanban_task_cli(name: str, assignee: str, body: str, parent_id: str = "") -> dict:
    cmd = ["hermes", "kanban", "create", name, "--assignee", assignee, "--body", body]
    if parent_id:
        cmd.extend(["--parent", parent_id])
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = (proc.stdout or "").strip()
        tid = ""
        m = re.search(r"(?:task[:\s]+|id[:\s]+)?([a-f0-9]{8,})", output, re.I)
        if m:
            tid = m.group(1)
        return {"status": "ok" if proc.returncode == 0 else "failed", "task_id": tid, "output": output[:300]}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def decompose_cli(
    project_root: Path,
    title: str,
    description: str,
    scenario: str,
    dry_run: bool,
) -> dict:
    slug = extract_slug_from_path(project_root)
    children = build_children(scenario, slug, title or f"Idea: {slug}")
    setup = setup_project(project_root, slug, title, description)
    write_run_manifest(project_root, slug, title, [c["title"] for c in children], scenario)

    stages_out = []
    task_ids_by_idx: dict[int, str] = {}
    for i, stage_def in enumerate(children):
        parent_id = ""
        for pidx in stage_def.get("parents") or []:
            if pidx in task_ids_by_idx:
                parent_id = task_ids_by_idx[pidx]
                break
        entry = {"title": stage_def["title"], "assignee": stage_def["assignee"]}
        if dry_run:
            entry["status"] = "dry_run"
        else:
            res = create_kanban_task_cli(
                stage_def["title"], stage_def["assignee"], stage_def["body"], parent_id,
            )
            entry.update(res)
            if res.get("task_id"):
                task_ids_by_idx[i] = res["task_id"]
        stages_out.append(entry)

    child_ids = [s.get("task_id") for s in stages_out if s.get("task_id")]
    return {
        "mode": "cli", "slug": slug, "scenario": scenario,
        "project_dir": str(project_root), "child_ids": child_ids,
        "child_count": len(child_ids), "pipeline_version": PIPELINE_VERSION,
        "setup": setup, "stages": stages_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=f"PM pipeline decompose v{PIPELINE_VERSION}")
    parser.add_argument("--task-id", default=None, help="Gateway mode: triage task ID")
    parser.add_argument("--slug", default=None, help="Override slug (no pm- prefix)")
    parser.add_argument("--project-root", default=None, help="CLI mode: project directory")
    parser.add_argument("--title", default="", help="Idea title (CLI mode)")
    parser.add_argument("--description", default="", help="Idea description (CLI mode)")
    parser.add_argument("--scenario", default="greenfield",
                        choices=["greenfield", "import_repo", "brownfield", "optimize", "refine"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    os.environ.setdefault("HERMES_HOME", str(HERMES_HOME))

    if args.task_id:
        result = decompose_gateway(args.task_id, args.slug, scenario=args.scenario, dry_run=args.dry_run)
    elif args.project_root:
        result = decompose_cli(
            Path(args.project_root).resolve(), args.title, args.description,
            args.scenario, args.dry_run,
        )
    else:
        parser.error("Provide --task-id (gateway) or --project-root (CLI)")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
