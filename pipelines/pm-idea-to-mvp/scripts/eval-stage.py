#!/usr/bin/env python3
"""
eval-stage.py — Evaluate pipeline stage quality with rubric scoring.

Supports two modes:
  1. Default: Text-pattern rubric checks (v5.1 compatible)
  2. --runtime: Command-based rubric checks from rubrics/{stage}-runtime.json

Exit 0 if score >= threshold, 1 otherwise. Outputs JSON report.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root

PIPELINE_VERSION = "6.2.0"

# Default text-pattern rubrics (v5.1 compatible)
DEFAULT_RUBRICS = {
    "brief": {
        "threshold": 60,
        "criteria": [
            {"id": "B1", "description": "Has title/idea description", "pattern": r".{20,}", "weight": 20, "target": "00-brief.md"},
            {"id": "B2", "description": "Contains problem statement", "pattern": r"问题|problem|痛点|pain", "weight": 20, "target": "00-brief.md"},
            {"id": "B3", "description": "Contains target user", "pattern": r"用户|user|受众|audience", "weight": 20, "target": "00-brief.md"},
            {"id": "B4", "description": "Minimum length", "type": "min_lines", "min": 5, "weight": 20, "target": "00-brief.md"},
            {"id": "B5", "description": "Has success criteria", "pattern": r"成功|success|目标|goal|指标|metric", "weight": 20, "target": "00-brief.md"},
        ],
    },
    "align": {
        "threshold": 70,
        "criteria": [
            {"id": "A1", "description": "CONTEXT.md exists with content", "type": "min_lines", "min": 10, "weight": 25, "target": "CONTEXT.md"},
            {"id": "A2", "description": "Decisions documented", "type": "min_lines", "min": 5, "weight": 25, "target": "decisions.md"},
            {"id": "A3", "description": "Contains assumptions", "pattern": r"假设|assumption|前提|premise", "weight": 25, "target": "CONTEXT.md"},
            {"id": "A4", "description": "Contains constraints", "pattern": r"约束|constraint|限制|limit", "weight": 25, "target": "CONTEXT.md"},
        ],
    },
    "research": {
        "threshold": 75,
        "criteria": [
            {"id": "R1", "description": "Has ≥5 source URLs", "type": "url_count", "min": 5, "weight": 30, "target": "01-research.md"},
            {"id": "R2", "description": "Competitor analysis present", "pattern": r"竞品|competitor|对比|compared", "weight": 25, "target": "01-research.md"},
            {"id": "R3", "description": "Market analysis", "pattern": r"市场|market|规模|size| TAM|SAM|SOM", "weight": 20, "target": "01-research.md"},
            {"id": "R4", "description": "Minimum length", "type": "min_lines", "min": 20, "weight": 25, "target": "01-research.md"},
        ],
    },
    "analysis": {
        "threshold": 75,
        "criteria": [
            {"id": "AN1", "description": "Multiple options analyzed", "pattern": r"方案.{1,5}(A|B|C|一|二|三|1|2|3)|option.{1,5}[123]", "weight": 25, "target": "02-analysis.md"},
            {"id": "AN2", "description": "Recommendation present", "pattern": r"推荐|recommend|建议|suggest", "weight": 25, "target": "02-analysis.md"},
            {"id": "AN3", "description": "Risk assessment", "pattern": r"风险|risk|隐患|drawback", "weight": 25, "target": "02-analysis.md"},
            {"id": "AN4", "description": "Minimum length", "type": "min_lines", "min": 30, "weight": 25, "target": "02-analysis.md"},
        ],
    },
    "spec": {
        "threshold": 80,
        "criteria": [
            {"id": "S1", "description": "PRD exists", "type": "file_exists", "weight": 20, "target": "03-prd.md"},
            {"id": "S2", "description": "User journey exists", "type": "file_exists", "weight": 20, "target": "03b-user-journey.md"},
            {"id": "S3", "description": "User stories defined", "pattern": r"用户故事|user stor|作为.*我想|As a.*I want", "weight": 20, "target": "03-prd.md"},
            {"id": "S4", "description": "Acceptance criteria", "pattern": r"验收标准|acceptance|AC[：:]|Given.*When.*Then", "weight": 20, "target": "03-prd.md"},
            {"id": "S5", "description": "Task breakdown", "type": "file_exists", "weight": 20, "target": "openspec/tasks.md"},
        ],
    },
    "mvp": {
        "threshold": 70,
        "criteria": [
            {"id": "M1", "description": "MVP directory exists", "type": "dir_exists", "weight": 20, "target": "04-mvp"},
            {"id": "M2", "description": "README present", "type": "file_exists", "weight": 20, "target": "04-mvp/README.md"},
            {"id": "M3", "description": "Design tokens", "type": "file_exists", "weight": 20, "target": "04-mvp/DESIGN.md"},
            {"id": "M4", "description": "Has implementation code", "type": "dir_has_files", "min": 3, "weight": 20, "target": "04-mvp"},
            {"id": "M5", "description": "UX review present", "type": "file_exists", "weight": 20, "target": "04-mvp/UX-REVIEW.md"},
        ],
    },
    "ship": {
        "threshold": 80,
        "criteria": [
            {"id": "SH1", "description": "Runbook exists", "type": "min_lines", "min": 10, "weight": 25, "target": "RUNBOOK.md"},
            {"id": "SH2", "description": "Deploy instructions", "pattern": r"部署|deploy|发布|release", "weight": 25, "target": "RUNBOOK.md"},
            {"id": "SH3", "description": "Rollback plan", "pattern": r"回滚|rollback|恢复|recover", "weight": 25, "target": "RUNBOOK.md"},
            {"id": "SH4", "description": "Monitoring setup", "pattern": r"监控|monitor|告警|alert", "weight": 25, "target": "RUNBOOK.md"},
        ],
    },
    "operate": {
        "threshold": 70,
        "criteria": [
            {"id": "O1", "description": "Runbook has monitoring section", "pattern": r"监控|monitor|告警|alert|SLA", "weight": 30, "target": "RUNBOOK.md"},
            {"id": "O2", "description": "Incident response steps", "pattern": r"故障|incident|on-call|响应", "weight": 25, "target": "RUNBOOK.md"},
            {"id": "O3", "description": "Ops notes or runbook updates", "type": "file_exists", "weight": 25, "target": "RUNBOOK.md"},
            {"id": "O4", "description": "Health check documented", "pattern": r"health|健康检查|探活", "weight": 20, "target": "RUNBOOK.md"},
        ],
    },
    "grow": {
        "threshold": 70,
        "criteria": [
            {"id": "G1", "description": "Growth doc exists", "type": "min_lines", "min": 15, "weight": 25, "target": "06-growth.md"},
            {"id": "G2", "description": "North star metric", "pattern": r"北极星|north.star|核心指标|key.metric", "weight": 25, "target": "06-growth.md"},
            {"id": "G3", "description": "Growth channels", "pattern": r"渠道|channel|获客|acquisition", "weight": 25, "target": "06-growth.md"},
            {"id": "G4", "description": "Growth strategy", "pattern": r"策略|strategy|计划|plan", "weight": 25, "target": "06-growth.md"},
        ],
    },
    "retro": {
        "threshold": 75,
        "criteria": [
            {"id": "RE1", "description": "Retro doc exists", "type": "min_lines", "min": 15, "weight": 20, "target": "05-retro.md"},
            {"id": "RE2", "description": "Lessons learned", "pattern": r"教训|lesson|学到|learned|反思|reflect", "weight": 20, "target": "05-retro.md"},
            {"id": "RE3", "description": "Skill proposals", "pattern": r"skill_patch_proposals|技能.*改进|skill.*improve", "weight": 20, "target": "05-retro.md"},
            {"id": "RE4", "description": "Timing analysis", "pattern": r"时间|time|耗时|duration|阶段.*时间", "weight": 20, "target": "05-retro.md"},
            {"id": "RE5", "description": "Evolution notes", "pattern": r"进化|evolution|改进|improvement", "weight": 20, "target": "05-retro.md"},
        ],
    },
}


def load_runtime_rubric(stage: str, project_root: Path) -> dict | None:
    """Load runtime rubric from rubrics/{stage}-runtime.json."""
    rubric_path = project_root / "rubrics" / f"{stage}-runtime.json"
    if not rubric_path.exists():
        return None
    try:
        return json.loads(rubric_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return None


def evaluate_text_criterion(criterion: dict, project_root: Path) -> dict:
    """Evaluate a single text-pattern criterion."""
    cid = criterion.get("id", "?")
    ctype = criterion.get("type", "pattern")
    target = criterion.get("target", "")
    weight = criterion.get("weight", 10)
    description = criterion.get("description", "")

    result = {
        "id": cid,
        "description": description,
        "weight": weight,
        "score": 0,
        "max_score": weight,
        "pass": False,
    }

    target_path = project_root / target

    if ctype == "pattern":
        pattern = criterion.get("pattern", "")
        if not target_path.exists():
            result["detail"] = f"File not found: {target}"
            return result
        content = target_path.read_text(encoding="utf-8", errors="replace")
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            result["score"] = weight
            result["pass"] = True
            result["detail"] = f"Pattern matched in {target}"
        else:
            result["detail"] = f"Pattern NOT matched in {target}"

    elif ctype == "file_exists":
        if target_path.exists():
            result["score"] = weight
            result["pass"] = True
            result["detail"] = f"File exists: {target}"
        else:
            result["detail"] = f"File NOT found: {target}"

    elif ctype == "dir_exists":
        if target_path.exists() and target_path.is_dir():
            result["score"] = weight
            result["pass"] = True
            result["detail"] = f"Directory exists: {target}"
        else:
            result["detail"] = f"Directory NOT found: {target}"

    elif ctype == "min_lines":
        min_lines = criterion.get("min", 10)
        if not target_path.exists():
            result["detail"] = f"File not found: {target}"
            return result
        content = target_path.read_text(encoding="utf-8", errors="replace")
        lines = [l for l in content.splitlines() if l.strip()]
        if len(lines) >= min_lines:
            result["score"] = weight
            result["pass"] = True
            result["detail"] = f"Has {len(lines)} lines (min: {min_lines})"
        else:
            result["detail"] = f"Only {len(lines)} lines (min: {min_lines})"

    elif ctype == "url_count":
        min_urls = criterion.get("min", 5)
        if not target_path.exists():
            result["detail"] = f"File not found: {target}"
            return result
        content = target_path.read_text(encoding="utf-8", errors="replace")
        urls = set(re.findall(r'https?://[^\s\)>\]\"\']+', content))
        if len(urls) >= min_urls:
            result["score"] = weight
            result["pass"] = True
            result["detail"] = f"Has {len(urls)} URLs (min: {min_urls})"
        else:
            result["detail"] = f"Only {len(urls)} URLs (min: {min_urls})"

    elif ctype == "dir_has_files":
        min_files = criterion.get("min", 3)
        if not target_path.exists() or not target_path.is_dir():
            result["detail"] = f"Directory not found: {target}"
            return result
        files = [f for f in target_path.rglob("*") if f.is_file()]
        if len(files) >= min_files:
            result["score"] = weight
            result["pass"] = True
            result["detail"] = f"Has {len(files)} files (min: {min_files})"
        else:
            result["detail"] = f"Only {len(files)} files (min: {min_files})"

    else:
        result["detail"] = f"Unknown criterion type: {ctype}"

    return result


def evaluate_runtime_criterion(criterion: dict, project_root: Path) -> dict:
    """Evaluate a runtime (command-based) criterion."""
    cid = criterion.get("id", "?")
    ctype = criterion.get("type", "command")
    weight = criterion.get("weight", 10)
    description = criterion.get("description", "")

    result = {
        "id": cid,
        "description": description,
        "weight": weight,
        "score": 0,
        "max_score": weight,
        "pass": False,
    }

    if ctype == "command":
        command = criterion.get("command", "")
        workdir = criterion.get("workdir", "")
        cwd = project_root / workdir if workdir else project_root

        if not command:
            result["detail"] = "No command specified"
            return result

        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=criterion.get("timeout", 120),
            )
            if proc.returncode == 0:
                result["score"] = weight
                result["pass"] = True
                result["detail"] = f"Command passed: {command}"
            else:
                result["detail"] = f"Command failed (exit {proc.returncode}): {command}"
                result["output"] = (proc.stderr or proc.stdout or "")[:300]
        except subprocess.TimeoutExpired:
            result["detail"] = f"Command timed out: {command}"
        except Exception as e:
            result["detail"] = f"Command error: {e}"

    elif ctype == "health_check":
        url = criterion.get("url", "")
        if not url:
            result["detail"] = "No URL specified"
            return result
        try:
            import urllib.request
            import urllib.error
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                if 200 <= status < 400:
                    result["score"] = weight
                    result["pass"] = True
                    result["detail"] = f"Health check passed: {url} (status {status})"
                else:
                    result["detail"] = f"Health check failed: {url} (status {status})"
        except Exception as e:
            result["detail"] = f"Health check error: {e}"

    elif ctype == "file_exists":
        target = criterion.get("target", "")
        target_path = project_root / target
        if target_path.exists():
            result["score"] = weight
            result["pass"] = True
            result["detail"] = f"File exists: {target}"
        else:
            result["detail"] = f"File NOT found: {target}"

    elif ctype == "output_contains":
        command = criterion.get("command", "")
        expected = criterion.get("pattern", criterion.get("expected", ""))
        workdir = criterion.get("workdir", "")
        cwd = project_root / workdir if workdir else project_root

        try:
            proc = subprocess.run(
                command, shell=True, cwd=str(cwd),
                capture_output=True, text=True, timeout=120,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            if re.search(expected, output, re.IGNORECASE):
                result["score"] = weight
                result["pass"] = True
                result["detail"] = f"Output contains expected pattern"
            else:
                result["detail"] = f"Output does NOT contain expected pattern: {expected}"
        except Exception as e:
            result["detail"] = f"Command error: {e}"

    else:
        result["detail"] = f"Unknown runtime criterion type: {ctype}"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate pipeline stage quality with rubric scoring"
    )
    parser.add_argument(
        "--stage", required=True,
        help="Stage to evaluate"
    )
    parser.add_argument(
        "--project-root", required=True,
        help="Project root directory"
    )
    parser.add_argument(
        "--runtime", action="store_true",
        help="Use runtime rubric from rubrics/{stage}-runtime.json"
    )
    parser.add_argument(
        "--rubric-file",
        help="Override rubric file path"
    )
    parser.add_argument(
        "--threshold", type=int,
        help="Override pass threshold (0-100)"
    )

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    stage = args.stage

    # Determine rubric
    rubric = None
    rubric_source = "default"

    if args.runtime:
        rubric = load_runtime_rubric(stage, project_root)
        if rubric:
            rubric_source = f"rubrics/{stage}-runtime.json"
        else:
            # Fall back to default rubric with a warning
            rubric = DEFAULT_RUBRICS.get(stage)
            rubric_source = "default (runtime rubric not found)"

    if args.rubric_file:
        rubric_path = Path(args.rubric_file)
        if rubric_path.exists():
            try:
                rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
                rubric_source = str(rubric_path)
            except json.JSONDecodeError:
                pass

    if not rubric:
        rubric = DEFAULT_RUBRICS.get(stage)
        rubric_source = "default"

    if not rubric:
        report = {
            "pipeline_version": PIPELINE_VERSION,
            "stage": stage,
            "error": f"No rubric found for stage: {stage}",
            "score": 0,
            "threshold": 0,
            "passed": False,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(1)

    threshold = args.threshold or rubric.get("threshold", 70)
    criteria = rubric.get("criteria", [])

    # Evaluate criteria
    results = []
    total_score = 0
    max_score = 0

    for criterion in criteria:
        if args.runtime and criterion.get("type") in ("command", "health_check", "output_contains"):
            result = evaluate_runtime_criterion(criterion, project_root)
        else:
            result = evaluate_text_criterion(criterion, project_root)
        results.append(result)
        total_score += result["score"]
        max_score += result["max_score"]

    # Calculate percentage score
    score_pct = round(total_score / max_score * 100, 1) if max_score > 0 else 0
    passed = score_pct >= threshold

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "stage": stage,
        "project_root": str(project_root),
        "rubric_source": rubric_source,
        "mode": "runtime" if args.runtime else "text_pattern",
        "criteria": results,
        "score": total_score,
        "max_score": max_score,
        "score_percent": score_pct,
        "threshold": threshold,
        "passed": passed,
        "summary": {
            "total_criteria": len(criteria),
            "passed_criteria": sum(1 for r in results if r["pass"]),
            "failed_criteria": sum(1 for r in results if not r["pass"]),
        },
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
