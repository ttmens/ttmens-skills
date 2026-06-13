#!/usr/bin/env python3
"""Deterministic PM pipeline v4 Refine decomposition (manual trigger)."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", r"D:\hermes-data"))
HERMES_AGENT = HERMES_HOME / "hermes-agent"
if str(HERMES_AGENT) not in sys.path:
    sys.path.insert(0, str(HERMES_AGENT))

from hermes_cli import kanban_db as kb  # noqa: E402

PROJECTS_ROOT = Path(rstr(Path(__file__).resolve().parents[4] / "projects"))
PIPELINE_ROOT = Path(rstr(Path(__file__).resolve().parent.parent))

CHECKPOINT_REFINE_UX = """HUMAN CHECKPOINT (two-phase):
  FIRST RUN (kanban_show has no unblock comment):
    stage-complete --stage spec --task-id <this_task_id> (journey+prototype gates) → kanban_block reason '等待用户确认 Refine 旅程与原型'
    Do NOT kanban_complete.
  RESUME (kanban_show has unblock comment, task ready):
    verify gates still pass → kanban_complete (optional stage-complete --skip-git)
    Do NOT kanban_block again."""


def project_dir(slug: str) -> Path:
    return PROJECTS_ROOT / f"pm-{slug.removeprefix('pm-')}"


def refine_task_body(stage: str, slug: str, reason: str, extra: str = "") -> str:
    proj = project_dir(slug).as_posix()
    base = f"""PM pipeline v4 Refine — stage: {stage}
Project directory: {proj}
Slug: {slug}
Reason: {reason}

MANDATORY before kanban_complete:
  python {PIPELINE_ROOT.as_posix()}/scripts/stage-complete.py --run {proj} --slug {slug.removeprefix('pm-')} --stage {stage} --message "refine({stage}): complete" --task-id <this_task_id>
"""
    if extra:
        base += f"\n{extra}\n"
    return base.strip()


def build_refine_children(slug: str, reason: str) -> list[dict]:
    s = slug.removeprefix("pm-")
    return [
        {
            "title": f"Refine-1 业界实现深研 — {s}",
            "assignee": "pm-researcher",
            "parents": [],
            "body": refine_task_body(
                "benchmark",
                s,
                reason,
                "Skill: industry-benchmark.\n"
                "Output: 01b-benchmark.md (≥3 implementation case studies vs current 04-mvp).\n"
                "Append actionable gaps to feedback.jsonl (stage: benchmark).",
            ),
        },
        {
            "title": f"Refine-2 架构差距+C4 — {s}",
            "assignee": "pm-analyst",
            "parents": [0],
            "body": refine_task_body(
                "analysis",
                s,
                reason,
                "Skills: c4-architecture, openspec.\n"
                "Outputs: architecture/c4-context.md, c4-container.md, c4-component.md; update openspec/design.md; new ADRs if needed.\n"
                "Runs analysis+architecture gates via stage-complete --stage analysis.",
            ),
        },
        {
            "title": f"Refine-3 旅程与 UX 复审 — {s}",
            "assignee": "pm-planner",
            "parents": [1],
            "body": refine_task_body(
                "spec",
                s,
                reason,
                "Skills: user-journey, sketch, open-design.\n"
                "Outputs: 03b-user-journey.md, update 03-prd.md gap section, refresh 02b-prototype/.\n"
                f"{CHECKPOINT_REFINE_UX}",
            ),
        },
        {
            "title": f"Refine-4 MVP 定向优化 — {s}",
            "assignee": "pm-builder",
            "parents": [2],
            "body": refine_task_body(
                "refine",
                s,
                reason,
                "Chain: plan → ui-ux-pro-max → design-review → ux-optimize → dogfood.\n"
                "Fix P0 from 01b-benchmark + UX-REVIEW. Write 06-refine-retro.md.\n"
                "stage-complete --stage refine aggregates benchmark+architecture+journey+mvp+ux-review+refine.",
            ),
        },
    ]


def refine_project(slug: str, reason: str, *, dry_run: bool = False) -> dict:
    resolved = slug.removeprefix("pm-")
    proj = project_dir(resolved)
    if not proj.exists():
        raise SystemExit(f"Project not found: {proj}")

    children = build_refine_children(resolved, reason)
    if dry_run:
        return {"slug": resolved, "project_dir": str(proj), "children": children}

    with kb.connect_closing() as conn:
        root_id = kb.create_task(
            conn,
            title=f"Refine 深化 — {resolved}",
            body=(
                f"PM pipeline v4 Refine sprint.\n"
                f"slug: {resolved}\n"
                f"project: {proj.as_posix()}\n"
                f"reason: {reason}\n"
                f"trigger: hermes kanban refine"
            ),
            assignee="pm-orchestrator",
            triage=True,
            created_by="decompose-refine-pipeline",
        )
        child_ids = kb.decompose_triage_task(
            conn,
            root_id,
            root_assignee="pm-orchestrator",
            children=children,
            author="decompose-refine-pipeline",
        )
        if not child_ids:
            raise SystemExit("decompose_triage_task failed")

        kb.add_comment(
            conn,
            root_id,
            "decompose-refine-pipeline",
            f"Refine v4 decomposed.\n"
            f"slug: {resolved}\n"
            f"reason: {reason}\n"
            f"children: {', '.join(child_ids)}",
        )

    return {
        "root_id": root_id,
        "slug": resolved,
        "project_dir": str(proj),
        "child_ids": child_ids,
        "reason": reason,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Decompose Refine sprint for an existing PM project")
    parser.add_argument("slug", help="Project slug (with or without pm- prefix)")
    parser.add_argument("--reason", default="实现不满意：需业界深研与优化")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = refine_project(args.slug, args.reason, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Refine root: {result.get('root_id', '(dry-run)')}")
        if result.get("child_ids"):
            for cid in result["child_ids"]:
                print(f"  child: {cid}")
        print(f"Project: {result['project_dir']}")


if __name__ == "__main__":
    main()
