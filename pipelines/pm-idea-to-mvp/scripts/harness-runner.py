#!/usr/bin/env python3
"""Execute harness-rules.yaml decisions for a pipeline stage."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root

from pipeline_version import PIPELINE_VERSION


def load_harness(project_root: Path) -> dict:
    path = project_root / "harness-rules.yaml"
    if not path.exists():
        return {}
    try:
        import yaml

        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}


def run_decision(name: str, cfg: dict, project_root: Path, scripts_dir: Path) -> dict:
    action = cfg.get("action", "auto_verify")
    risk = cfg.get("risk", "medium")
    out = {"decision": name, "risk": risk, "action": action, "pass": True}

    if action == "human_checkpoint":
        out["pass"] = True
        out["requires_human"] = True
        out["block_reason"] = cfg.get("block_reason", f"Human checkpoint: {name}")
        return out

    verify = cfg.get("verify", "")
    if verify and "goal-check" in verify:
        stage = verify.split("--stage")[-1].split()[0].strip() if "--stage" in verify else ""
        if stage:
            r = subprocess.run(
                [sys.executable, str(scripts_dir / "goal-check.py"), "--stage", stage, "--project-root", str(project_root)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            out["pass"] = r.returncode == 0
            out["verify_exit"] = r.returncode
        return out

    if action == "write_adr_and_notify":
        adr_dir = project_root / "architecture" / "adr"
        out["pass"] = adr_dir.exists() or (project_root / "decisions.md").exists()
        out["detail"] = "ADR or decisions.md expected for medium-risk change"
        return out

    # auto_verify default
    return out


def apply_safe_improvements(project_root: Path, harness: dict) -> dict:
    """Merge low-risk lines from harness-improvements.md (Phase 6)."""
    imp = project_root / "harness-improvements.md"
    if not imp.exists():
        return {"applied": 0, "detail": "no harness-improvements.md"}
    text = imp.read_text(encoding="utf-8", errors="replace")
    applied = 0
    rules_path = project_root / "harness-rules.yaml"
    body = rules_path.read_text(encoding="utf-8") if rules_path.exists() else ""
    for line in text.splitlines():
        if line.strip().startswith("- [auto]") and ":" in line:
            patch = line.split("- [auto]", 1)[1].strip()
            if patch and patch not in body:
                body += f"\n# auto-applied from retro\n{patch}\n"
                applied += 1
    if applied:
        rules_path.write_text(body, encoding="utf-8")
    return {"applied": applied}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run harness decision rules")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--decision", default="", help="Named decision from harness-rules decisions:")
    parser.add_argument("--apply-safe", action="store_true", help="Apply low-risk harness patches from retro")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scripts_dir = Path(__file__).resolve().parent
    harness = load_harness(project_root)

    if args.apply_safe:
        print(json.dumps(apply_safe_improvements(project_root, harness), ensure_ascii=False, indent=2))
        return 0

    decisions = harness.get("decisions", {})
    report = {
        "pipeline_version": PIPELINE_VERSION,
        "stage": args.stage,
        "decisions": [],
        "human_checkpoints": harness.get("human_checkpoints", []),
        "needs_human": args.stage in (harness.get("human_checkpoints") or []),
    }

    if args.decision:
        cfg = decisions.get(args.decision, {})
        report["decisions"].append(run_decision(args.decision, cfg, project_root, scripts_dir))
    else:
        for name, cfg in decisions.items():
            if isinstance(cfg, dict):
                report["decisions"].append(run_decision(name, cfg, project_root, scripts_dir))

    report["all_passed"] = all(d.get("pass", False) for d in report["decisions"]) if report["decisions"] else True
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
