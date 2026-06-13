#!/usr/bin/env python3
"""Feishu stage notification (stub — set FEISHU_WEBHOOK_URL)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

PIPELINE_VERSION = "6.1.0"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--task-id", default="")
    args = parser.parse_args()

    webhook = os.environ.get("FEISHU_WEBHOOK_URL", "")
    payload = {
        "msg_type": "text",
        "content": {
            "text": f"[pm-idea-to-mvp] {args.stage} {args.status}\nproject: {args.project_root}\ntask: {args.task_id or 'n/a'}",
        },
    }
    report = {"pipeline_version": PIPELINE_VERSION, "sent": False}
    if webhook:
        req = urllib.request.Request(
            webhook,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            report["sent"] = resp.status == 200
    else:
        report["detail"] = "FEISHU_WEBHOOK_URL not set; logged only"
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
