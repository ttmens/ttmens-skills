#!/usr/bin/env python3
"""Feishu notification for pm-idea-to-mvp stage events."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipelines" / "pm-idea-to-mvp" / "scripts"))
from pipeline_version import PIPELINE_VERSION  # noqa: E402


def build_message(stage: str, status: str, project_root: str, task_id: str, extra: str = "") -> str:
    slug = Path(project_root).name.removeprefix("pm-")
    lines = [
        f"[pm-idea-to-mvp v{PIPELINE_VERSION}]",
        f"阶段: {stage}",
        f"状态: {status}",
        f"项目: pm-{slug}",
        f"任务: {task_id or 'n/a'}",
    ]
    if "checkpoint" in status.lower() or "block" in status.lower():
        lines.append("")
        lines.append("⏸ 人工卡点 — 确认产物后执行:")
        lines.append(f"  hermes kanban unblock {task_id}")
    if extra:
        lines.append("")
        lines.append(extra)
    return "\n".join(lines)


def send_webhook(text: str) -> dict:
    webhook = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    payload = {"msg_type": "text", "content": {"text": text}}
    report: dict = {"pipeline_version": PIPELINE_VERSION, "sent": False}
    if not webhook:
        report["detail"] = "FEISHU_WEBHOOK_URL not set; logged only"
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return report
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        report["sent"] = resp.status == 200
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Feishu notify for pm-idea-to-mvp")
    parser.add_argument("--stage", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--extra", default="")
    parser.add_argument("--heartbeat", action="store_true")
    args = parser.parse_args()

    text = build_message(args.stage, args.status, args.project_root, args.task_id, args.extra)
    if args.heartbeat:
        text = "💓 Kanban 进度\n" + text
    report = send_webhook(text)
    report["message_preview"] = text[:500]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
