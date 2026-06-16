#!/usr/bin/env python3
"""Refine sprint decompose — 4 subtasks for existing pm-{slug}."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root

from pipeline_version import PIPELINE_VERSION

REFINE_STAGES = [
    ("Refine-1: 业界深研", "pm-researcher", "industry-benchmark → 01b-benchmark.md"),
    ("Refine-2: C4 差距", "pm-analyst", "c4-architecture gap vs 04-mvp"),
    ("Refine-3: 旅程/UX 复审", "pm-planner", "user-journey + ui-acceptance-review journey"),
    ("Refine-4: MVP 优化", "pm-builder", "inner-loop-driver + subagent-driven-development"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Decompose refine pipeline into kanban tasks")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--slug", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    scripts_dir = Path(__file__).resolve().parent
    slug = args.slug or root.name.replace("pm-", "")
    parent_name = f"Refine: {slug}"

    report = {"pipeline_version": PIPELINE_VERSION, "tasks": [], "parent": parent_name}

    if args.dry_run:
        for name, assignee, focus in REFINE_STAGES:
            report["tasks"].append({"name": name, "assignee": assignee, "focus": focus, "status": "dry_run"})
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    parent_id = ""
    try:
        r = subprocess.run(
            ["hermes", "kanban", "create", parent_name, "--assignee", "pm-orchestrator",
             "--body", f"Refine sprint for pm-{slug}"],
            capture_output=True, text=True, timeout=30,
        )
        if r.stdout.strip():
            parent_id = r.stdout.strip().split()[-1]
    except FileNotFoundError:
        report["error"] = "hermes CLI not found"
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    prev_id = parent_id
    for name, assignee, focus in REFINE_STAGES:
        body = f"Refine task. Project: {root}\nFocus: {focus}\nScripts: {scripts_dir}"
        cmd = ["hermes", "kanban", "create", name, "--assignee", assignee, "--body", body]
        if prev_id:
            cmd.extend(["--parent", prev_id])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        tid = r.stdout.strip().split()[-1] if r.stdout.strip() else ""
        report["tasks"].append({"name": name, "task_id": tid, "exit_code": r.returncode})
        prev_id = tid or prev_id

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
