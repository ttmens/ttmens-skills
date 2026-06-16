#!/usr/bin/env python3
"""E2E smoke checks for pm-idea-to-mvp v7.2 infra."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_paths import resolve_hermes_home, resolve_projects_root, resolve_skills_root  # noqa: E402

SKILLS = resolve_skills_root()
HERMES_HOME = resolve_hermes_home()
PIPELINE_SCRIPTS = SKILLS / "pipelines/pm-idea-to-mvp/scripts"
PROJECTS = resolve_projects_root()
VENV = HERMES_HOME / "hermes-agent" / "venv" / "Scripts" / "python.exe"
PY = str(VENV) if VENV.exists() else sys.executable
HERMES_AGENT = HERMES_HOME / "hermes-agent"


def run(cmd: list[str], cwd: Path | None = None) -> dict:
    r = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        cwd=str(cwd) if cwd else None, encoding="utf-8", errors="replace",
    )
    return {"cmd": cmd, "ok": r.returncode == 0, "code": r.returncode, "out": (r.stdout or "")[:400]}


def check_pipeline_notify_message() -> dict:
    test_root = PROJECTS / "pm-test-dry"
    if not test_root.exists():
        test_root = PROJECTS / "pm-product-knowledge"
    if not test_root.exists():
        return {"check": "pipeline_notify_message", "ok": False, "missing": ["project_root"], "preview_head": ""}
    cmd = [
        PY,
        str(SKILLS / "scripts/feishu_notify.py"),
        "--stage", "align",
        "--status", "PASS",
        "--project-root", str(test_root),
        "--task-id", "t_smoke1234",
        "--human-checkpoint",
        "--dry-run",
    ]
    r = subprocess.run(
        cmd, capture_output=True, text=True, timeout=60,
        encoding="utf-8", errors="replace",
    )
    ok = r.returncode == 0
    preview = ""
    stdout = r.stdout or ""
    if stdout.strip():
        try:
            data = json.loads(stdout)
            preview = data.get("message_preview", "")
        except json.JSONDecodeError:
            preview = stdout[:400]
    required = ("本阶段产物", "Pages", "Repo", "本地", "确认 t_smoke1234")
    missing = [k for k in required if k not in preview]
    return {
        "check": "pipeline_notify_message",
        "ok": ok and not missing,
        "missing": missing,
        "preview_head": preview[:200],
    }


def check_kanban_notify_bridge() -> dict:
    if not HERMES_AGENT.exists():
        return {"check": "kanban_notify_bridge", "ok": True, "skipped": "hermes-agent not found"}
    agent_path = str(HERMES_AGENT).replace("\\", "\\\\")
    cmd = [
        PY,
        "-c",
        f"import sys; sys.path.insert(0, r'{agent_path}'); "
        "from hermes_cli import pm_pipeline; "
        "m=pm_pipeline.build_kanban_notify_message('blocked','t_abcd','Grill 对齐 — test-dry',"
        "body='Project root: D:/workspace/projects/pm-test-dry\\nstage: align',"
        "reason='human checkpoint'); "
        "assert 'Pages' in m and '确认 t_abcd' in m",
    ]
    return run(cmd)


def check_feishu_cards() -> dict:
    if not HERMES_AGENT.exists():
        return {"check": "feishu_pipeline_cards", "ok": True, "skipped": "hermes-agent not found"}
    agent_path = str(HERMES_AGENT).replace("\\", "\\\\")
    return run([
        PY, "-c",
        f"import sys; sys.path.insert(0, r'{agent_path}'); "
        "from hermes_cli.feishu_pipeline_cards import parse_checkpoint_confirm; "
        "assert parse_checkpoint_confirm('确认 t_abcd1234')",
    ])


def main() -> int:
    checks = []
    checks.append(run([PY, str(SKILLS / "scripts" / "validate_skills.py")]))
    checks.append(check_feishu_cards())
    decompose = SKILLS / "pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py"
    checks.append(run([PY, str(decompose), "--help"]))
    notify = SKILLS / "scripts/feishu_notify.py"
    checks.append({"check": "feishu_notify_exists", "ok": notify.exists()})
    checks.append(check_pipeline_notify_message())
    checks.append(check_kanban_notify_bridge())
    checks.append(run([
        PY, "-c",
        f"import sys; sys.path.insert(0, r'{PIPELINE_SCRIPTS}'); "
        "from pipeline_notify import artifact_tab_id; "
        "assert artifact_tab_id('CONTEXT.md')=='CONTEXT-md'",
    ]))
    report = {"checks": checks, "all_ok": all(c.get("ok") for c in checks)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
