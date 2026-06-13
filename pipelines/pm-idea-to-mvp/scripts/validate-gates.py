#!/usr/bin/env python3
"""
validate-gates.py — Validate pipeline stage gates (v6.0.0).

Checks stage artifact files exist and meet minimum requirements.
Supports three modes:
  1. Default (v5.1 compat): file existence + URL counting + content checks
  2. --runtime: Execute actual commands from harness-rules.yaml (tests, builds, health probes)
  3. --goal: Verify goals from goals/{stage}.yaml

Exit 0 if all checks pass, 1 otherwise. Outputs JSON report.
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root

PIPELINE_VERSION = "6.0.0"

# Stage → required files/patterns (v5.1 backward-compatible checks)
STAGE_FILES = {
    "brief": {
        "files": ["00-brief.md"],
        "min_lines": 5,
    },
    "align": {
        "files": ["CONTEXT.md", "decisions.md"],
        "min_lines": 10,
    },
    "research": {
        "files": ["01-research.md"],
        "min_urls": 5,
        "min_lines": 20,
        "content_patterns": [
            r"竞品|competitor|对比|分析",
        ],
    },
    "analysis": {
        "files": ["02-analysis.md"],
        "min_lines": 30,
        "content_patterns": [
            r"方案|option|recommendation|推荐|风险|risk",
        ],
        "optional_dirs": ["architecture"],
    },
    "spec": {
        "files": ["03-prd.md", "03b-user-journey.md"],
        "min_lines": 20,
        "content_patterns": [
            r"用户故事|user stor|验收标准|acceptance",
        ],
        "optional_dirs": ["02b-prototype", "openspec"],
    },
    "mvp": {
        "files": ["04-mvp/README.md"],
        "min_lines": 5,
        "optional_dirs": ["04-mvp"],
    },
    "ship": {
        "files": ["RUNBOOK.md"],
        "min_lines": 10,
        "content_patterns": [
            r"部署|deploy|回滚|rollback|监控|monitor",
        ],
    },
    "operate": {
        "files": [],
        "min_lines": 0,
    },
    "grow": {
        "files": ["06-growth.md"],
        "min_lines": 15,
        "content_patterns": [
            r"增长|growth|指标|metric|渠道|channel",
        ],
    },
    "retro": {
        "files": ["05-retro.md"],
        "min_lines": 15,
        "content_patterns": [
            r"回顾|retro|evolution|进化|教训|lesson",
        ],
    },
}


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

    # Basic YAML parsing fallback for harness-rules format
    text = rules_path.read_text(encoding="utf-8")
    result = {}
    current_section = None
    current_subsection = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level keys
        if indent == 0 and ":" in stripped:
            key = stripped.split(":")[0].strip()
            val = stripped.split(":", 1)[1].strip().strip("'\"")
            if val:
                result[key] = val
            else:
                result[key] = {}
                current_section = key
            continue

        # Section content
        if current_section and indent > 0:
            if ":" in stripped:
                key = stripped.split(":")[0].strip().lstrip("- ")
                val = stripped.split(":", 1)[1].strip().strip("'\"")
                if isinstance(result.get(current_section), dict):
                    result[current_section][key] = val

    return result


def count_urls(content: str) -> int:
    """Count unique URLs in content."""
    url_pattern = r'https?://[^\s\)>\]\"\']+'
    urls = re.findall(url_pattern, content)
    return len(set(urls))


def check_file_exists(project_root: Path, filepath: str) -> dict:
    """Check if a file exists."""
    full_path = project_root / filepath
    exists = full_path.exists()
    return {
        "file": filepath,
        "exists": exists,
        "pass": exists,
    }


def check_min_lines(project_root: Path, filepath: str, min_lines: int) -> dict:
    """Check if file has minimum non-empty lines."""
    full_path = project_root / filepath
    if not full_path.exists():
        return {"file": filepath, "pass": False, "detail": "File not found"}

    content = full_path.read_text(encoding="utf-8", errors="replace")
    lines = [l for l in content.splitlines() if l.strip()]
    count = len(lines)
    passed = count >= min_lines
    return {
        "file": filepath,
        "pass": passed,
        "line_count": count,
        "min_required": min_lines,
    }


def check_url_count(project_root: Path, filepath: str, min_urls: int) -> dict:
    """Check if file has minimum unique URLs."""
    full_path = project_root / filepath
    if not full_path.exists():
        return {"file": filepath, "pass": False, "detail": "File not found"}

    content = full_path.read_text(encoding="utf-8", errors="replace")
    count = count_urls(content)
    passed = count >= min_urls
    return {
        "file": filepath,
        "pass": passed,
        "url_count": count,
        "min_required": min_urls,
    }


def check_content_pattern(project_root: Path, filepath: str, pattern: str) -> dict:
    """Check if file content matches a regex pattern."""
    full_path = project_root / filepath
    if not full_path.exists():
        return {"file": filepath, "pass": False, "detail": "File not found"}

    content = full_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(pattern, content, re.IGNORECASE)
    return {
        "file": filepath,
        "pass": bool(match),
        "pattern": pattern,
        "matched": bool(match),
    }


def validate_stage_files(stage: str, project_root: Path) -> list[dict]:
    """Run all v5.1-compatible file checks for a stage."""
    checks = []
    stage_config = STAGE_FILES.get(stage, {})

    if not stage_config:
        checks.append({
            "check": "stage_config",
            "pass": False,
            "detail": f"No configuration for stage: {stage}",
        })
        return checks

    # File existence checks
    for filepath in stage_config.get("files", []):
        checks.append(check_file_exists(project_root, filepath))

    # Min lines checks
    min_lines = stage_config.get("min_lines", 0)
    if min_lines > 0:
        for filepath in stage_config.get("files", []):
            checks.append(check_min_lines(project_root, filepath, min_lines))

    # URL count checks
    min_urls = stage_config.get("min_urls", 0)
    if min_urls > 0:
        for filepath in stage_config.get("files", []):
            checks.append(check_url_count(project_root, filepath, min_urls))

    # Content pattern checks
    for pattern in stage_config.get("content_patterns", []):
        for filepath in stage_config.get("files", []):
            checks.append(check_content_pattern(project_root, filepath, pattern))

    return checks


def resolve_runtime_config(harness: dict, project_root: Path) -> tuple[dict, Path]:
    """Merge runtime + project sections; return config and working directory."""
    runtime = harness.get("runtime", {}) or {}
    project = harness.get("project", {}) or {}
    merged = {
        "test_cmd": runtime.get("test_cmd") or project.get("test_cmd", ""),
        "build_cmd": runtime.get("build_cmd") or project.get("build_cmd", ""),
        "lint_cmd": runtime.get("lint_cmd") or project.get("lint_cmd", ""),
        "health_url": runtime.get("health_url") or project.get("health_url", ""),
        "workdir": runtime.get("workdir") or project.get("workdir") or ".",
    }
    workdir = merged["workdir"]
    cwd = project_root / workdir if workdir and workdir != "." else project_root
    return merged, cwd


def run_runtime_checks(stage: str, project_root: Path, harness: dict) -> list[dict]:
    """Execute runtime checks from harness-rules.yaml."""
    checks = []
    if not harness.get("project") and not harness.get("runtime"):
        checks.append({
            "check": "harness_config",
            "pass": False,
            "detail": "No project/runtime config in harness-rules.yaml",
        })
        return checks

    cfg, cwd = resolve_runtime_config(harness, project_root)
    test_cmd = cfg.get("test_cmd", "")
    build_cmd = cfg.get("build_cmd", "")
    lint_cmd = cfg.get("lint_cmd", "")
    health_url = cfg.get("health_url", "")

    # Test command
    if test_cmd:
        try:
            result = subprocess.run(
                test_cmd,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=180,
            )
            checks.append({
                "check": "test_command",
                "command": test_cmd,
                "pass": result.returncode == 0,
                "exit_code": result.returncode,
                "output_snippet": (result.stdout or result.stderr or "")[:500],
            })
        except subprocess.TimeoutExpired:
            checks.append({
                "check": "test_command",
                "command": test_cmd,
                "pass": False,
                "detail": "Command timed out (180s)",
            })
        except Exception as e:
            checks.append({
                "check": "test_command",
                "command": test_cmd,
                "pass": False,
                "detail": str(e),
            })

    # Lint command
    if lint_cmd:
        try:
            result = subprocess.run(
                lint_cmd,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=120,
            )
            checks.append({
                "check": "lint_command",
                "command": lint_cmd,
                "pass": result.returncode == 0,
                "exit_code": result.returncode,
                "output_snippet": (result.stdout or result.stderr or "")[:500],
            })
        except Exception as e:
            checks.append({
                "check": "lint_command",
                "command": lint_cmd,
                "pass": False,
                "detail": str(e),
            })

    # Build command
    if build_cmd:
        try:
            result = subprocess.run(
                build_cmd,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=120,
            )
            checks.append({
                "check": "build_command",
                "command": build_cmd,
                "pass": result.returncode == 0,
                "exit_code": result.returncode,
                "output_snippet": (result.stdout or result.stderr or "")[:500],
            })
        except subprocess.TimeoutExpired:
            checks.append({
                "check": "build_command",
                "command": build_cmd,
                "pass": False,
                "detail": "Command timed out (120s)",
            })
        except Exception as e:
            checks.append({
                "check": "build_command",
                "command": build_cmd,
                "pass": False,
                "detail": str(e),
            })

    # Health endpoint probe
    if health_url:
        try:
            req = urllib.request.Request(health_url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                checks.append({
                    "check": "health_probe",
                    "url": health_url,
                    "pass": 200 <= status < 400,
                    "status_code": status,
                })
        except urllib.error.URLError as e:
            checks.append({
                "check": "health_probe",
                "url": health_url,
                "pass": False,
                "detail": f"Connection failed: {e}",
            })
        except Exception as e:
            checks.append({
                "check": "health_probe",
                "url": health_url,
                "pass": False,
                "detail": str(e),
            })

    # Stage-specific goals from harness
    stage_goals = harness.get("goals", {}).get(stage, [])
    for goal in stage_goals:
        goal_type = goal.get("type", "")
        goal_id = goal.get("id", "?")

        if goal_type == "command_pass":
            cmd = goal.get("command", "")
            workdir = goal.get("workdir", "")
            cwd = project_root / workdir if workdir else project_root
            try:
                result = subprocess.run(
                    cmd, shell=True, cwd=str(cwd),
                    capture_output=True, text=True, timeout=120,
                )
                checks.append({
                    "check": f"goal_{goal_id}",
                    "command": cmd,
                    "pass": result.returncode == 0,
                    "exit_code": result.returncode,
                })
            except Exception as e:
                checks.append({
                    "check": f"goal_{goal_id}",
                    "pass": False,
                    "detail": str(e),
                })
        elif goal_type == "file_exists":
            target = goal.get("target", "")
            checks.append(check_file_exists(project_root, target))

    return checks


def run_goal_checks(stage: str, project_root: Path) -> dict:
    """Delegate to goal-check.py for goal verification."""
    scripts_dir = Path(__file__).resolve().parent
    goal_check_script = scripts_dir / "goal-check.py"

    if not goal_check_script.exists():
        return {
            "error": "goal-check.py not found",
            "pass": False,
        }

    try:
        result = subprocess.run(
            [sys.executable, str(goal_check_script),
             "--stage", stage,
             "--project-root", str(project_root)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(scripts_dir),
        )
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            report = {
                "raw_output": result.stdout[:1000],
                "stderr": result.stderr[:500],
            }
        report["pass"] = result.returncode == 0
        return report
    except subprocess.TimeoutExpired:
        return {"error": "goal-check.py timed out", "pass": False}
    except Exception as e:
        return {"error": str(e), "pass": False}


def main():
    parser = argparse.ArgumentParser(
        description="Validate pipeline stage gates (v6.0.0)"
    )
    parser.add_argument(
        "--run", dest="project_root",
        help="Project root directory (pm-{slug} repo)"
    )
    parser.add_argument(
        "--project-root", dest="project_root_alt",
        help="Alias for --run"
    )
    parser.add_argument(
        "--stage", required=True,
        help="Stage to validate (brief, align, research, analysis, spec, mvp, ship, operate, grow, retro)"
    )
    parser.add_argument(
        "--runtime", action="store_true",
        help="Execute runtime checks from harness-rules.yaml (tests, builds, health probes)"
    )
    parser.add_argument(
        "--goal", action="store_true",
        help="Verify goals from goals/{stage}.yaml"
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Write results to gates.json in project root"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress stdout, only write to gates.json"
    )

    args = parser.parse_args()
    project_root_str = args.project_root or args.project_root_alt
    if not project_root_str:
        print(json.dumps({"error": "No project root specified. Use --run or --project-root"}))
        sys.exit(1)

    project_root = Path(project_root_str).resolve()
    stage = args.stage

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "stage": stage,
        "project_root": str(project_root),
        "mode": [],
        "checks": [],
        "summary": {"total": 0, "passed": 0, "failed": 0},
        "all_passed": False,
    }

    # Mode 1: Standard file checks (always run unless only --goal)
    if not args.goal or args.runtime:
        report["mode"].append("file_checks")
        file_checks = validate_stage_files(stage, project_root)
        report["checks"].extend(file_checks)

    # Mode 2: Runtime checks
    if args.runtime:
        report["mode"].append("runtime")
        harness = load_harness_rules(project_root)
        if harness:
            runtime_checks = run_runtime_checks(stage, project_root, harness)
            report["checks"].extend(runtime_checks)
        else:
            report["checks"].append({
                "check": "harness_rules",
                "pass": False,
                "detail": "harness-rules.yaml not found in project root",
            })

    # Mode 3: Goal checks
    if args.goal:
        report["mode"].append("goals")
        goal_report = run_goal_checks(stage, project_root)
        report["goal_check"] = goal_report
        # If goal check failed, add a synthetic check entry
        if not goal_report.get("pass", False):
            report["checks"].append({
                "check": "goal_verification",
                "pass": False,
                "detail": f"Goal check failed: {goal_report.get('error', 'goals not met')}",
            })
        else:
            report["checks"].append({
                "check": "goal_verification",
                "pass": True,
                "detail": "All goals passed",
            })

    # Compute summary
    report["summary"]["total"] = len(report["checks"])
    report["summary"]["passed"] = sum(1 for c in report["checks"] if c.get("pass", False))
    report["summary"]["failed"] = report["summary"]["total"] - report["summary"]["passed"]
    report["all_passed"] = report["summary"]["failed"] == 0 and report["summary"]["total"] > 0

    # Write to gates.json if requested
    if args.write:
        gates_file = project_root / "gates.json"
        gates_data = {
            "version": PIPELINE_VERSION,
            stage: {
                "status": "pass" if report["all_passed"] else "fail",
                "checks": report["summary"],
                "mode": report["mode"],
            },
        }
        # Merge with existing gates.json
        if gates_file.exists():
            try:
                existing = json.loads(gates_file.read_text(encoding="utf-8"))
                existing.update(gates_data)
                gates_data = existing
            except (json.JSONDecodeError, Exception):
                pass
        gates_file.write_text(
            json.dumps(gates_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        report["gates_file_written"] = str(gates_file)

    # Output
    if not args.quiet:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    sys.exit(0 if report["all_passed"] else 1)


if __name__ == "__main__":
    main()
