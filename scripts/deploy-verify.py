#!/usr/bin/env python3
"""Ship-stage deploy preflight: RUNBOOK structure + optional runtime."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PIPELINE_VERSION = "6.1.0"

REQUIRED_SECTIONS = [
    (r"部署|deploy", "deploy"),
    (r"回滚|rollback", "rollback"),
    (r"监控|monitor|健康|health", "monitoring"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--runtime", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    runbook = root / "RUNBOOK.md"
    checks = []

    if not runbook.exists():
        print(json.dumps({"error": "RUNBOOK.md missing", "all_passed": False}, ensure_ascii=False))
        return 1

    text = runbook.read_text(encoding="utf-8", errors="replace")
    for pattern, name in REQUIRED_SECTIONS:
        checks.append({"check": name, "pass": bool(re.search(pattern, text, re.I))})

    if args.runtime:
        scripts = Path(__file__).resolve().parent.parent / "pipelines" / "pm-idea-to-mvp" / "scripts"
        vg = scripts / "validate-gates.py"
        if vg.exists():
            r = subprocess.run(
                [sys.executable, str(vg), "--stage", "mvp", "--run", str(root), "--runtime"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            checks.append({"check": "mvp_runtime_regression", "pass": r.returncode == 0})

    bar = root / "production-bar.yaml"
    if bar.exists():
        checks.append({"check": "production_bar_defined", "pass": True})

    all_passed = all(c["pass"] for c in checks)
    print(json.dumps({"checks": checks, "all_passed": all_passed, "pipeline_version": PIPELINE_VERSION}, ensure_ascii=False, indent=2))
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
