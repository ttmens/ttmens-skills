#!/usr/bin/env python3
"""Generate GitHub Pages index.html stage report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_VERSION = "6.1.0"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    gates = {}
    gp = root / "gates.json"
    if gp.exists():
        gates = json.loads(gp.read_text(encoding="utf-8"))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = ""
    for stage, data in gates.items():
        if isinstance(data, dict) and "status" in data:
            rows += f"<tr><td>{stage}</td><td>{data.get('status','?')}</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>pm pipeline report</title>
<style>body{{font-family:system-ui;max-width:800px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:.5rem}}</style></head>
<body><h1>Pipeline Report</h1><p>Updated: {now}</p>
<table><tr><th>Stage</th><th>Status</th></tr>{rows or '<tr><td colspan=2>暂无 gates.json 数据</td></tr>'}
</table></body></html>"""
    out = docs / "index.html"
    out.write_text(html, encoding="utf-8")
    print(json.dumps({"written": str(out), "pipeline_version": PIPELINE_VERSION}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
