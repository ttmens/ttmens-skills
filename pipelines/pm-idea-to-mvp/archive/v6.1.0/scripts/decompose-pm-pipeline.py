#!/usr/bin/env python3
"""
decompose-pm-pipeline.py — Decompose a product idea into kanban tasks (v6.0.0).

Dual mode:
  --task-id <triage_id>   Hermes gateway (kanban_db.decompose_triage_task)
  --project-root <path>   Standalone CLI (hermes kanban create subprocess)

Creates outer-loop stages + MVP inner loop (Plan + iter1-3).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_paths import resolve_pipeline_root  # noqa: E402

PIPELINE_VERSION = "6.0.0"
PROJECTS_ROOT = Path(r"D:/workspace/projects")
PIPELINE_ROOT = resolve_pipeline_root()

HERMES_HOME = Path(os.environ.get("HERMES_HOME", r"D:\hermes-data"))
HERMES_AGENT = HERMES_HOME / "hermes-agent"
if str(HERMES_AGENT) not in sys.path:
    sys.path.insert(0, str(HERMES_AGENT))

from hermes_cli import kanban_db as kb  # noqa: E402

DEFAULT_HUMAN_CHECKPOINTS = ["align", "spec", "ship"]

CHECKPOINT_ALIGN = """HUMAN CHECKPOINT (two-phase):
  FIRST RUN: stage-complete --stage align --project-root <proj> --task-id <id> --runtime
    → kanban_block reason '等待用户确认 align 产物'. Do NOT kanban_complete.
  RESUME: verify gates → kanban_complete. Do NOT kanban_block again."""

CHECKPOINT_SPEC = """HUMAN CHECKPOINT (two-phase):
  FIRST RUN: stage-complete --stage spec --project-root <proj> --task-id <id> --runtime
    → kanban_block reason '等待用户确认 PRD/原型范围'. Do NOT kanban_complete.
  RESUME: verify gates → kanban_complete."""

CHECKPOINT_SHIP = """HUMAN CHECKPOINT (two-phase, G3):
  FIRST RUN: stage-complete --stage ship --project-root <proj> --task-id <id> --runtime
    → kanban_block reason '等待用户确认部署范围'. Do NOT kanban_complete.
  RESUME: verify gates → kanban_complete."""

HARNESS_RULES_TEMPLATE = """\
version: '6.0.0'
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
  - spec
  - ship

inner_loop:
  max_iterations: 3
  test_command: '{test_cmd}'
"""


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:48] or "idea"


def extract_slug_from_text(title: str, body: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit.strip().removeprefix("pm-")
    combined = f"{title}\n{body}"
    for pat in (r"projects/pm-([\w-]+)", r"slug[:\s]+([\w-]+)", r"pm-([\w-]+)"):
        m = re.search(pat, combined, re.I)
        if m:
            return m.group(1).removeprefix("pm-")
    if any(k in combined for k in ("产品知识库", "产品知识平台", "知识平台")):
        return "product-knowledge"
    if "yuxi" in combined.lower():
        return "product-knowledge-yuxi"
    return slugify(title)


def extract_slug_from_path(project_root: Path) -> str:
    name = project_root.name
    return name[3:] if name.startswith("pm-") else name


def project_dir(slug: str) -> Path:
    return PROJECTS_ROOT / f"pm-{slug}"


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
    created = False
    if not rules_path.exists():
        test_cmd = detect_test_cmd(project_root)
        rules_path.write_text(
            HARNESS_RULES_TEMPLATE.format(slug=slug, test_cmd=test_cmd),
            encoding="utf-8",
        )
        created = True
    return {"path": str(rules_path), "created": created}


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
    script = PIPELINE_ROOT / "scripts" / "publish_repo.py"
    if not script.exists():
        return None
    proc = subprocess.run(
        [sys.executable, str(script), "--dir", str(proj), "--slug", slug, "--description", title[:200]],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode == 0:
        return None
    return (proc.stderr or proc.stdout or "unknown")[:500]


def write_run_manifest(proj: Path, slug: str, title: str, child_titles: list[str]) -> None:
    stages = "\n".join(f"- [ ] {t}" for t in child_titles)
    content = f"""# 本次运行说明 (v6.0)

| 项 | 值 |
|----|-----|
| 标题 | {title} |
| Slug | `{slug}` |
| 目录 | `{proj.as_posix()}` |
| Pages | https://ttmens.github.io/pm-{slug}/ |

## 阶段清单（含 MVP 内循环）

{stages}

## 人工检查点

1. **align** — 确认 CONTEXT 后 unblock
2. **spec** — 确认 PRD/原型后 unblock
3. **ship** — 确认部署范围后 unblock

Harness: `harness-rules.yaml` | Progress: `PROGRESS.md`
"""
    (proj / "RUN.md").write_text(content, encoding="utf-8")


def task_body(stage: str, slug: str, title: str, extra: str = "") -> str:
    proj = project_dir(slug).as_posix()
    scripts = (PIPELINE_ROOT / "scripts").as_posix()
    base = f"""PM pipeline v{PIPELINE_VERSION} — stage: {stage}
Project root: {proj}
Slug: {slug}
Parent idea: {title}

MANDATORY before kanban_complete:
  python {scripts}/stage-complete.py --project-root {proj} --stage {stage} --task-id <this_task_id>

All artifacts under {proj}/. See harness-rules.yaml + PROGRESS.md.
"""
    if extra:
        base += f"\n{extra}\n"
    return base.strip()


def build_children(slug: str, title: str) -> list[dict]:
    """Flat kanban children: outer loop + MVP inner loop (plan + 3 iterations)."""
    proj = project_dir(slug).as_posix()
    return [
        {
            "title": f"Grill 对齐想法 — {slug}",
            "assignee": "pm-aligner",
            "parents": [],
            "body": task_body(
                "align", slug, title,
                "Skills: grill-me / grill-with-docs.\n"
                "Outputs: CONTEXT.md, decisions.md.\n" + CHECKPOINT_ALIGN,
            ),
        },
        {
            "title": f"深度调研 — {slug}",
            "assignee": "pm-researcher",
            "parents": [0],
            "body": task_body("research", slug, title, "Output: 01-research.md (≥5 URLs)."),
        },
        {
            "title": f"方案论证 — {slug}",
            "assignee": "pm-analyst",
            "parents": [1],
            "body": task_body(
                "analysis", slug, title,
                "Outputs: 02-analysis.md, architecture/c4-*.md, openspec/proposal.md.",
            ),
        },
        {
            "title": f"原型+PRD+OpenSpec — {slug}",
            "assignee": "pm-planner",
            "parents": [2],
            "body": task_body(
                "spec", slug, title,
                "Outputs: 03b-user-journey.md, 02b-prototype/, 03-prd.md, openspec/tasks.md.\n"
                + CHECKPOINT_SPEC,
            ),
        },
        {
            "title": f"MVP Plan — {slug}",
            "assignee": "pm-builder",
            "parents": [3],
            "body": task_body(
                "mvp-plan", slug, title,
                "Inner loop step 1: read openspec/tasks.md + 03b-user-journey.md.\n"
                "Run writing-plans; produce 04-mvp/DESIGN.md via ui-ux-pro-max.\n"
                "Update PROGRESS.md task plan. No full implementation yet.",
            ),
        },
        {
            "title": f"MVP Code+Test iter 1 — {slug}",
            "assignee": "pm-builder",
            "parents": [4],
            "body": task_body(
                "mvp-iter1", slug, title,
                f"Inner loop iter 1: implement per openspec/tasks.md in {proj}/04-mvp.\n"
                "Chain: TDD → opencode → ui-acceptance-review (journey) → dogfood.\n"
                "Run stage-complete --stage mvp --runtime --verify-goals on pass.\n"
                "If tests fail: fix in-place; iter2 continues if still failing after complete.",
            ),
        },
        {
            "title": f"MVP Code+Test iter 2 — {slug}",
            "assignee": "pm-builder",
            "parents": [5],
            "body": task_body(
                "mvp-iter2", slug, title,
                "Inner loop iter 2 (only if iter1 left failing tests/UX P0).\n"
                "Focus fixes; re-run tests. stage-complete --stage mvp --runtime on pass.",
            ),
        },
        {
            "title": f"MVP Code+Test iter 3 — {slug}",
            "assignee": "pm-builder",
            "parents": [6],
            "body": task_body(
                "mvp-iter3", slug, title,
                "Inner loop iter 3 (final). If still failing: kanban_block + harness-improvements.md.\n"
                "stage-complete --stage mvp --runtime --verify-goals before ship.",
            ),
        },
        {
            "title": f"Ship 部署 — {slug}",
            "assignee": "pm-shipper",
            "parents": [7],
            "body": task_body(
                "ship", slug, title,
                "Outputs: RUNBOOK.md, docs/ui-acceptance-report.md.\n"
                "Skills: ui-acceptance-review (full), kw-deploy-checklist.\n" + CHECKPOINT_SHIP,
            ),
        },
        {
            "title": f"Operate 运维 — {slug}",
            "assignee": "pm-operator",
            "parents": [8],
            "body": task_body("operate", slug, title, "Output: 07-ops-notes.md (on-call, monitoring, rollback)."),
        },
        {
            "title": f"Grow 增长 — {slug}",
            "assignee": "pm-growth",
            "parents": [9],
            "body": task_body("grow", slug, title, "Output: 06-growth.md (NSM + GTM)."),
        },
        {
            "title": f"Retro+进化 — {slug}",
            "assignee": "pm-builder",
            "parents": [10],
            "body": task_body(
                "retro", slug, title,
                "Output: 05-retro.md, harness-improvements.md, evolution-notes.md.",
            ),
        },
    ]


def setup_project(project_root: Path, slug: str, title: str, body: str) -> dict:
    project_root.mkdir(parents=True, exist_ok=True)
    return {
        "harness": setup_harness_rules(project_root, slug),
        "goals": setup_goals_directory(project_root),
        "brief": ensure_brief(project_root, title, body),
        "progress": setup_progress(project_root),
    }


def decompose_gateway(task_id: str, slug: str | None, dry_run: bool = False) -> dict:
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
        children = build_children(resolved_slug, title)

        if dry_run:
            return {
                "task_id": task_id,
                "slug": resolved_slug,
                "project_dir": str(proj),
                "child_count": len(children),
                "children": [{"title": c["title"], "assignee": c["assignee"]} for c in children],
            }

        setup = setup_project(proj, resolved_slug, title, body)
        publish_err = publish_project_repo(proj, resolved_slug, title)
        child_titles = [c["title"] for c in children]
        write_run_manifest(proj, resolved_slug, title, child_titles)

        child_ids = kb.decompose_triage_task(
            conn, task_id,
            root_assignee="pm-orchestrator",
            children=children,
            author="decompose-pm-pipeline-v6",
        )
        if not child_ids:
            raise SystemExit("decompose_triage_task failed")

        pages = f"https://ttmens.github.io/pm-{resolved_slug}/"
        repo = f"https://github.com/ttmens/pm-{resolved_slug}"
        kb.add_comment(
            conn, task_id, "decompose-pm-pipeline",
            f"pm-pipeline v{PIPELINE_VERSION} decomposed ({len(child_ids)} tasks, inner loop).\n"
            f"slug: {resolved_slug}\nproject: {proj.as_posix()}\n"
            f"repo: {repo}\npages: {pages}\n"
            f"harness: initialized\nchildren: {', '.join(child_ids)}",
        )

    return {
        "task_id": task_id,
        "slug": resolved_slug,
        "project_dir": str(proj),
        "child_ids": child_ids,
        "child_count": len(child_ids),
        "pipeline_version": PIPELINE_VERSION,
        "setup": setup,
        "publish_error": publish_err,
        "assignees": [c["assignee"] for c in children],
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


def decompose_cli(project_root: Path, title: str, description: str, dry_run: bool) -> dict:
    slug = extract_slug_from_path(project_root)
    children = build_children(slug, title or f"Idea: {slug}")
    setup = setup_project(project_root, slug, title, description)
    write_run_manifest(project_root, slug, title, [c["title"] for c in children])

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
        "mode": "cli",
        "slug": slug,
        "project_dir": str(project_root),
        "child_ids": child_ids,
        "child_count": len(child_ids),
        "pipeline_version": PIPELINE_VERSION,
        "setup": setup,
        "stages": stages_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=f"PM pipeline decompose v{PIPELINE_VERSION}")
    parser.add_argument("--task-id", default=None, help="Gateway mode: triage task ID")
    parser.add_argument("--slug", default=None, help="Override slug (no pm- prefix)")
    parser.add_argument("--project-root", default=None, help="CLI mode: project directory")
    parser.add_argument("--title", default="", help="Idea title (CLI mode)")
    parser.add_argument("--description", default="", help="Idea description (CLI mode)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    os.environ.setdefault("HERMES_HOME", str(HERMES_HOME))

    if args.task_id:
        result = decompose_gateway(args.task_id, args.slug, dry_run=args.dry_run)
    elif args.project_root:
        result = decompose_cli(
            Path(args.project_root).resolve(),
            args.title,
            args.description,
            args.dry_run,
        )
    else:
        parser.error("Provide --task-id (gateway) or --project-root (CLI)")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
