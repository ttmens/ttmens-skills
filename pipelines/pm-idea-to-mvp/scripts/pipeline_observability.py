#!/usr/bin/env python3
"""Pipeline observability — Kanban alert + optional skills sync (for Hermes cron)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_paths import resolve_hermes_home, resolve_skills_root  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", default="", help="Optional project slug for focused report")
    parser.add_argument("--sync-skills", action="store_true", help="Run ttmens-skills-sync API zip fallback")
    args = parser.parse_args()

    report_script = SCRIPT_DIR / "kanban-status-report.py"
    cmd = [sys.executable, str(report_script), "--feishu-notify"]
    if args.slug:
        cmd.extend(["--slug", args.slug.removeprefix("pm-")])
    subprocess.run(cmd, timeout=120)

    if args.sync_skills:
        sync_skill = resolve_skills_root().parent / "scripts" / "ttmens-skills-sync"
        # fallback: run validate only
        validate = resolve_skills_root() / "scripts" / "validate_skills.py"
        if validate.exists():
            subprocess.run([sys.executable, str(validate)], cwd=str(validate.parent.parent), timeout=120)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
