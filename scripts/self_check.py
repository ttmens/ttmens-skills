#!/usr/bin/env python3
"""Subagent quality self-check before task complete."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PIPELINE_VERSION = "7.1.0"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--workdir", default="04-mvp")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    wd = root / args.workdir
    checks = []

    if (wd / "README.md").exists():
        checks.append({"check": "readme", "pass": True})
    else:
        checks.append({"check": "readme", "pass": False})

    r = subprocess.run(
        "python -m compileall -q . 2>nul || python -m compileall -q .",
        shell=True,
        cwd=str(wd) if wd.exists() else str(root),
        capture_output=True,
        text=True,
        timeout=60,
    )
    checks.append({"check": "compileall", "pass": r.returncode == 0})

    skills_root = Path(__file__).resolve().parent.parent
    ua = skills_root / "scripts" / "ui_acceptance.py"
    if ua.exists() and wd.exists():
        r2 = subprocess.run(
            [sys.executable, str(ua), "--project-root", str(root), "--quick"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        checks.append({"check": "ui_acceptance_quick", "pass": r2.returncode == 0})

    passed = all(c["pass"] for c in checks)
    print(json.dumps({"checks": checks, "all_passed": passed, "pipeline_version": PIPELINE_VERSION}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
