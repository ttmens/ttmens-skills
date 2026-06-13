#!/usr/bin/env python3
"""Sync PROGRESS.md / stage status to Hermes Kanban comments."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PIPELINE_VERSION = "6.1.0"


def kanban_comment(task_id: str, message: str) -> dict:
    try:
        r = subprocess.run(
            ["hermes", "kanban", "comment", task_id, message],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "status": "ok" if r.returncode == 0 else "failed",
            "exit_code": r.returncode,
            "stdout": r.stdout[:300],
            "stderr": r.stderr[:300],
        }
    except FileNotFoundError:
        return {"status": "skipped", "detail": "hermes CLI not found", "command": f"hermes kanban comment {task_id} ..."}


def kanban_action(action: str, task_id: str, reason: str = "") -> dict:
    cmd = ["hermes", "kanban", action, task_id]
    if action == "block" and reason:
        cmd.extend(["--reason", reason])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {"action": action, "status": "ok" if r.returncode == 0 else "failed", "exit_code": r.returncode}
    except FileNotFoundError:
        return {"action": action, "status": "skipped", "detail": f"Run manually: {' '.join(cmd)}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Kanban sync helper")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--message", default="")
    parser.add_argument("--action", choices=["comment", "block", "complete"], default="comment")
    parser.add_argument("--reason", default="等待用户确认")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    progress = project_root / "PROGRESS.md"
    msg = args.message or (progress.read_text(encoding="utf-8")[:500] if progress.exists() else "stage update")

    if args.action == "comment":
        result = kanban_comment(args.task_id, msg)
    else:
        result = kanban_action(args.action, args.task_id, args.reason)

    print(json.dumps({"pipeline_version": PIPELINE_VERSION, **result}, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("ok", "skipped") else 1


if __name__ == "__main__":
    sys.exit(main())
