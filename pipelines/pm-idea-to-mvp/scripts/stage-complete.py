#!/usr/bin/env python3
"""
stage-complete.py — Orchestrate stage completion (v8.0.0).

Flow: progress-tracker update → validate-gates → eval-stage → goal-check (optional)
      → build-run-report → feishu_notify → git push

Reads harness-rules.yaml to determine if stage needs human checkpoint.
By default only 'ship' requires human approval (align/spec become auto if harness says so).
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from execution_mode import human_checkpoint_stages
from pipeline_paths import resolve_pipeline_root, resolve_skills_root
from pipeline_version import PIPELINE_VERSION

# Default human checkpoints (overridable via harness-rules.yaml; empty when auto_hitl)
DEFAULT_HUMAN_CHECKPOINT_STAGES: list[str] = []

# Stages that MANDATE runtime verification (cannot be skipped)
# Based on pm-knowledge-platform post-mortem: tasks were marked complete without
# actual verification, leading to bugs surfacing only at deployment.
MANDATORY_RUNTIME_STAGES = ["mvp", "ship"]
MANDATORY_GOAL_STAGES = ["mvp", "ship", "retro"]

# Stages that mandate docs-hygiene check before completion
MANDATORY_DOCS_HYGIENE_STAGES = ["align", "analysis", "spec", "mvp", "ship"]

# v7.0: Stages that mandate behavior check (anti-rationalization + failure modes)
MANDATORY_BEHAVIOR_STAGES = ["align", "research", "analysis", "spec", "mvp", "ship", "operate", "grow", "retro"]


def check_behavior(stage: str, project_root: Path, skills_root: Path) -> dict:
    """
    v7.0: Check stage card for anti-rationalization table and failure modes.
    Returns dict with status, issues, and details.
    """
    stage_card_dir = skills_root / "pipelines" / "pm-idea-to-mvp" / "references" / "hermes-stage-cards"
    
    # Map stage names to file names
    stage_file_map = {
        "mvp": "mvp-iter.md",  # mvp uses mvp-iter card
        "mvp-plan": "mvp-plan.md",
    }
    card_file = stage_file_map.get(stage, f"{stage}.md")
    card_path = stage_card_dir / card_file
    
    result = {
        "status": "ok",
        "issues": [],
        "checks": {
            "anti_rationalization": False,
            "failure_modes": False,
            "behavior_code_ref": False,
            "version_tag": False,
        }
    }
    
    if not card_path.exists():
        result["status"] = "skip"
        result["detail"] = f"Stage card {card_file} not found"
        return result
    
    try:
        content = card_path.read_text(encoding="utf-8")
    except Exception as e:
        result["status"] = "error"
        result["detail"] = f"Failed to read stage card: {e}"
        return result
    
    # Check 1: Anti-rationalization table
    if "反合理化" in content or "Rationalization" in content:
        result["checks"]["anti_rationalization"] = True
    else:
        result["issues"].append("Missing anti-rationalization table (反合理化表格)")
    
    # Check 2: Failure modes section
    if "失败模式" in content or "Failure Mode" in content:
        result["checks"]["failure_modes"] = True
    else:
        result["issues"].append("Missing failure modes section (失败模式)")
    
    # Check 3: Reference to agent-behavior-code.md
    if "agent-behavior-code" in content:
        result["checks"]["behavior_code_ref"] = True
    else:
        result["issues"].append("Missing reference to agent-behavior-code.md")
    
    # Check 4: Version tag (v7.0)
    if "v7.0" in content:
        result["checks"]["version_tag"] = True
    else:
        result["issues"].append("Missing v7.0 version tag")
    
    # Determine overall status
    if result["issues"]:
        result["status"] = "warning"  # Don't block, just warn
    
    return result


def load_harness_rules(project_root: Path) -> dict:
    """Load harness-rules.yaml from project root."""
    rules_path = project_root / "harness-rules.yaml"
    if not rules_path.exists():
        return {}

    try:
        import yaml
        with open(rules_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        pass

    # Basic fallback parser
    text = rules_path.read_text(encoding="utf-8")
    result = {}
    current_section = None
    in_list = False
    list_key = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        if indent == 0 and ":" in stripped:
            key = stripped.split(":")[0].strip()
            val = stripped.split(":", 1)[1].strip().strip("'\"")
            if val:
                result[key] = val
            else:
                result[key] = {}
                current_section = key
            in_list = False
            continue

        if current_section and indent > 0:
            if stripped.startswith("- "):
                # List item
                val = stripped[2:].strip().strip("'\"")
                if isinstance(result.get(current_section), dict):
                    if list_key is None:
                        list_key = current_section
                    # This is a list under the section
                    if not isinstance(result[current_section], list):
                        result[current_section] = []
                    result[current_section].append(val)
                elif isinstance(result.get(current_section), list):
                    result[current_section].append(val)
            elif ":" in stripped:
                key = stripped.split(":")[0].strip()
                val = stripped.split(":", 1)[1].strip().strip("'\"")
                if isinstance(result.get(current_section), dict):
                    result[current_section][key] = val

    return result


def get_human_checkpoint_stages(project_root: Path) -> list[str]:
    """Human checkpoint stages; empty when auto_hitl (lights-out mode)."""
    return human_checkpoint_stages(project_root)


def run_script(script_name: str, args: list[str], project_root: Path, timeout: int = 300) -> dict:
    """Run a pipeline script and capture output."""
    scripts_dir = Path(__file__).resolve().parent
    script_path = scripts_dir / script_name

    if not script_path.exists():
        return {
            "script": script_name,
            "status": "error",
            "detail": f"Script not found: {script_path}",
            "exit_code": -1,
        }

    cmd = [sys.executable, str(script_path)] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(scripts_dir),
        )
        output = result.stdout.strip()
        # Try to parse JSON from output
        try:
            parsed = json.loads(output) if output else {}
        except json.JSONDecodeError:
            parsed = {"raw_output": output[:2000]}

        return {
            "script": script_name,
            "status": "ok" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "result": parsed,
            "stderr": result.stderr[:500] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "script": script_name,
            "status": "timeout",
            "detail": f"Timed out after {timeout}s",
            "exit_code": -1,
        }
    except Exception as e:
        return {
            "script": script_name,
            "status": "error",
            "detail": str(e),
            "exit_code": -1,
        }


def run_feishu_notify(
    stage: str,
    project_root: Path,
    passed: bool,
    task_id: str = "",
    *,
    needs_checkpoint: bool = False,
) -> dict:
    """Send Feishu notification via feishu_notify.py if available."""
    scripts_dir = Path(__file__).resolve().parent
    skills_root = resolve_skills_root()

    notify_scripts = [
        scripts_dir / "feishu_notify.py",
        skills_root / "scripts" / "feishu_notify.py",
    ]

    if needs_checkpoint and passed:
        status_text = "CHECKPOINT ⏸ — awaiting confirm"
    else:
        status_text = "PASS ✅" if passed else "FAIL ❌"

    for notify_script in notify_scripts:
        if notify_script.exists():
            args = [
                "--stage", stage,
                "--status", status_text,
                "--project-root", str(project_root),
            ]
            if task_id:
                args.extend(["--task-id", task_id])
            if needs_checkpoint and passed:
                args.append("--human-checkpoint")

            return run_script("feishu_notify.py", args, project_root, timeout=30)

    # Try hermes feishu_notify command
    try:
        status_text = "PASS ✅" if passed else "FAIL ❌"
        result = subprocess.run(
            ["hermes", "feishu_notify", "--stage", stage, "--status", status_text],
            capture_output=True, text=True, timeout=30,
        )
        return {
            "script": "hermes feishu_notify",
            "status": "ok" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "output": result.stdout[:500],
        }
    except Exception:
        return {
            "script": "feishu_notify",
            "status": "skipped",
            "detail": "No feishu_notify available",
        }


def run_git_push(project_root: Path) -> dict:
    """Git add, commit, and push stage completion."""
    try:
        # Stage all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(project_root),
            capture_output=True, text=True, timeout=30,
        )

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        commit_msg = f"stage-complete: pipeline v{PIPELINE_VERSION} @ {now}"

        result = subprocess.run(
            ["git", "commit", "-m", commit_msg, "--allow-empty"],
            cwd=str(project_root),
            capture_output=True, text=True, timeout=30,
        )

        push_result = subprocess.run(
            ["git", "push"],
            cwd=str(project_root),
            capture_output=True, text=True, timeout=60,
        )

        return {
            "action": "git_push",
            "status": "ok" if push_result.returncode == 0 else "failed",
            "commit": result.stdout[:200] if result.stdout else "",
            "push_output": push_result.stdout[:200] or push_result.stderr[:200],
            "exit_code": push_result.returncode,
        }
    except Exception as e:
        return {
            "action": "git_push",
            "status": "error",
            "detail": str(e),
        }


def build_run_report(stage: str, project_root: Path) -> dict:
    """Build a run report for the stage completion."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    script_dir = Path(__file__).resolve().parent
    build_script = script_dir / "build-run-report.py"
    pages = None
    if build_script.exists():
        r = subprocess.run(
            [sys.executable, str(build_script), "--run", str(project_root)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode == 0:
            try:
                pages = json.loads(r.stdout)
            except json.JSONDecodeError:
                pages = {"raw": (r.stdout or "")[:500]}
        else:
            pages = {"error": (r.stderr or r.stdout or "")[:300]}
    return {
        "pipeline_version": PIPELINE_VERSION,
        "stage": stage,
        "project_root": str(project_root),
        "timestamp": now,
        "status": "completed",
        "pages": pages,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate stage completion (v6.0.0)"
    )
    parser.add_argument(
        "--stage", required=True,
        help="Stage being completed"
    )
    parser.add_argument(
        "--project-root", required=True,
        help="Project root directory"
    )
    parser.add_argument(
        "--task-id", default="",
        help="Kanban task ID for notifications"
    )
    parser.add_argument(
        "--verify-goals", action="store_true",
        help="Run goal-check.py for the stage"
    )
    parser.add_argument(
        "--runtime", action="store_true",
        help="Enable runtime checks in validate-gates"
    )
    parser.add_argument(
        "--skip-git", action="store_true",
        help="Skip git push (for resume scenarios)"
    )
    parser.add_argument(
        "--skip-notify", action="store_true",
        help="Skip Feishu notification"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Force completion even if gates fail"
    )
    parser.add_argument(
        "--progress-task", type=int,
        help="Update this progress task ID to 'done' before validation"
    )
    parser.add_argument(
        "--check-behavior", action="store_true",
        help="v7.0: Check stage card for anti-rationalization table and failure modes"
    )

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    stage = args.stage

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "stage": stage,
        "project_root": str(project_root),
        "task_id": args.task_id,
        "steps": [],
        "all_passed": False,
        "needs_human_checkpoint": False,
        "human_checkpoint_reason": "",
    }

    # Step 0: Determine human checkpoint requirement
    checkpoint_stages = get_human_checkpoint_stages(project_root)
    needs_checkpoint = stage in checkpoint_stages
    report["needs_human_checkpoint"] = needs_checkpoint
    if needs_checkpoint:
        report["human_checkpoint_reason"] = f"Stage '{stage}' requires human approval per harness-rules.yaml"

    # Step 1: Update progress tracker (if task specified)
    if args.progress_task:
        progress_result = run_script(
            "progress-tracker.py",
            ["--project-root", str(project_root), "update",
             "--task", str(args.progress_task), "--status", "done"],
            project_root,
        )
        report["steps"].append({"step": "progress_update", **progress_result})

    # Step 1b: Harness runner (risk decisions)
    harness_args = ["--project-root", str(project_root), "--stage", stage]
    harness_result = run_script("harness-runner.py", harness_args, project_root)
    report["steps"].append({"step": "harness_runner", **harness_result})

    # Step 2: Validate gates (with mandatory runtime for mvp/ship)
    gate_args = ["--stage", stage, "--run", str(project_root), "--write"]
    # v6.2: Force runtime verification for stages that need it
    if args.runtime or stage in MANDATORY_RUNTIME_STAGES:
        gate_args.append("--runtime")
    # v6.2: Force goal verification for stages that need it
    if args.verify_goals or stage in MANDATORY_GOAL_STAGES:
        gate_args.append("--goal")

    gates_result = run_script("validate-gates.py", gate_args, project_root)
    report["steps"].append({"step": "validate_gates", **gates_result})

    gates_passed = gates_result.get("exit_code", 1) == 0

    # Step 2b: v6.2 — Mandatory docs-hygiene check (cross-document consistency)
    if stage in MANDATORY_DOCS_HYGIENE_STAGES:
        hygiene_args = ["--project-root", str(project_root), "--json"]
        hygiene_result = run_script("../../scripts/check_docs_ssot.py", hygiene_args, project_root)
        # Also try the skills root location
        if hygiene_result.get("status") == "error":
            hygiene_result = run_script("check_docs_ssot.py", hygiene_args, project_root)
        report["steps"].append({"step": "docs_hygiene", **hygiene_result})
        hygiene_ok = hygiene_result.get("exit_code", 1) == 0 or hygiene_result.get("status") == "ok"
        if not hygiene_ok:
            # Don't block on warnings, only on errors
            hygiene_data = hygiene_result.get("result", {})
            has_errors = any(
                i.get("severity") == "error"
                for i in hygiene_data.get("issues", [])
            ) if isinstance(hygiene_data, dict) else False
            if has_errors and not args.force:
                gates_passed = False

    # Step 2c: v7.0 — Behavior check (anti-rationalization + failure modes)
    if args.check_behavior or stage in MANDATORY_BEHAVIOR_STAGES:
        behavior_result = check_behavior(stage, project_root, resolve_skills_root())
        report["steps"].append({"step": "behavior_check", **behavior_result})
        # Behavior check is advisory (warning), not blocking
        if behavior_result.get("status") == "error" and not args.force:
            gates_passed = False

    # Step 2d: v7.1 — Lighthouse (ship + runtime, advisory)
    if stage == "ship" and (args.runtime or stage in MANDATORY_RUNTIME_STAGES):
        skills_root = resolve_skills_root()
        lh = skills_root / "scripts" / "lighthouse_check.py"
        if lh.exists():
            lh_result = subprocess.run(
                [sys.executable, str(lh), "--project-root", str(project_root), "--json"],
                capture_output=True,
                text=True,
                timeout=200,
                cwd=str(project_root),
            )
            try:
                lh_data = json.loads(lh_result.stdout) if lh_result.stdout.strip() else {}
            except json.JSONDecodeError:
                lh_data = {"status": "error", "raw": lh_result.stdout[:200]}
            report["steps"].append({
                "step": "lighthouse_check",
                "status": "ok" if lh_result.returncode == 0 else "warning",
                "exit_code": lh_result.returncode,
                "result": lh_data,
            })

    # Step 3: Eval stage (quality scoring)
    eval_args = ["--stage", stage, "--project-root", str(project_root)]
    if args.runtime:
        eval_args.append("--runtime")

    eval_result = run_script("eval-stage.py", eval_args, project_root)
    report["steps"].append({"step": "eval_stage", **eval_result})

    eval_passed = eval_result.get("exit_code", 1) == 0

    # Step 4: Goal check (mandatory for certain stages, optional for others)
    if args.verify_goals or stage in MANDATORY_GOAL_STAGES:
        goal_args = ["--stage", stage, "--project-root", str(project_root)]
        goal_result = run_script("goal-check.py", goal_args, project_root)
        report["steps"].append({"step": "goal_check", **goal_result})
        # v6.2: Goal failure blocks stage completion (no more self-reported completion)
        goal_passed = goal_result.get("exit_code", 1) == 0
        if not goal_passed and not args.force:
            gates_passed = False

    # Determine overall pass
    all_checks_passed = gates_passed and eval_passed
    if args.force:
        all_checks_passed = True

    report["all_passed"] = all_checks_passed

    # Step 5: Build run report
    run_report = build_run_report(stage, project_root)
    run_report["checks_passed"] = all_checks_passed
    report["steps"].append({"step": "build_run_report", "report": run_report})

    # Step 6: Git push before notify so Pages link reflects latest report
    if not args.skip_git and all_checks_passed:
        git_result = run_git_push(project_root)
        report["steps"].append({"step": "git_push", **git_result})
    elif not args.skip_git and not all_checks_passed:
        report["steps"].append({
            "step": "git_push",
            "status": "skipped",
            "detail": "Checks failed, skipping git push",
        })

    # Step 7: Feishu notification (after push when checks passed)
    if not args.skip_notify:
        notify_result = run_feishu_notify(
            stage, project_root, all_checks_passed, args.task_id,
            needs_checkpoint=needs_checkpoint,
        )
        report["steps"].append({"step": "feishu_notify", **notify_result})

    # Final status
    # Final status + platform actions
    kanban_action = "complete" if all_checks_passed and not needs_checkpoint else "block" if needs_checkpoint else "defer"
    report["kanban_action"] = kanban_action

    if args.task_id and all_checks_passed:
        if needs_checkpoint:
            sync_result = run_script(
                "kanban-sync.py",
                ["--task-id", args.task_id, "--project-root", str(project_root),
                 "--action", "block", "--reason", report.get("human_checkpoint_reason", "human checkpoint")],
                project_root,
            )
        else:
            sync_result = run_script(
                "kanban-sync.py",
                ["--task-id", args.task_id, "--project-root", str(project_root), "--action", "complete"],
                project_root,
            )
        report["steps"].append({"step": "kanban_sync", **sync_result})

    cursor_status = project_root / ".cursor" / "stage-status.json"
    cursor_status.parent.mkdir(parents=True, exist_ok=True)
    cursor_status.write_text(
        json.dumps({
            "stage": stage,
            "all_passed": all_checks_passed,
            "needs_human_checkpoint": needs_checkpoint,
            "kanban_action": kanban_action,
            "pipeline_version": PIPELINE_VERSION,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if needs_checkpoint and all_checks_passed:
        report["action_required"] = "human_checkpoint"
        report["message"] = f"Stage '{stage}' passed all checks. Awaiting human approval."
    elif all_checks_passed:
        report["action_required"] = "none"
        report["message"] = f"Stage '{stage}' completed successfully."
    else:
        report["action_required"] = "fix_failures"
        report["message"] = f"Stage '{stage}' has failing checks. Review and retry."

    print(json.dumps(report, ensure_ascii=False, indent=2))

    # Exit code: 0 if passed, 1 if failed
    sys.exit(0 if all_checks_passed else 1)


if __name__ == "__main__":
    main()
