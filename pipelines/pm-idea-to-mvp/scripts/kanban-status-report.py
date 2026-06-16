#!/usr/bin/env python3
"""
kanban-status-report.py — Human-readable Kanban status for pm-idea-to-mvp (v6.1.0).

Usage:
  python kanban-status-report.py --slug product-knowledge
  python kanban-status-report.py --task-id t_abc123
  python kanban-status-report.py --slug product-knowledge --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from pipeline_version import PIPELINE_VERSION
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_paths import resolve_hermes_home, resolve_projects_root  # noqa: E402

PROJECTS_ROOT = resolve_projects_root()
HERMES_HOME = resolve_hermes_home()
HERMES_AGENT = HERMES_HOME / "hermes-agent"

if str(HERMES_AGENT) not in sys.path:
    sys.path.insert(0, str(HERMES_AGENT))

from hermes_cli import kanban_db as kb  # noqa: E402


def project_root_for_slug(slug: str) -> Path:
    s = slug.removeprefix("pm-")
    return PROJECTS_ROOT / f"pm-{s}"


def find_root_task_for_slug(conn, slug: str) -> str | None:
    s = slug.removeprefix("pm-")
    needle = f"pm-{s}"
    tasks = kb.list_tasks(conn, limit=500)
    for t in tasks:
        body = (t.body or "") + (t.title or "")
        if needle in body or s in (t.title or ""):
            if t.assignee == "pm-orchestrator" or "pm-pipeline" in (t.created_by or ""):
                return t.id
    return None


def summarize_tasks(conn, slug: str | None, root_id: str | None) -> dict:
    tasks = kb.list_tasks(conn, limit=500)
    relevant = []
    if root_id:
        root = kb.get_task(conn, root_id)
        if root:
            relevant.append(root)
            for t in tasks:
                if t.parent_id == root_id or (root_id in (t.body or "")):
                    relevant.append(t)
    elif slug:
        needle = slug.removeprefix("pm-")
        for t in tasks:
            blob = f"{t.title or ''}\n{t.body or ''}"
            if needle in blob or f"pm-{needle}" in blob:
                relevant.append(t)
    else:
        relevant = list(tasks[:50])

    by_status: dict[str, int] = {}
    active = []
    blocked = []
    for t in relevant:
        by_status[t.status] = by_status.get(t.status, 0) + 1
        if t.status in ("running", "ready", "todo"):
            active.append({"id": t.id, "title": t.title, "assignee": t.assignee, "status": t.status})
        if t.status == "blocked":
            blocked.append({"id": t.id, "title": t.title, "assignee": t.assignee})

    return {
        "pipeline_version": PIPELINE_VERSION,
        "slug": slug,
        "root_task_id": root_id,
        "counts": by_status,
        "active": active[:12],
        "blocked": blocked[:8],
        "total_matched": len(relevant),
    }


def format_text(report: dict) -> str:
    slug = report.get("slug") or "?"
    lines = [
        f"PM Kanban 状态 (v{PIPELINE_VERSION}) — pm-{slug.removeprefix('pm-')}",
        f"匹配任务: {report.get('total_matched', 0)}",
    ]
    counts = report.get("counts") or {}
    if counts:
        lines.append("状态: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    blocked = report.get("blocked") or []
    if blocked:
        lines.append("")
        lines.append("⏸ 等待 unblock:")
        for b in blocked:
            lines.append(f"  • {b['id']} [{b['assignee']}] {b['title'][:60]}")
            lines.append(f"    → 飞书回复: 确认 {b['id']}")
    active = report.get("active") or []
    if active:
        lines.append("")
        lines.append("▶ 进行中/待执行:")
        for a in active[:6]:
            lines.append(f"  • {a['status']} {a['id']} [{a['assignee']}] {a['title'][:60]}")
    if not blocked and not active:
        lines.append("")
        lines.append("（无 active/blocked 子任务 — 可能已完成或未启动 decompose）")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Kanban status report for pm-idea-to-mvp")
    parser.add_argument("--slug", default="")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--feishu-notify", action="store_true", help="Push alert to Feishu when blocked/ready thresholds exceeded")
    args = parser.parse_args()

    slug = args.slug.removeprefix("pm-") if args.slug else ""
    proj = None
    with kb.connect_closing() as conn:
        root_id = args.task_id or None
        if not root_id and slug:
            root_id = find_root_task_for_slug(conn, slug)
        report = summarize_tasks(conn, slug or None, root_id)
        proj = project_root_for_slug(slug) if slug else None
        if proj:
            report["project_root"] = str(proj)
            report["project_exists"] = proj.exists()

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        text = format_text(report)
        print(text)

    if args.feishu_notify:
        blocked = report.get("blocked") or []
        ready_count = (report.get("counts") or {}).get("ready", 0)
        if blocked or ready_count > 5:
            skills_root = HERMES_HOME / "skills"
            notify = skills_root / "scripts" / "feishu_notify.py"
            if notify.exists():
                import subprocess

                extra = text if not args.json else format_text(report)
                subprocess.run(
                    [
                        sys.executable,
                        str(notify),
                        "--stage", "kanban",
                        "--status", "ALERT",
                        "--project-root", str(proj or PROJECTS_ROOT),
                        "--extra", extra[:1500],
                    ],
                    timeout=30,
                )


if __name__ == "__main__":
    main()
