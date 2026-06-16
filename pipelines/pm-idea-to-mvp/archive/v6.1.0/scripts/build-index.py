#!/usr/bin/env python3
"""Build pipeline index page listing all ttmens/pm-* repos."""
from __future__ import annotations

import html
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from github_helpers import GITHUB_OWNER, list_pm_repos, pages_url, repo_url  # noqa: E402


def build_index_html(repos: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = []
    for r in repos:
        name = r["name"]
        if name == "pm-pipeline-index":
            continue
        desc = html.escape(r.get("description") or "")
        updated = (r.get("updated_at") or "")[:10]
        rows.append(
            f"<tr><td><a href=\"{html.escape(pages_url(name))}\">{html.escape(name)}</a></td>"
            f"<td><a href=\"{html.escape(repo_url(name))}\">repo</a></td>"
            f"<td>{desc}</td><td>{updated}</td></tr>"
        )
    body = "\n".join(rows) or "<tr><td colspan='4'><em>No pm-* repos yet.</em></td></tr>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>PM Pipeline Index</title>
<style>body{{font-family:system-ui,sans-serif;background:#0f1419;color:#e7ecf3;padding:16px;max-width:960px;margin:auto}}
table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #2b3b52;padding:10px;text-align:left}}
a{{color:#6cb6ff}}</style></head><body>
<h1>PM Pipeline — 想法索引</h1>
<p>Owner: {html.escape(GITHUB_OWNER)} · Updated: {now}</p>
<table><thead><tr><th>Project</th><th>GitHub</th><th>Description</th><th>Updated</th></tr></thead>
<tbody>{body}</tbody></table></body></html>"""


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output docs/index.html path")
    args = parser.parse_args()
    repos = list_pm_repos()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_index_html(repos), encoding="utf-8")
    print(f"Wrote {out} ({len(repos)} repos)")


if __name__ == "__main__":
    main()
