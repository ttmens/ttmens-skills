#!/usr/bin/env python3
"""PM pipeline execution mode — auto HITL vs manual checkpoints."""

from __future__ import annotations

import os
from pathlib import Path

from pipeline_paths import resolve_hermes_home, resolve_pipeline_root

_TRUE = frozenset({"1", "true", "yes", "on"})


def _parse_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def load_trigger_routing() -> dict:
    path = resolve_pipeline_root() / "assets" / "trigger-routing.yaml"
    return _parse_yaml(path)


def load_execution_config() -> dict:
    routing = load_trigger_routing()
    execution = routing.get("execution") or {}
    if not isinstance(execution, dict):
        return {}
    return execution


def load_harness_rules(project_root: Path) -> dict:
    rules_path = project_root / "harness-rules.yaml"
    return _parse_yaml(rules_path)


def auto_hitl_enabled(project_root: Path | None = None) -> bool:
    """True → stages auto-complete after gates; no 确认 t_xxx loop."""
    env = os.environ.get("PM_AUTO_HITL", "").strip().lower()
    if env in _TRUE:
        return True
    if env in ("0", "false", "no", "off"):
        return False

    execution = load_execution_config()
    if "auto_hitl" in execution:
        return bool(execution.get("auto_hitl"))

    if project_root is not None:
        harness = load_harness_rules(project_root)
        if harness.get("auto_hitl") is True:
            return True
        checkpoints = harness.get("human_checkpoints")
        if checkpoints == []:
            return True

    # Default: lights-out (user /goal already expresses intent).
    return True


def human_checkpoint_stages(project_root: Path | None = None) -> list[str]:
    if auto_hitl_enabled(project_root):
        return []
    if project_root is not None:
        harness = load_harness_rules(project_root)
        checkpoints = harness.get("human_checkpoints")
        if isinstance(checkpoints, list):
            return [str(s).strip() for s in checkpoints if str(s).strip()]
    execution = load_execution_config()
    raw = execution.get("human_checkpoints")
    if isinstance(raw, list):
        return [str(s).strip() for s in raw if str(s).strip()]
    return ["align", "ship"]


def skip_grill_for_scenario(scenario: str) -> bool:
    execution = load_execution_config()
    skip = execution.get("skip_grill_scenarios") or []
    if isinstance(skip, list):
        return scenario in skip
    return scenario in ("import_repo", "brownfield", "optimize", "refine")


AUTO_ADVANCE_EXIT = """AUTO-ADVANCE (lights-out):
  Run stage-complete with --task-id <this_task_id> (add --runtime when required).
  If stage-complete exits 0 → kanban_complete immediately.
  Do NOT kanban_block for human approval unless stage-complete returns needs_human_checkpoint."""
