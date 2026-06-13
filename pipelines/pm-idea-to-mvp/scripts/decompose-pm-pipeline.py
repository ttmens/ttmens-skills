#!/usr/bin/env python3
"""
decompose-pm-pipeline.py — Decompose a product idea into kanban tasks (v6.0.0).

Creates 9 child tasks for the pm-idea-to-mvp pipeline stages:
  T1: Align → T2: Research → T3: Analysis → T4: Spec → T5: MVP
  → T6: Ship → T7: Operate → T8: Grow → T9: Retro

Also sets up:
  - harness-rules.yaml (from template)
  - PROGRESS.md (from openspec/tasks.md)
  - goals/ directory with default goal YAML per stage

Uses hermes kanban CLI for task creation.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root, resolve_skills_root

PIPELINE_VERSION = "6.0.0"

# Stage definitions with assignees and dependencies
STAGES = [
    {
        "id": "T1",
        "name": "Stage 0+1: 对齐想法",
        "assignee": "pm-aligner",
        "stage": "align",
        "parent_offset": None,  # No parent (root child)
        "body_template": """\
## 任务：对齐想法 (Align)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: align (G1)

### 指令
1. 读取 `00-brief.md` 了解产品想法
2. 运行 `grill-me`（如无 CONTEXT.md）或 `grill-with-docs`
3. 一次一个问题，不做代码/研究/推荐
4. 产出 `CONTEXT.md` + 更新 `decisions.md`
5. 完成后运行:
   ```
   python {{scripts_dir}}/stage-complete.py --stage align --project-root {{project_root}} --task-id {{task_id}} --runtime
   ```

### 人工检查点
完成后等待用户确认（首次 block，resume complete）。
""",
    },
    {
        "id": "T2",
        "name": "Stage 2: 深度调研",
        "assignee": "pm-researcher",
        "stage": "research",
        "parent_offset": -1,  # Parent is previous task
        "body_template": """\
## 任务：深度调研 (Research)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: research

### 指令
1. 读取 `CONTEXT.md` + `00-brief.md`
2. 使用 Tavily 搜索（browser 备用）
3. 产出 `01-research.md`：竞品、来源URL(≥5)、置信度标签
4. **必须** `write_file` 落盘；禁止仅 kanban_comment
5. 完成后运行:
   ```
   python {{scripts_dir}}/stage-complete.py --stage research --project-root {{project_root}} --task-id {{task_id}} --verify-goals
   ```
""",
    },
    {
        "id": "T3",
        "name": "Stage 3: 方案论证",
        "assignee": "pm-analyst",
        "stage": "analysis",
        "parent_offset": -1,
        "body_template": """\
## 任务：方案论证 (Analysis)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: analysis

### 指令
1. 读取 `01-research.md` + `CONTEXT.md`
2. 产出 `02-analysis.md`：≥3方案、推荐、风险
3. 运行 `c4-architecture`：产出 `architecture/c4-*.md`
4. 起草 `openspec/proposal.md`；`openspec/design.md` 链接 C4
5. 不写实现代码
6. 完成后运行:
   ```
   python {{scripts_dir}}/stage-complete.py --stage analysis --project-root {{project_root}} --task-id {{task_id}}
   ```
""",
    },
    {
        "id": "T4",
        "name": "Stage 4: 原型+PRD+OpenSpec",
        "assignee": "pm-planner",
        "stage": "spec",
        "parent_offset": -1,
        "body_template": """\
## 任务：原型+PRD+OpenSpec (Spec)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: spec (G2)

### 指令
1. `user-journey` → `03b-user-journey.md`
2. `open-design` 原型（静态 HTML）
3. `03-prd.md`：≤5 用户故事、验收标准
4. `openspec/tasks.md` + `openspec/specs/` delta specs
5. 完成后运行:
   ```
   python {{scripts_dir}}/stage-complete.py --stage spec --project-root {{project_root}} --task-id {{task_id}} --runtime
   ```

### 人工检查点
完成后等待用户确认（首次 block，resume complete）。
""",
    },
    {
        "id": "T5a",
        "name": "Stage 5a: MVP Plan",
        "assignee": "pm-builder",
        "stage": "mvp-plan",
        "parent_offset": -1,
        "body_template": """\
## 任务：MVP Plan

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}

1. `writing-plans` + `progress-tracker.py init`
2. 产出 `phase-plan.md`
""",
    },
    {
        "id": "T5b",
        "name": "Stage 5b: MVP Inner Loop",
        "assignee": "pm-builder",
        "stage": "mvp-build",
        "parent_offset": -1,
        "body_template": """\
## 任务：MVP Inner Loop (Build/Test)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}

1. 实现 `04-mvp/`（subagent / opencode）
2. 每轮: `python {{scripts_dir}}/inner-loop-driver.py --project-root {{project_root}}`
3. FAIL → adjust; PASS → T5c
""",
    },
    {
        "id": "T5c",
        "name": "Stage 5c: MVP G3 Verify",
        "assignee": "pm-builder",
        "stage": "mvp",
        "parent_offset": -1,
        "body_template": """\
## 任务：MVP G3 验证

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: mvp (G3)

1. UI acceptance quick/full
2. `python {{scripts_dir}}/stage-complete.py --stage mvp --project-root {{project_root}} --task-id {{task_id}} --runtime --verify-goals`
""",
    },
    {
        "id": "T6",
        "name": "Stage 6: 发布准备",
        "assignee": "pm-shipper",
        "stage": "ship",
        "parent_offset": -1,
        "body_template": """\
## 任务：发布准备 (Ship)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: ship

### 指令
1. 产出 `RUNBOOK.md`：部署、回滚、监控
2. 运行 `ui-acceptance-review`（完整模式）
3. 产出 `docs/ui-acceptance-report.md`
4. 安全审计（`pm-security-audit-static`）
5. 完成后运行:
   ```
   python {{scripts_dir}}/stage-complete.py --stage ship --project-root {{project_root}} --task-id {{task_id}} --runtime
   ```

### 人工检查点
Ship 阶段始终需要用户确认后才能发布。
""",
    },
    {
        "id": "T7",
        "name": "Stage 7: 运维",
        "assignee": "pm-operator",
        "stage": "operate",
        "parent_offset": -1,
        "body_template": """\
## 任务：运维 (Operate)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: operate

### 指令
1. 审阅 `RUNBOOK.md`
2. 确认监控和告警配置
3. 记录运维笔记
4. 完成后运行:
   ```
   python {{scripts_dir}}/stage-complete.py --stage operate --project-root {{project_root}} --task-id {{task_id}}
   ```
""",
    },
    {
        "id": "T8",
        "name": "Stage 8: 增长",
        "assignee": "pm-growth",
        "stage": "grow",
        "parent_offset": -1,
        "body_template": """\
## 任务：增长 (Grow)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: grow

### 指令
1. 产出 `06-growth.md`：北极星指标、增长渠道、策略
2. 运行 `pm-north-star-metric`
3. 运行 `pm-gtm-strategy`
4. 完成后运行:
   ```
   python {{scripts_dir}}/stage-complete.py --stage grow --project-root {{project_root}} --task-id {{task_id}} --verify-goals
   ```
""",
    },
    {
        "id": "T9",
        "name": "Stage 9: 回顾+进化",
        "assignee": "pm-builder",
        "stage": "retro",
        "parent_offset": -1,
        "body_template": """\
## 任务：回顾+进化 (Retro)

**Pipeline**: pm-idea-to-mvp v{version}
**Project Root**: {{project_root}}
**Stage**: retro

### 指令
1. 产出 `05-retro.md`（简体中文）：
   - 阶段时间 & 技能命中/未命中
   - 假设验证
   - `skill_patch_proposals[]` 用于流水线进化
   - `feedback.jsonl` 中的待处理项
2. 更新 `evolution-notes.md`
3. 运行 `pm-git-publish`
4. 完成后运行:
   ```
   python {{scripts_dir}}/stage-complete.py --stage retro --project-root {{project_root}} --task-id {{task_id}}
   ```
""",
    },
]

# Default goals per stage
DEFAULT_GOALS = {
    "align": {
        "stage": "align",
        "goals": [
            {"id": "A1", "description": "CONTEXT.md exists with ≥10 lines", "type": "min_lines", "target": "CONTEXT.md", "min": 10},
            {"id": "A2", "description": "Decisions documented", "type": "min_lines", "target": "decisions.md", "min": 5},
            {"id": "A3", "description": "Contains assumptions", "type": "content_match", "target": "CONTEXT.md", "pattern": "假设|assumption|前提"},
            {"id": "A4", "description": "Assumption debate resolved", "type": "debate_resolved", "debates_dir": "debates", "stage_prefix": "align"},
        ],
    },
    "research": {
        "stage": "research",
        "goals": [
            {"id": "R1", "description": "Research has ≥5 source URLs", "type": "url_count", "target": "01-research.md", "min": 5},
            {"id": "R2", "description": "Competitor analysis present", "type": "content_match", "target": "01-research.md", "pattern": "竞品|competitor|对比"},
            {"id": "R3", "description": "At least 3 competitor rows", "type": "min_table_rows", "target": "01-research.md", "min": 3},
        ],
    },
    "analysis": {
        "stage": "analysis",
        "goals": [
            {"id": "AN1", "description": "Analysis doc ≥30 lines", "type": "min_lines", "target": "02-analysis.md", "min": 30},
            {"id": "AN2", "description": "Multiple options analyzed", "type": "content_match", "target": "02-analysis.md", "pattern": "方案|option|推荐|recommend"},
            {"id": "AN3", "description": "Risk assessment present", "type": "content_match", "target": "02-analysis.md", "pattern": "风险|risk|隐患"},
            {"id": "AN4", "description": "Architecture PK debate resolved", "type": "debate_resolved", "debates_dir": "debates", "stage_prefix": "analysis"},
        ],
    },
    "spec": {
        "stage": "spec",
        "goals": [
            {"id": "S1", "description": "PRD exists", "type": "file_exists", "target": "03-prd.md"},
            {"id": "S2", "description": "User journey exists", "type": "file_exists", "target": "03b-user-journey.md"},
            {"id": "S3", "description": "Tasks breakdown exists", "type": "file_exists", "target": "openspec/tasks.md"},
            {"id": "S4", "description": "User stories defined", "type": "content_match", "target": "03-prd.md", "pattern": "用户故事|user stor|作为.*我想"},
            {"id": "S5", "description": "PRD red-team debate resolved", "type": "debate_resolved", "debates_dir": "debates", "stage_prefix": "spec"},
        ],
    },
    "mvp": {
        "stage": "mvp",
        "goals": [
            {"id": "M1", "description": "MVP README exists", "type": "file_exists", "target": "04-mvp/README.md"},
            {"id": "M2", "description": "Design tokens exist", "type": "file_exists", "target": "04-mvp/DESIGN.md"},
            {"id": "M3", "description": "Tests pass", "type": "command_pass", "command": "pytest -q --co -q 2>/dev/null || echo 'no tests'", "workdir": "04-mvp"},
        ],
    },
    "ship": {
        "stage": "ship",
        "goals": [
            {"id": "SH1", "description": "Runbook exists", "type": "min_lines", "target": "RUNBOOK.md", "min": 10},
            {"id": "SH2", "description": "Deploy instructions present", "type": "content_match", "target": "RUNBOOK.md", "pattern": "部署|deploy|发布"},
            {"id": "SH3", "description": "Rollback plan present", "type": "content_match", "target": "RUNBOOK.md", "pattern": "回滚|rollback|恢复"},
        ],
    },
    "grow": {
        "stage": "grow",
        "goals": [
            {"id": "G1", "description": "Growth doc exists", "type": "min_lines", "target": "06-growth.md", "min": 15},
            {"id": "G2", "description": "North star metric defined", "type": "content_match", "target": "06-growth.md", "pattern": "北极星|north.star|核心指标"},
        ],
    },
    "retro": {
        "stage": "retro",
        "goals": [
            {"id": "RE1", "description": "Retro doc exists", "type": "min_lines", "target": "05-retro.md", "min": 15},
            {"id": "RE2", "description": "Lessons learned", "type": "content_match", "target": "05-retro.md", "pattern": "教训|lesson|学到|learned"},
        ],
    },
}

# Default harness-rules.yaml template
HARNESS_RULES_TEMPLATE = """\
version: '6.0.0'
project:
  slug: {slug}
  tech_stack: python
  language: zh-CN

runtime:
  test_cmd: 'pytest -q --tb=short'
  build_cmd: 'python -m py_compile **/*.py'
  lint_cmd: 'python -m flake8 --max-line-length=120'
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
  content_update:
    risk: low
    action: auto_verify

human_checkpoints:
  - ship  # only ship requires human approval by default

goals:
  research:
    - id: R1
      type: url_count
      target: '01-research.md'
      min: 5
    - id: R2
      type: content_match
      target: '01-research.md'
      pattern: '竞品|competitor'
  mvp:
    - id: M1
      type: command_pass
      command: 'pytest -q'
      workdir: '04-mvp'
    - id: M2
      type: file_exists
      target: '04-mvp/README.md'
"""


def extract_slug(project_root: Path) -> str:
    """Extract slug from project directory name (pm-{slug})."""
    name = project_root.name
    if name.startswith("pm-"):
        return name[3:]
    return name


def setup_harness_rules(project_root: Path, slug: str) -> dict:
    """Create harness-rules.yaml from template if not exists."""
    rules_path = project_root / "harness-rules.yaml"
    created = False

    if not rules_path.exists():
        content = HARNESS_RULES_TEMPLATE.format(slug=slug)
        rules_path.write_text(content, encoding="utf-8")
        created = True

    return {
        "path": str(rules_path),
        "created": created,
        "existed": not created,
    }


def setup_goals_directory(project_root: Path) -> dict:
    """Create goals/ directory with default goal YAML per stage."""
    goals_dir = project_root / "goals"
    goals_dir.mkdir(exist_ok=True)

    created_files = []
    for stage, goals_data in DEFAULT_GOALS.items():
        goal_file = goals_dir / f"{stage}.yaml"
        if not goal_file.exists():
            # Write YAML manually to avoid PyYAML dependency
            lines = [f"stage: {stage}", "goals:"]
            for goal in goals_data.get("goals", []):
                lines.append(f"  - id: {goal['id']}")
                lines.append(f"    description: '{goal.get('description', '')}'")
                lines.append(f"    type: {goal['type']}")
                if "target" in goal:
                    lines.append(f"    target: '{goal['target']}'")
                if "pattern" in goal:
                    lines.append(f"    pattern: '{goal['pattern']}'")
                if "min" in goal:
                    lines.append(f"    min: {goal['min']}")
                if "command" in goal:
                    lines.append(f"    command: '{goal['command']}'")
                if "workdir" in goal:
                    lines.append(f"    workdir: '{goal['workdir']}'")
                if "debates_dir" in goal:
                    lines.append(f"    debates_dir: '{goal['debates_dir']}'")
                if "stage_prefix" in goal:
                    lines.append(f"    stage_prefix: '{goal['stage_prefix']}'")
                if goal.get("optional"):
                    lines.append(f"    optional: true")
            lines.append("")
            goal_file.write_text("\n".join(lines), encoding="utf-8")
            created_files.append(str(goal_file))

    return {
        "goals_dir": str(goals_dir),
        "created_files": created_files,
        "total_stages": len(DEFAULT_GOALS),
    }


def setup_progress(project_root: Path, scripts_dir: Path) -> dict:
    """Initialize PROGRESS.md via progress-tracker.py."""
    progress_script = scripts_dir / "progress-tracker.py"
    if not progress_script.exists():
        return {"status": "skipped", "detail": "progress-tracker.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, str(progress_script),
             "--project-root", str(project_root), "init"],
            capture_output=True, text=True, timeout=30,
            cwd=str(scripts_dir),
        )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"status": "ok", "raw": result.stdout[:500]}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def render_body(template: str, context: dict) -> str:
    """Render task body template with context variables."""
    body = template.format(version=PIPELINE_VERSION)
    for key, value in context.items():
        body = body.replace("{{" + key + "}}", str(value))
    return body


def create_kanban_task(name: str, assignee: str, body: str, parent_id: str = "") -> dict:
    """Create a kanban task via hermes CLI."""
    cmd = ["hermes", "kanban", "create", name, "--assignee", assignee, "--body", body]
    if parent_id:
        cmd.extend(["--parent", parent_id])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
        )
        output = result.stdout.strip()

        # Try to extract task ID from output
        task_id = ""
        # Common patterns: "Created task: abc123" or "id: abc123" or just an ID
        import re
        id_match = re.search(r'(?:task[:\s]+|id[:\s]+)?([a-f0-9]{8,})', output, re.IGNORECASE)
        if id_match:
            task_id = id_match.group(1)
        elif output and len(output) <= 40:
            task_id = output.strip()

        return {
            "status": "ok" if result.returncode == 0 else "failed",
            "task_id": task_id,
            "name": name,
            "assignee": assignee,
            "exit_code": result.returncode,
            "output": output[:500],
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "detail": "hermes CLI not found. Install hermes-agent or use manual kanban create.",
            "name": name,
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e),
            "name": name,
        }


def ensure_brief(project_root: Path, title: str = "", description: str = "") -> dict:
    """Ensure 00-brief.md exists in project root."""
    brief_path = project_root / "00-brief.md"
    if brief_path.exists():
        return {"status": "exists", "path": str(brief_path)}

    # Create minimal brief
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    content = f"""\
# 产品想法

**创建时间**: {now}

## 标题
{title or 'Untitled'}

## 描述
{description or 'No description provided.'}

## 目标用户
（待补充）

## 核心问题
（待补充）

## 成功标准
（待补充）
"""
    brief_path.write_text(content, encoding="utf-8")
    return {"status": "created", "path": str(brief_path)}


def main():
    parser = argparse.ArgumentParser(
        description="Decompose product idea into kanban tasks (v6.0.0)"
    )
    parser.add_argument(
        "--project-root", required=True,
        help="Project root directory (pm-{slug})"
    )
    parser.add_argument(
        "--title", default="",
        help="Product idea title"
    )
    parser.add_argument(
        "--description", default="",
        help="Product idea description"
    )
    parser.add_argument(
        "--skip-harness", action="store_true",
        help="Skip harness-rules.yaml creation"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be created without actually creating"
    )
    parser.add_argument(
        "--scenario", default="greenfield",
        choices=["greenfield", "brownfield", "refine", "optimize"],
        help="Pipeline scenario (see scenarios.yaml)",
    )
    parser.add_argument(
        "--json", action="store_true", default=True,
        help="Output JSON (default)"
    )

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    scripts_dir = Path(__file__).resolve().parent
    slug = extract_slug(project_root)

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "project_root": str(project_root),
        "slug": slug,
        "stages": [],
        "setup": {},
        "errors": [],
    }

    # Ensure project root exists
    project_root.mkdir(parents=True, exist_ok=True)

    # Setup: harness-rules.yaml
    if not args.skip_harness:
        harness_result = setup_harness_rules(project_root, slug)
        report["setup"]["harness_rules"] = harness_result

    # Setup: goals/ directory
    goals_result = setup_goals_directory(project_root)
    report["setup"]["goals"] = goals_result

    # Setup: ensure brief exists
    brief_result = ensure_brief(project_root, args.title, args.description)
    report["setup"]["brief"] = brief_result

    # Setup: PROGRESS.md init
    if not args.dry_run:
        progress_result = setup_progress(project_root, scripts_dir)
        report["setup"]["progress"] = progress_result

    # Create kanban tasks
    task_ids = {}  # stage -> task_id mapping for parent linking

    # Load scenario filter
    stages_to_run = STAGES
    scenarios_path = resolve_skills_root() / "scenarios.yaml"
    if scenarios_path.exists():
        try:
            import yaml
            with scenarios_path.open(encoding="utf-8") as f:
                sc_cfg = yaml.safe_load(f) or {}
            skip = set(sc_cfg.get("scenarios", {}).get(args.scenario, {}).get("skip_stages", []))
            if skip:
                stages_to_run = [s for s in STAGES if s["stage"] not in skip and s.get("stage", "").split("-")[0] not in skip]
        except Exception:
            pass
    report["scenario"] = args.scenario

    for stage_def in stages_to_run:
        context = {
            "project_root": str(project_root),
            "scripts_dir": str(scripts_dir),
            "task_id": "{{task_id}}",  # Placeholder, filled after creation
            "slug": slug,
        }

        body = render_body(stage_def["body_template"], context)

        # Determine parent
        parent_id = ""
        if stage_def["parent_offset"] is not None:
            # Find parent task ID
            stage_idx = stages_to_run.index(stage_def)
            parent_idx = stage_idx + stage_def["parent_offset"]
            if 0 <= parent_idx < len(stages_to_run):
                parent_stage = stages_to_run[parent_idx]["stage"]
                parent_id = task_ids.get(parent_stage, "")

        stage_report = {
            "id": stage_def["id"],
            "name": stage_def["name"],
            "assignee": stage_def["assignee"],
            "stage": stage_def["stage"],
            "parent_id": parent_id,
        }

        if args.dry_run:
            stage_report["status"] = "dry_run"
            stage_report["body_preview"] = body[:200] + "..."
        else:
            create_result = create_kanban_task(
                stage_def["name"],
                stage_def["assignee"],
                body,
                parent_id,
            )
            stage_report.update(create_result)
            if create_result.get("task_id"):
                task_ids[stage_def["stage"]] = create_result["task_id"]

        report["stages"].append(stage_report)

    # Summary
    created_count = sum(1 for s in report["stages"] if s.get("status") == "ok")
    error_count = sum(1 for s in report["stages"] if s.get("status") in ("error", "failed"))
    report["summary"] = {
        "total_stages": len(STAGES),
        "created": created_count,
        "errors": error_count,
        "dry_run": args.dry_run,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if error_count == 0 else 1)


if __name__ == "__main__":
    main()
