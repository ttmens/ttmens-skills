#!/usr/bin/env python3
"""
goal-check.py — Verify goal conditions for a pipeline stage.

Reads goals/{stage}.yaml from the project root and checks each goal condition.
Supports: file_exists, content_match, command_pass, url_count, min_lines,
min_table_rows, and composite (AND/OR) goals.

Exit 0 if all goals pass, 1 otherwise. Outputs JSON report.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add scripts dir to path for pipeline_paths import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root

PIPELINE_VERSION = "6.0.0"


def load_yaml_simple(path: Path) -> dict:
    """
    Minimal YAML parser for goals files. Handles the subset of YAML
    used in goals/{stage}.yaml without requiring PyYAML.
    Falls back to PyYAML if available.
    """
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        pass

    # Fallback: basic parser for the goals YAML format
    text = path.read_text(encoding="utf-8")
    result = {}
    current_list = None
    current_item = None
    stage_name = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Top-level key: stage: xxx
        if line.startswith("stage:"):
            stage_name = stripped.split(":", 1)[1].strip().strip("'\"")
            result["stage"] = stage_name
            continue

        # goals: starts the list
        if stripped == "goals:":
            result["goals"] = []
            current_list = result["goals"]
            continue

        # List item start: - id: R1
        if stripped.startswith("- id:"):
            current_item = {}
            val = stripped.split(":", 1)[1].strip().strip("'\"")
            current_item["id"] = val
            if current_list is not None:
                current_list.append(current_item)
            continue

        # List item continuation: key: value
        if current_item is not None and ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip("'\"")
            # Try to convert numeric values
            try:
                val = int(val)
            except (ValueError, TypeError):
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    pass
            current_item[key] = val
            continue

    return result


def check_file_exists(target: str, project_root: Path) -> dict:
    """Check if a file exists."""
    file_path = project_root / target
    exists = file_path.exists()
    return {
        "pass": exists,
        "detail": f"File {'exists' if exists else 'NOT FOUND'}: {target}"
    }


def check_content_match(target: str, pattern: str, project_root: Path) -> dict:
    """Check if file content matches a regex pattern."""
    file_path = project_root / target
    if not file_path.exists():
        return {"pass": False, "detail": f"File not found: {target}"}

    content = file_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(pattern, content, re.IGNORECASE)
    return {
        "pass": bool(match),
        "detail": f"Pattern '{pattern}' {'found' if match else 'NOT FOUND'} in {target}"
    }


def check_command_pass(command: str, workdir: str | None, project_root: Path) -> dict:
    """Run a command and check if it exits with code 0."""
    cwd = project_root / workdir if workdir else project_root
    if not cwd.exists():
        return {"pass": False, "detail": f"Workdir not found: {workdir}"}

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120
        )
        passed = result.returncode == 0
        output_snippet = (result.stdout or result.stderr or "")[:500]
        return {
            "pass": passed,
            "detail": f"Command '{command}' exit={result.returncode}",
            "output": output_snippet
        }
    except subprocess.TimeoutExpired:
        return {"pass": False, "detail": f"Command timed out: {command}"}
    except Exception as e:
        return {"pass": False, "detail": f"Command error: {e}"}


def check_url_count(target: str, min_count: int, project_root: Path) -> dict:
    """Count URLs in a file and check against minimum."""
    file_path = project_root / target
    if not file_path.exists():
        return {"pass": False, "detail": f"File not found: {target}"}

    content = file_path.read_text(encoding="utf-8", errors="replace")
    url_pattern = r'https?://[^\s\)>\]\"\']+'
    urls = re.findall(url_pattern, content)
    unique_urls = set(urls)
    count = len(unique_urls)
    passed = count >= min_count
    return {
        "pass": passed,
        "detail": f"URL count: {count} (min: {min_count}) in {target}",
        "count": count
    }


def check_min_lines(target: str, min_count: int, project_root: Path) -> dict:
    """Check if file has at least min_count non-empty lines."""
    file_path = project_root / target
    if not file_path.exists():
        return {"pass": False, "detail": f"File not found: {target}"}

    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = [l for l in content.splitlines() if l.strip()]
    count = len(lines)
    passed = count >= min_count
    return {
        "pass": passed,
        "detail": f"Line count: {count} (min: {min_count}) in {target}",
        "count": count
    }


def check_min_table_rows(target: str, min_count: int, project_root: Path) -> dict:
    """Count markdown table rows (lines starting with |) and check minimum."""
    file_path = project_root / target
    if not file_path.exists():
        return {"pass": False, "detail": f"File not found: {target}"}

    content = file_path.read_text(encoding="utf-8", errors="replace")
    # Count table rows (lines starting with |, excluding separator lines like |---|)
    table_rows = [
        l for l in content.splitlines()
        if l.strip().startswith("|") and not re.match(r'^\|[\s\-:|]+\|$', l.strip())
    ]
    # Subtract header row if present (first table row)
    count = max(0, len(table_rows) - 1) if table_rows else 0
    passed = count >= min_count
    return {
        "pass": passed,
        "detail": f"Table rows: {count} (min: {min_count}) in {target}",
        "count": count
    }


def check_forbidden(target: str, pattern: str, project_root: Path) -> dict:
    """Fail if forbidden pattern appears in file."""
    file_path = project_root / target
    if not file_path.exists():
        return {"pass": True, "detail": f"File not found (forbidden skipped): {target}"}
    content = file_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(pattern, content, re.IGNORECASE)
    return {
        "pass": not bool(match),
        "detail": f"Forbidden pattern {'FOUND' if match else 'absent'} in {target}",
    }


def check_min_matches(target: str, pattern: str, min_count: int, project_root: Path) -> dict:
    """Count regex matches in file."""
    file_path = project_root / target
    if not file_path.exists():
        return {"pass": False, "detail": f"File not found: {target}"}
    content = file_path.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(pattern, content, re.IGNORECASE)
    count = len(matches)
    return {
        "pass": count >= min_count,
        "detail": f"Matches: {count} (min: {min_count}) in {target}",
        "count": count,
    }


def check_debate_resolved(debates_dir: str, stage_prefix: str, project_root: Path) -> dict:
    """Verify debate rounds exist and synthesis has no open questions."""
    base = project_root / debates_dir
    if not base.exists():
        return {"pass": False, "detail": f"Debates dir missing: {debates_dir}"}
    rounds = sorted(base.glob(f"{stage_prefix}-*.md"))
    if len(rounds) < 2:
        return {"pass": False, "detail": f"Need ≥2 debate files for {stage_prefix}, found {len(rounds)}"}
    synthesis = base / f"{stage_prefix}-synthesis.md"
    if synthesis.exists():
        text = synthesis.read_text(encoding="utf-8", errors="replace")
        open_q = re.findall(r"OPEN\s*[?:]|待决|未解决|TBD", text, re.IGNORECASE)
        if open_q:
            return {"pass": False, "detail": f"Open questions in synthesis: {len(open_q)}"}
    return {"pass": True, "detail": f"Debate resolved for {stage_prefix} ({len(rounds)} rounds)"}


def args_stage_prefix(goal: dict) -> str:
    return goal.get("stage_prefix") or goal.get("stage", "align")


def evaluate_goal(goal: dict, project_root: Path) -> dict:
    """Evaluate a single goal condition."""
    goal_id = goal.get("id", "?")
    goal_type = goal.get("type", "")
    description = goal.get("description", "")

    result = {
        "id": goal_id,
        "description": description,
        "type": goal_type,
    }

    if goal_type == "file_exists":
        check = check_file_exists(goal["target"], project_root)
    elif goal_type == "content_match":
        check = check_content_match(goal["target"], goal["pattern"], project_root)
    elif goal_type == "command_pass":
        check = check_command_pass(
            goal["command"],
            goal.get("workdir"),
            project_root
        )
    elif goal_type == "url_count":
        check = check_url_count(goal["target"], goal.get("min", 5), project_root)
    elif goal_type == "min_lines":
        check = check_min_lines(goal["target"], goal.get("min", 10), project_root)
    elif goal_type == "min_table_rows":
        check = check_min_table_rows(goal["target"], goal.get("min", 3), project_root)
    elif goal_type == "forbidden":
        check = check_forbidden(goal["target"], goal["pattern"], project_root)
    elif goal_type == "min_matches":
        check = check_min_matches(
            goal["target"], goal["pattern"], goal.get("min", goal.get("min_matches", 1)), project_root
        )
    elif goal_type == "debate_resolved":
        check = check_debate_resolved(
            goal.get("debates_dir", "debates"),
            goal.get("stage_prefix", args_stage_prefix(goal)),
            project_root,
        )
    elif goal_type == "composite_and":
        # All sub-conditions must pass
        sub_results = []
        for sub in goal.get("conditions", []):
            sub_results.append(evaluate_goal(sub, project_root))
        all_pass = all(r.get("passed", False) for r in sub_results)
        check = {
            "pass": all_pass,
            "detail": f"AND composite: {sum(1 for r in sub_results if r.get('passed'))}/{len(sub_results)} passed",
            "sub_results": sub_results
        }
    elif goal_type == "composite_or":
        # At least one sub-condition must pass
        sub_results = []
        for sub in goal.get("conditions", []):
            sub_results.append(evaluate_goal(sub, project_root))
        any_pass = any(r.get("passed", False) for r in sub_results)
        check = {
            "pass": any_pass,
            "detail": f"OR composite: {sum(1 for r in sub_results if r.get('passed'))}/{len(sub_results)} passed",
            "sub_results": sub_results
        }
    else:
        check = {"pass": False, "detail": f"Unknown goal type: {goal_type}"}

    result["passed"] = check["pass"]
    result["detail"] = check["detail"]
    if "output" in check:
        result["output"] = check["output"]
    if "sub_results" in check:
        result["sub_results"] = check["sub_results"]

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Verify goal conditions for a pipeline stage"
    )
    parser.add_argument(
        "--stage", required=True,
        help="Stage name (e.g., research, mvp, ship)"
    )
    parser.add_argument(
        "--project-root", required=True,
        help="Project root directory (pm-{slug} repo)"
    )
    parser.add_argument(
        "--goals-file",
        help="Override goals file path (default: goals/{stage}.yaml)"
    )
    parser.add_argument(
        "--json", action="store_true", default=True,
        help="Output JSON (default: true)"
    )
    parser.add_argument(
        "--runtime-only", action="store_true",
        help="Only verify runtime goals (check_type: command_pass)"
    )

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    # Determine goals file
    if args.goals_file:
        goals_path = Path(args.goals_file)
    else:
        goals_path = project_root / "goals" / f"{args.stage}.yaml"

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "stage": args.stage,
        "project_root": str(project_root),
        "goals_file": str(goals_path),
        "goals": [],
        "summary": {"total": 0, "passed": 0, "failed": 0},
        "all_passed": False
    }

    if not goals_path.exists():
        report["error"] = f"Goals file not found: {goals_path}"
        report["all_passed"] = False
        print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(1)

    # Load goals
    try:
        data = load_yaml_simple(goals_path)
    except Exception as e:
        report["error"] = f"Failed to parse goals file: {e}"
        report["all_passed"] = False
        print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(1)

    goals = data.get("goals", [])
    
    # Filter goals if --runtime-only
    if args.runtime_only:
        goals = [g for g in goals if g.get("type") == "command_pass" or g.get("check_type") == "runtime"]
    
    report["summary"]["total"] = len(goals)

    # Evaluate each goal
    for goal in goals:
        result = evaluate_goal(goal, project_root)
        optional = goal.get("optional", False)
        if optional and not result["passed"]:
            result["passed"] = True
            result["detail"] += " (optional, skipped)"
        report["goals"].append(result)
        if result["passed"]:
            report["summary"]["passed"] += 1
        else:
            report["summary"]["failed"] += 1

    report["summary"]["failed"] = sum(1 for g in report["goals"] if not g["passed"])
    report["summary"]["passed"] = report["summary"]["total"] - report["summary"]["failed"]
    report["all_passed"] = report["summary"]["failed"] == 0 and report["summary"]["total"] > 0

    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["all_passed"] else 1)


if __name__ == "__main__":
    main()
