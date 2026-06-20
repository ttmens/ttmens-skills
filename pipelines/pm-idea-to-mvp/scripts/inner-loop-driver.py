#!/usr/bin/env python3
"""
Drive MVP inner loop: Plan → Code → Test → Observe → Adjust (max N iterations).

v9.1: artifact-driven; runtime checks from harness-rules.yaml (no validate-gates.py).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_version import PIPELINE_VERSION


def load_harness_rules(project_root: Path) -> dict:
    rules_path = project_root / "harness-rules.yaml"
    if not rules_path.exists():
        return {}
    try:
        import yaml

        with open(rules_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        pass
    result: dict = {}
    current_section: str | None = None
    for line in rules_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and stripped.endswith(":"):
            current_section = stripped[:-1]
            result[current_section] = {}
            continue
        if current_section and ":" in stripped:
            key, _, val = stripped.partition(":")
            result[current_section][key.strip()] = val.strip().strip("'\"")
    return result


def resolve_runtime_config(harness: dict, project_root: Path) -> tuple[dict, Path]:
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


def run_runtime_checks(project_root: Path, harness: dict) -> list[dict]:
    checks: list[dict] = []
    if not harness.get("project") and not harness.get("runtime"):
        return [{"check": "harness_config", "pass": False, "detail": "No harness config"}]

    cfg, cwd = resolve_runtime_config(harness, project_root)
    for name, cmd, timeout in (
        ("test_command", cfg.get("test_cmd", ""), 180),
        ("lint_command", cfg.get("lint_cmd", ""), 120),
        ("build_command", cfg.get("build_cmd", ""), 300),
    ):
        if not cmd:
            continue
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
            )
            checks.append({
                "check": name,
                "command": cmd,
                "pass": result.returncode == 0,
                "exit_code": result.returncode,
                "output_snippet": (result.stdout or result.stderr or "")[:500],
            })
        except subprocess.TimeoutExpired:
            checks.append({"check": name, "command": cmd, "pass": False, "detail": f"timeout {timeout}s"})
        except Exception as exc:
            checks.append({"check": name, "command": cmd, "pass": False, "detail": str(exc)})

    health_url = cfg.get("health_url", "")
    if health_url:
        try:
            with urllib.request.urlopen(health_url, timeout=15) as resp:
                checks.append({"check": "health_url", "url": health_url, "pass": resp.status == 200})
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            checks.append({"check": "health_url", "url": health_url, "pass": False, "detail": str(exc)})

    return checks or [{"check": "runtime", "pass": False, "detail": "No runtime commands configured"}]


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
    checks = run_runtime_checks(project_root, harness)
    passed = len(checks) > 0 and all(c.get("pass") for c in checks)
    report = {
        "summary": {"passed": sum(1 for c in checks if c.get("pass")), "total": len(checks)},
        "checks": checks,
    }
    return {"pass": passed, "exit_code": 0 if passed else 1, "report": report}


def check_prerequisites(project_root: Path) -> list[str]:
    """v6.2: Check that prerequisites for inner loop are met."""
    errors = []
    goals_file = project_root / "goals" / "mvp.yaml"
    if not goals_file.exists():
        errors.append(f"goals/mvp.yaml not found — inner loop requires verifiable goals")
    harness_file = project_root / "harness-rules.yaml"
    if not harness_file.exists():
        errors.append(f"harness-rules.yaml not found — inner loop requires runtime config")
    return errors


def log_to_feedback(project_root: Path, iteration: int, signal: str, details: dict) -> None:
    """v6.2: Write iteration result to feedback.jsonl for cross-session memory."""
    fb = project_root / "feedback.jsonl"
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "inner-loop",
        "stage": "mvp",
        "iteration": iteration,
        "signal": signal,
        "details": details,
        "proposed_delta": f"inner-loop iter {iteration}: {signal}",
        "status": "recorded",
    }
    fb.parent.mkdir(parents=True, exist_ok=True)
    with open(fb, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_to_progress(project_root: Path, iteration: int, signal: str, observe_report: dict) -> None:
    """v6.2: Append iteration log to PROGRESS.md inner loop history."""
    progress = project_root / "PROGRESS.md"
    if not progress.exists():
        return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    summary = observe_report.get("report", {}).get("summary", {})
    passed = summary.get("passed", "?")
    total = summary.get("total", "?")
    line = f"| {iteration} | {now} | {signal} | {passed}/{total} | {'✅ PASS' if signal == 'pass' else '❌ FAIL'} |\n"

    # Append to inner loop history table if it exists
    content = progress.read_text(encoding="utf-8", errors="replace")
    if "内循环日志" in content or "Inner Loop" in content.lower():
        with open(progress, "a", encoding="utf-8") as f:
            f.write(line)


def escalate_to_harness(project_root: Path, reason: str) -> None:
    """v6.2: Write harness improvement proposal when inner loop exhausts iterations."""
    harness_improvements = project_root / "harness-improvements.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    content = f"""# Harness 改进提案

生成时间：{now}
触发原因：MVP 内循环 3 次迭代后仍 FAIL

## 问题分析

{reason}

## 建议改进（Medium risk — 需 retro 确认）

- [ ] 检查测试命令是否正确配置（harness-rules.yaml → runtime.test_cmd）
- [ ] 检查构建命令是否匹配实际技术栈
- [ ] 考虑是否需要调整 health_url 或增加超时时间
- [ ] 分析是否为 harness 配置问题 vs 代码质量问题

## 分类

| 风险等级 | 处理方式 |
|---------|---------|
| Low | 自动应用到 harness-rules.yaml |
| Medium | 写入 backlog，等待 retro 确认 |
| High | 需人工审批 |
"""
    harness_improvements.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="MVP inner loop driver (v9.1.0)")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--iteration", type=int, default=0, help="0 = auto increment")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-start", action="store_true", help="Skip prerequisite checks")
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

    # v6.2: Check prerequisites before starting
    if not args.force_start and iteration == 1:
        prereq_errors = check_prerequisites(project_root)
        if prereq_errors:
            report["action"] = "blocked"
            report["reason"] = "Prerequisites not met"
            report["errors"] = prereq_errors
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1

    if iteration > max_iter:
        report["action"] = "escalate_human"
        report["reason"] = f"Exceeded max_iterations ({max_iter})"
        # v6.2: Auto-generate harness improvement proposal
        escalate_to_harness(
            project_root,
            f"Inner loop exhausted {max_iter} iterations without passing all goals. "
            f"Last observe result: {state.get('last_signal', 'unknown')}"
        )
        report["harness_improvements_written"] = True
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

    # v6.2: Log to feedback.jsonl and PROGRESS.md
    log_to_feedback(project_root, iteration, signal, obs.get("report", {}))
    log_to_progress(project_root, iteration, signal, obs)

    if obs["pass"]:
        report["action"] = "exit_loop_g3"
    elif iteration >= max_iter:
        report["action"] = "escalate_human"
        escalate_to_harness(
            project_root,
            f"Iteration {iteration} failed. All {max_iter} attempts exhausted."
        )
        report["harness_improvements_written"] = True
    else:
        report["action"] = "adjust_and_retry"
        remaining = max_iter - iteration
        report["remaining_iterations"] = remaining

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if obs["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
