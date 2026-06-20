#!/usr/bin/env python3
"""
consume-feedback.py — Parse and summarize feedback.jsonl for retro stage.

v6.2: Closes the feedback loop — feedback.jsonl was write-only, now consumed.
Generates a summary report and marks entries as consumed.

Usage:
  python consume-feedback.py --project-root <path> [--json] [--write]
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consume feedback.jsonl and generate retro summary (v9.1.0)"
    )
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--write", action="store_true",
                        help="Append consumption marker to feedback.jsonl")
    parser.add_argument("--append-retro", action="store_true",
                        help="Append summary section to 05-retro.md")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    entries = load_feedback(project_root)
    summary = summarize(entries)

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "project_root": str(project_root),
        "feedback_summary": summary,
    }

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
