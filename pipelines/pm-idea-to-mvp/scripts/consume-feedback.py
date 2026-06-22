#!/usr/bin/env python3
"""
consume-feedback.py — Parse and summarize feedback.jsonl for retro stage.

v9.2: Added pattern detection for outer loop automation.
v6.2: Closes the feedback loop — feedback.jsonl was write-only, now consumed.
Generates a summary report and marks entries as consumed.

Usage:
  python consume-feedback.py --project-root <path> [--json] [--write] [--pattern-detection]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root

from pipeline_version import PIPELINE_VERSION


def load_feedback(project_root: Path) -> list[dict]:
    """Load all feedback entries from feedback.jsonl."""
    fb_path = project_root / "feedback.jsonl"
    if not fb_path.exists():
        return []
    entries = []
    for line in fb_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def summarize(entries: list[dict]) -> dict:
    """Generate summary statistics from feedback entries."""
    if not entries:
        return {
            "total": 0,
            "by_stage": {},
            "by_source": {},
            "by_signal": {},
            "by_status": {},
            "pending_items": [],
            "auto_applied": [],
        }

    by_stage = Counter()
    by_source = Counter()
    by_status = Counter()
    pending = []
    auto_applied = []

    for e in entries:
        by_stage[e.get("stage", "unknown")] += 1
        by_source[e.get("source", "unknown")] += 1
        by_status[e.get("status", "unknown")] += 1

        if e.get("status") == "pending":
            pending.append({
                "ts": e.get("ts", ""),
                "stage": e.get("stage", ""),
                "signal": e.get("signal", ""),
                "proposed_delta": e.get("proposed_delta", ""),
            })
        elif e.get("status") in ("auto-applied", "applied"):
            auto_applied.append({
                "ts": e.get("ts", ""),
                "stage": e.get("stage", ""),
                "signal": e.get("signal", ""),
            })

    return {
        "total": len(entries),
        "by_stage": dict(by_stage),
        "by_source": dict(by_source),
        "by_status": dict(by_status),
        "pending_items": pending,
        "auto_applied": auto_applied,
    }


def generate_retro_section(summary: dict) -> str:
    """Generate markdown section for 05-retro.md from feedback summary."""
    lines = [
        "## 反馈闭环摘要（自动生成 by consume-feedback.py）\n",
        f"**生成时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')}\n",
        f"**反馈总数**: {summary['total']}\n",
    ]

    if summary["by_stage"]:
        lines.append("\n### 按阶段分布\n")
        lines.append("| 阶段 | 数量 |")
        lines.append("|------|------|")
        for stage, count in sorted(summary["by_stage"].items()):
            lines.append(f"| {stage} | {count} |")

    if summary["by_status"]:
        lines.append("\n### 按状态分布\n")
        lines.append("| 状态 | 数量 |")
        lines.append("|------|------|")
        for status, count in sorted(summary["by_status"].items()):
            lines.append(f"| {status} | {count} |")

    if summary["pending_items"]:
        lines.append("\n### 待处理项\n")
        for item in summary["pending_items"]:
            lines.append(f"- [{item['stage']}] {item['signal']}")
            if item.get("proposed_delta"):
                lines.append(f"  - 建议: {item['proposed_delta']}")

    if summary["auto_applied"]:
        lines.append("\n### 已自动应用\n")
        for item in summary["auto_applied"]:
            lines.append(f"- ✅ [{item['stage']}] {item['signal']}")

    return "\n".join(lines)


def mark_consumed(project_root: Path) -> None:
    """Append a consumption marker to feedback.jsonl."""
    fb_path = project_root / "feedback.jsonl"
    marker = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "consume-feedback",
        "stage": "retro",
        "signal": "feedback consumed by retro stage",
        "status": "consumed",
    }
    with open(fb_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(marker, ensure_ascii=False) + "\n")


def detect_patterns(entries: list[dict]) -> list[dict]:
    """
    Detect repeated failure patterns (≥3 similar failures).
    
    Returns list of detected patterns with:
    - pattern: description of the pattern
    - count: number of occurrences
    - entries: list of matching feedback entries
    - suggested_rule: proposed rule to add to agent-behavior-code.md
    """
    if not entries:
        return []
    
    # Group entries by signal (failure type)
    signal_groups = {}
    for e in entries:
        signal = e.get("signal", "")
        if not signal or e.get("status") in ("resolved", "consumed"):
            continue
        
        # Normalize signal for grouping (remove specific details)
        normalized = signal.lower()
        # Extract key pattern (first 50 chars or first sentence)
        key = normalized[:50].split(".")[0].split(",")[0].strip()
        
        if key not in signal_groups:
            signal_groups[key] = []
        signal_groups[key].append(e)
    
    # Find patterns with ≥3 occurrences
    patterns = []
    for key, group in signal_groups.items():
        if len(group) >= 3:
            # Generate suggested rule
            stages = list(set(e.get("stage", "unknown") for e in group))
            suggested_rule = f"避免重复失败：{key}（出现 {len(group)} 次，阶段：{', '.join(stages)}）"
            
            patterns.append({
                "pattern": key,
                "count": len(group),
                "stages": stages,
                "entries": group,
                "suggested_rule": suggested_rule,
            })
    
    # Sort by count (descending)
    patterns.sort(key=lambda p: p["count"], reverse=True)
    return patterns


def generate_patterns_report(patterns: list[dict]) -> str:
    """Generate markdown report for auto-detected patterns."""
    lines = [
        "# 自动检测的失败模式\n",
        f"**生成时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')}\n",
        f"**检测到的模式数**: {len(patterns)}\n",
        "\n---\n",
    ]
    
    if not patterns:
        lines.append("\n✅ 未检测到重复失败模式（阈值：≥3 次相似失败）\n")
        return "\n".join(lines)
    
    lines.append("\n## 检测到的模式\n")
    
    for i, pattern in enumerate(patterns, 1):
        lines.append(f"\n### 模式 {i}: {pattern['pattern']}\n")
        lines.append(f"- **出现次数**: {pattern['count']}")
        lines.append(f"- **涉及阶段**: {', '.join(pattern['stages'])}")
        lines.append(f"- **建议规则**: {pattern['suggested_rule']}")
        
        lines.append("\n**相关反馈记录**:\n")
        for e in pattern["entries"][:5]:  # Show first 5 entries
            lines.append(f"- [{e.get('ts', '')}] [{e.get('stage', '')}] {e.get('signal', '')}")
            if e.get("proposed_delta"):
                lines.append(f"  - 建议: {e.get('proposed_delta')}")
    
    lines.append("\n---\n")
    lines.append("\n## 下一步行动\n")
    lines.append("1. 人工确认这些模式是否有效")
    lines.append("2. 确认后，将建议规则添加到 `references/agent-behavior-code.md`")
    lines.append("3. 更新相关技能的 SKILL.md")
    
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consume feedback.jsonl and generate retro summary (v9.2.0)"
    )
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--write", action="store_true",
                        help="Append consumption marker to feedback.jsonl")
    parser.add_argument("--append-retro", action="store_true",
                        help="Append summary section to 05-retro.md")
    parser.add_argument("--pattern-detection", action="store_true",
                        help="Detect repeated failure patterns and generate auto-detected-patterns.md")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    entries = load_feedback(project_root)
    summary = summarize(entries)

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "project_root": str(project_root),
        "feedback_summary": summary,
    }

    # Pattern detection (v9.2)
    if args.pattern_detection:
        patterns = detect_patterns(entries)
        patterns_report = generate_patterns_report(patterns)
        
        # Write to auto-detected-patterns.md
        patterns_path = project_root / "auto-detected-patterns.md"
        with open(patterns_path, "w", encoding="utf-8") as f:
            f.write(patterns_report)
        
        report["pattern_detection"] = {
            "patterns_found": len(patterns),
            "patterns_file": str(patterns_path),
        }
        
        if not args.json:
            print(f"\n🔍 Pattern Detection:")
            print(f"  Detected {len(patterns)} repeated failure patterns")
            print(f"  Report written to: {patterns_path}")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Feedback Summary: {summary['total']} entries")
        print(f"  By stage: {summary['by_stage']}")
        print(f"  By status: {summary['by_status']}")
        if summary["pending_items"]:
            print(f"  Pending: {len(summary['pending_items'])} items")
        if summary["auto_applied"]:
            print(f"  Auto-applied: {len(summary['auto_applied'])} items")

    if args.write:
        mark_consumed(project_root)
        if not args.json:
            print("  ✅ Consumption marker written to feedback.jsonl")

    if args.append_retro:
        retro_path = project_root / "05-retro.md"
        if retro_path.exists():
            section = generate_retro_section(summary)
            with open(retro_path, "a", encoding="utf-8") as f:
                f.write("\n\n" + section + "\n")
            if not args.json:
                print("  ✅ Summary appended to 05-retro.md")
        else:
            if not args.json:
                print("  ⚠️ 05-retro.md not found, skipping append")

    return 0


if __name__ == "__main__":
    sys.exit(main())
