#!/usr/bin/env python3
"""E2E smoke checks for pm-idea-to-mvp v7.2 infra."""
from __future__ import annotations

import json
import os
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


def check_profile_borrowed_skills() -> dict:
    sync_script = PIPELINE_SCRIPTS / "sync-hermes-profiles.py"
    if not sync_script.exists():
        return {"check": "profile_borrowed_skills", "ok": False, "error": "sync script missing"}
    cmd = [PY, str(sync_script), "--dry-run", "--sync-borrowed"]
    r = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        encoding="utf-8", errors="replace",
        env={**os.environ, "HERMES_HOME": str(HERMES_HOME)},
    )
    missing: list[str] = []
    if r.stdout.strip():
        try:
            data = json.loads(r.stdout)
            for prof in data.get("profiles") or []:
                borrowed = prof.get("borrowed") or {}
                for name in borrowed.get("borrowed_missing_src") or []:
                    missing.append(f"{prof.get('profile')}:src:{name}")
        except json.JSONDecodeError:
            pass
    profiles_root = HERMES_HOME / "profiles"
    profile_stages = {
        "pm-aligner": ["align"],
        "pm-researcher": ["research", "import"],
        "pm-analyst": ["analysis"],
        "pm-planner": ["spec"],
        "pm-builder": ["mvp", "retro", "import"],
        "pm-shipper": ["ship"],
        "pm-operator": ["operate"],
        "pm-growth": ["grow"],
    }
    import yaml

    stage_cfg_path = SKILLS / "pipelines/pm-idea-to-mvp/stage-skills.yaml"
    stage_cfg = yaml.safe_load(stage_cfg_path.read_text(encoding="utf-8")) if stage_cfg_path.exists() else {}
    stages = stage_cfg.get("stages") or {}
    for profile, stage_keys in profile_stages.items():
        for stage_key in stage_keys:
            for name in stages.get(stage_key, {}).get("borrowed") or []:
                dest = profiles_root / profile / "skills" / "borrowed" / name / "SKILL.md"
                if not dest.exists():
                    missing.append(f"{profile}:{name}")
    return {
        "check": "profile_borrowed_skills",
        "ok": not missing,
        "missing": missing[:20],
        "missing_count": len(missing),
    }


def check_pm_routing_smoke() -> dict:
    if not HERMES_AGENT.exists():
        return {"check": "pm_routing_smoke", "ok": True, "skipped": "hermes-agent not found"}
    agent_path = str(HERMES_AGENT).replace("\\", "\\\\")
    sample = (
        "使用想法到产品 新开一个项目 [amnRideAI/demo-repository] "
        "clone整个代码仓 深入优化"
    )
    cmd = [
        PY, "-c",
        f"import sys; sys.path.insert(0, r'{agent_path}'); "
        "from hermes_cli import pm_pipeline as p; "
        f"t={sample!r}; "
        "assert p.detect_scenario(t)=='import_repo', p.detect_scenario(t); "
        "assert p.extract_slug('', t)=='demo-repository', p.extract_slug('', t); "
        "assert p.classify_route('/goal '+t)=='pm_kanban'",
    ]
    return run(cmd)


def check_pm_kanban_guard() -> dict:
    if not HERMES_AGENT.exists():
        return {"check": "pm_kanban_guard", "ok": True, "skipped": "hermes-agent not found"}
    agent_path = str(HERMES_AGENT).replace("\\", "\\\\")
    cmd = [
        PY, "-c",
        f"import sys; sys.path.insert(0, r'{agent_path}'); "
        "from hermes_cli.pm_kanban_guard import pm_pipeline_completion_blocked; "
        "import sqlite3; c=sqlite3.connect(':memory:'); "
        "body='stage: mvp-iter1\\nSlug: demo\\nProject root: D:/workspace/projects/pm-demo'; "
        "msg=pm_pipeline_completion_blocked(c,'t_x',assignee='pm-builder',body=body,title='MVP',status='ready'); "
        "assert msg and 'gates not pass' in msg",
    ]
    return run(cmd)


def check_worker_skill_preload() -> dict:
    if not HERMES_AGENT.exists():
        return {"check": "worker_skill_preload", "ok": True, "skipped": "hermes-agent not found"}
    agent_path = str(HERMES_AGENT).replace("\\", "\\\\")
    profile_home = str(HERMES_HOME / "profiles" / "pm-builder").replace("\\", "/")
    cmd = [
        PY, "-c",
        f"import os; os.environ['HERMES_HOME']=r'{profile_home}'; "
        f"import sys; sys.path.insert(0, r'{agent_path}'); "
        "from agent.skill_commands import build_preloaded_skills_prompt; "
        "_, loaded, missing = build_preloaded_skills_prompt(['kw-testing-strategy']); "
        "assert not missing, missing; assert 'testing-strategy' in loaded",
    ]
    return run(cmd)
    if not HERMES_AGENT.exists():
        return {"check": "pm_routing_smoke", "ok": True, "skipped": "hermes-agent not found"}
    agent_path = str(HERMES_AGENT).replace("\\", "\\\\")
    sample = (
        "使用想法到产品 新开一个项目 [amnRideAI/demo-repository] "
        "clone整个代码仓 深入优化"
    )
    cmd = [
        PY, "-c",
        f"import sys; sys.path.insert(0, r'{agent_path}'); "
        "from hermes_cli import pm_pipeline as p; "
        f"t={sample!r}; "
        "assert p.detect_scenario(t)=='import_repo', p.detect_scenario(t); "
        "assert p.extract_slug('', t)=='demo-repository', p.extract_slug('', t); "
        "assert p.classify_route('/goal '+t)=='pm_kanban'",
    ]
    return run(cmd)


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
    checks.append(check_profile_borrowed_skills())
    checks.append(check_pm_routing_smoke())
    checks.append(check_pm_kanban_guard())
    checks.append(check_worker_skill_preload())
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
