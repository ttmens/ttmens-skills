#!/usr/bin/env python3
"""
progress-tracker.py — Manage PROGRESS.md for pipeline task tracking.

Subcommands:
  init    — Create PROGRESS.md from openspec/tasks.md
  update  — Update task status (--task <id> --status <status> [--note <note>])
  show    — Display current progress summary
  resume  — Output last incomplete task for agent to continue from

Status markers:
  - [x] done ✅
  - [ ] pending ⏳
  - [~] in-progress 🔄
  - [!] blocked ❌
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root

PIPELINE_VERSION = "6.2.0"

STATUS_MARKERS = {
    "done": ("x", "✅"),
    "pending": (" ", "⏳"),
    "in-progress": ("~", "🔄"),
    "blocked": ("!", "❌"),
}

# Reverse lookup: marker char -> status
MARKER_TO_STATUS = {v[0]: k for k, v in STATUS_MARKERS.items()}


def parse_tasks_from_openspec(tasks_file: Path) -> list[dict]:
    """
    Parse tasks from openspec/tasks.md.
    Expected format: markdown with task entries like:
      - [ ] Task 1: Description
      - [ ] Task 2: Description
    Or numbered lists / headings.
    """
    if not tasks_file.exists():
        return []

    content = tasks_file.read_text(encoding="utf-8")
    tasks = []
    task_num = 0

    for line in content.splitlines():
        stripped = line.strip()
        # Match checkbox lines: - [ ] Task N: Description
        match = re.match(r'^-\s*\[([ x~!])\]\s*(.+)$', stripped)
        if match:
            task_num += 1
            marker = match.group(1)
            desc = match.group(2).strip()
            status = MARKER_TO_STATUS.get(marker, "pending")
            tasks.append({
                "id": task_num,
                "description": desc,
                "status": status,
                "note": ""
            })
            continue

        # Match numbered items: 1. Task description
        match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
        if match and not stripped.startswith("-"):
            task_num += 1
            desc = match.group(2).strip()
            tasks.append({
                "id": task_num,
                "description": desc,
                "status": "pending",
                "note": ""
            })
            continue

        # Match headings as task separators: ## Task N: ...
        match = re.match(r'^#{1,3}\s+(?:Task\s+)?(\d+)[:\.\s]+(.+)$', stripped)
        if match:
            task_num += 1
            desc = match.group(2).strip()
            tasks.append({
                "id": task_num,
                "description": desc,
                "status": "pending",
                "note": ""
            })

    return tasks


def generate_progress_md(tasks: list[dict], title: str = "MVP Progress") -> str:
    """Generate PROGRESS.md content from task list."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# {title}",
        f"Last updated: {now}",
        "",
        "## Tasks",
    ]

    for task in tasks:
        marker, emoji = STATUS_MARKERS.get(task["status"], (" ", "⏳"))
        desc = task["description"]
        note_part = ""
        if task.get("note"):
            note_part = f" ({task['note']})"
        lines.append(f"- [{marker}] Task {task['id']}: {desc} {emoji}{note_part}")

    lines.append("")
    return "\n".join(lines)


def parse_progress_md(content: str) -> list[dict]:
    """Parse PROGRESS.md back into task list."""
    tasks = []
    for line in content.splitlines():
        stripped = line.strip()
        match = re.match(r'^-\s*\[([ x~!])\]\s*Task\s+(\d+)[:\.\s]+(.+)$', stripped)
        if match:
            marker = match.group(1)
            task_id = int(match.group(2))
            rest = match.group(3).strip()

            # Extract note from parentheses at end
            note = ""
            note_match = re.search(r'\(([^)]+)\)\s*$', rest)
            if note_match:
                note = note_match.group(1)
                rest = rest[:note_match.start()].strip()

            # Remove emoji from description
            desc = re.sub(r'\s*[✅⏳🔄❌]\s*$', '', rest).strip()

            status = MARKER_TO_STATUS.get(marker, "pending")
            tasks.append({
                "id": task_id,
                "description": desc,
                "status": status,
                "note": note
            })
    return tasks


def cmd_init(args):
    """Create PROGRESS.md from openspec/tasks.md."""
    project_root = Path(args.project_root).resolve()
    tasks_file = project_root / "openspec" / "tasks.md"
    progress_file = project_root / "PROGRESS.md"

    if progress_file.exists() and not args.force:
        result = {
            "action": "init",
            "status": "skipped",
            "detail": f"PROGRESS.md already exists (use --force to overwrite)",
            "path": str(progress_file)
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    tasks = parse_tasks_from_openspec(tasks_file)

    if not tasks:
        # Create a minimal progress file even without tasks
        tasks = [{"id": 1, "description": "No tasks found in openspec/tasks.md", "status": "pending", "note": ""}]

    content = generate_progress_md(tasks)
    progress_file.write_text(content, encoding="utf-8")

    result = {
        "action": "init",
        "status": "ok",
        "path": str(progress_file),
        "tasks_count": len(tasks),
        "tasks": [{"id": t["id"], "description": t["description"]} for t in tasks]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_update(args):
    """Update a task's status in PROGRESS.md."""
    project_root = Path(args.project_root).resolve()
    progress_file = project_root / "PROGRESS.md"

    if not progress_file.exists():
        result = {
            "action": "update",
            "status": "error",
            "detail": "PROGRESS.md not found. Run 'init' first."
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    content = progress_file.read_text(encoding="utf-8")
    tasks = parse_progress_md(content)

    # Find task by ID
    target_task = None
    for task in tasks:
        if task["id"] == args.task:
            target_task = task
            break

    if not target_task:
        result = {
            "action": "update",
            "status": "error",
            "detail": f"Task {args.task} not found in PROGRESS.md",
            "available_tasks": [t["id"] for t in tasks]
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    # Validate status
    if args.status not in STATUS_MARKERS:
        result = {
            "action": "update",
            "status": "error",
            "detail": f"Invalid status '{args.status}'. Valid: {list(STATUS_MARKERS.keys())}"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    # Update task
    old_status = target_task["status"]
    target_task["status"] = args.status
    if args.note:
        target_task["note"] = args.note

    # Regenerate file
    new_content = generate_progress_md(tasks)
    progress_file.write_text(new_content, encoding="utf-8")

    result = {
        "action": "update",
        "status": "ok",
        "task_id": args.task,
        "old_status": old_status,
        "new_status": args.status,
        "note": args.note or ""
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_show(args):
    """Display current progress summary."""
    project_root = Path(args.project_root).resolve()
    progress_file = project_root / "PROGRESS.md"

    if not progress_file.exists():
        result = {
            "action": "show",
            "status": "error",
            "detail": "PROGRESS.md not found"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    content = progress_file.read_text(encoding="utf-8")
    tasks = parse_progress_md(content)

    # Compute summary
    counts = {"done": 0, "pending": 0, "in-progress": 0, "blocked": 0}
    for task in tasks:
        counts[task["status"]] = counts.get(task["status"], 0) + 1

    total = len(tasks)
    done = counts["done"]
    pct = round(done / total * 100, 1) if total > 0 else 0

    result = {
        "action": "show",
        "status": "ok",
        "path": str(progress_file),
        "total": total,
        "done": done,
        "pending": counts["pending"],
        "in_progress": counts["in-progress"],
        "blocked": counts["blocked"],
        "percent_complete": pct,
        "tasks": tasks
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_resume(args):
    """Output the last incomplete task for agent to continue from."""
    project_root = Path(args.project_root).resolve()
    progress_file = project_root / "PROGRESS.md"

    if not progress_file.exists():
        result = {
            "action": "resume",
            "status": "error",
            "detail": "PROGRESS.md not found"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    content = progress_file.read_text(encoding="utf-8")
    tasks = parse_progress_md(content)

    # Find first non-done task (in-progress takes priority, then blocked, then pending)
    resume_task = None
    # Priority: in-progress > blocked > pending
    for priority_status in ("in-progress", "blocked", "pending"):
        for task in tasks:
            if task["status"] == priority_status:
                resume_task = task
                break
        if resume_task:
            break

    if not resume_task:
        result = {
            "action": "resume",
            "status": "complete",
            "detail": "All tasks are done",
            "task": None
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    result = {
        "action": "resume",
        "status": "ok",
        "task": resume_task,
        "message": f"Resume from Task {resume_task['id']}: {resume_task['description']}"
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Manage PROGRESS.md for pipeline task tracking"
    )
    parser.add_argument(
        "--project-root", required=True,
        help="Project root directory (pm-{slug} repo)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # init
    init_parser = subparsers.add_parser("init", help="Create PROGRESS.md from openspec/tasks.md")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing PROGRESS.md")

    # update
    update_parser = subparsers.add_parser("update", help="Update task status")
    update_parser.add_argument("--task", type=int, required=True, help="Task ID")
    update_parser.add_argument(
        "--status", required=True,
        choices=list(STATUS_MARKERS.keys()),
        help="New status"
    )
    update_parser.add_argument("--note", default="", help="Optional note")

    # show
    subparsers.add_parser("show", help="Display progress summary")

    # resume
    subparsers.add_parser("resume", help="Output last incomplete task")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init": cmd_init,
        "update": cmd_update,
        "show": cmd_show,
        "resume": cmd_resume,
    }

    exit_code = commands[args.command](args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
