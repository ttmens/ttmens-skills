#!/usr/bin/env python3
"""Drive MVP inner loop: Plan → Test → Observe → Adjust (max N iterations)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import importlib.util

PIPELINE_VERSION = "6.1.0"


def _load_harness_helpers():
    vg_path = Path(__file__).resolve().parent / "validate-gates.py"
    spec = importlib.util.spec_from_file_location("validate_gates", vg_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.load_harness_rules, mod.resolve_runtime_config


load_harness_rules, resolve_runtime_config = _load_harness_helpers()


def load_inner_state(project_root: Path) -> dict:
    ws = project_root / "docs" / "workflow_state.yaml"
    if not ws.exists():
        return {"current_iteration": 0, "max_iterations": 3, "last_signal": "unknown"}
    text = ws.read_text(encoding="utf-8", errors="replace")
    state = {"current_iteration": 0, "max_iterations": 3}
    for line in text.splitlines():
        if "current_iteration:" in line:
            state["current_iteration"] = int(line.split(":")[1].strip())
        if "max_iterations:" in line:
            state["max_iterations"] = int(line.split(":")[1].strip())
    return state


def save_inner_state(project_root: Path, iteration: int, signal: str, max_iter: int) -> None:
    ws = project_root / "docs" / "workflow_state.yaml"
    ws.parent.mkdir(parents=True, exist_ok=True)
    if ws.exists():
        text = ws.read_text(encoding="utf-8", errors="replace")
    else:
        text = "version: '6.0'\ncurrent_phase: mvp\ninner_loop_state:\n  current_iteration: 0\n  max_iterations: 3\n"
    lines = []
    in_inner = False
    for line in text.splitlines():
        if line.strip().startswith("inner_loop_state:"):
            in_inner = True
            lines.append(line)
            lines.append(f"  current_iteration: {iteration}")
            lines.append(f"  max_iterations: {max_iter}")
            lines.append(f"  last_signal: {signal}")
            lines.append(f"  updated_at: {datetime.now(timezone.utc).isoformat()}")
            continue
        if in_inner and line.startswith("  ") and ":" in line:
            continue
        if in_inner and line and not line.startswith(" "):
            in_inner = False
        if not in_inner:
            lines.append(line)
    if "inner_loop_state:" not in text:
        lines.extend([
            "inner_loop_state:",
            f"  current_iteration: {iteration}",
            f"  max_iterations: {max_iter}",
            f"  last_signal: {signal}",
        ])
    ws.write_text("\n".join(lines) + "\n", encoding="utf-8")


def observe(project_root: Path, harness: dict) -> dict:
    scripts_dir = Path(__file__).resolve().parent
    r = subprocess.run(
        [
            sys.executable,
            str(scripts_dir / "validate-gates.py"),
            "--stage", "mvp",
            "--run", str(project_root),
            "--runtime",
            "--goal",
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    try:
        report = json.loads(r.stdout) if r.stdout.strip() else {}
    except json.JSONDecodeError:
        report = {"raw": r.stdout[:500]}
    passed = r.returncode == 0
    return {"pass": passed, "exit_code": r.returncode, "report": report}


def main() -> int:
    parser = argparse.ArgumentParser(description="MVP inner loop driver")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--iteration", type=int, default=0, help="0 = auto increment")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    harness = load_harness_rules(project_root)
    inner = harness.get("inner_loop", {})
    max_iter = int(inner.get("max_iterations", 3))
    state = load_inner_state(project_root)
    iteration = args.iteration or (state["current_iteration"] + 1)

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "iteration": iteration,
        "max_iterations": max_iter,
        "action": "continue",
    }

    if iteration > max_iter:
        report["action"] = "escalate_human"
        report["reason"] = f"Exceeded max_iterations ({max_iter})"
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    if args.dry_run:
        report["action"] = "dry_run"
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    obs = observe(project_root, harness)
    report["observe"] = obs
    signal = "pass" if obs["pass"] else "fail"
    save_inner_state(project_root, iteration, signal, max_iter)

    if obs["pass"]:
        report["action"] = "exit_loop_g3"
    elif iteration >= max_iter:
        report["action"] = "escalate_human"
    else:
        report["action"] = "adjust_and_retry"

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if obs["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
