#!/usr/bin/env python3
"""Handle phase transitions: backtrack (mvp→spec) and inner-loop retry."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_VERSION = "6.2.0"


def load_gates(project_root: Path) -> dict:
    p = project_root / "gates.json"
    if not p.exists():
        return {"version": PIPELINE_VERSION, "stages": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def save_gates(project_root: Path, data: dict) -> None:
    (project_root / "gates.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def update_workflow_phase(project_root: Path, phase: str, reason: str) -> None:
    ws = project_root / "docs" / "workflow_state.yaml"
    ws.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    if ws.exists():
        lines = ws.read_text(encoding="utf-8").splitlines()
        out = []
        for line in lines:
            if line.strip().startswith("current_phase:"):
                out.append(f"current_phase: {phase}")
            elif line.strip().startswith("backtrack_reason:"):
                continue
            else:
                out.append(line)
        if not any(l.strip().startswith("current_phase:") for l in out):
            out.insert(0, f"current_phase: {phase}")
        out.append(f"backtrack_reason: {reason}")
        out.append(f"backtrack_at: {now}")
        ws.write_text("\n".join(out) + "\n", encoding="utf-8")
    else:
        ws.write_text(
            f"version: '6.0'\ncurrent_phase: {phase}\nbacktrack_reason: {reason}\nbacktrack_at: {now}\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline phase transition")
    parser.add_argument("--project-root", required=True)
    parser.add_argument(
        "--condition",
        required=True,
        choices=["design_flaw_detected", "test_failure", "manual"],
    )
    parser.add_argument("--from-stage", default="mvp")
    parser.add_argument("--to-stage", default="")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    to_stage = args.to_stage
    if not to_stage:
        to_stage = "spec" if args.condition == "design_flaw_detected" else args.from_stage

    gates = load_gates(project_root)
    stages = gates.setdefault("stages", {})
    stages[args.from_stage] = {
        "status": "backtrack" if to_stage != args.from_stage else "retry",
        "condition": args.condition,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    stages[to_stage] = {"status": "pending", "reactivated": True}
    save_gates(project_root, gates)
    update_workflow_phase(project_root, to_stage, args.condition)

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "from": args.from_stage,
        "to": to_stage,
        "condition": args.condition,
        "gates_updated": True,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
