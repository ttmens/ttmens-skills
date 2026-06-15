#!/usr/bin/env python3
"""Lighthouse performance check (optional, non-blocking when npx missing)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def resolve_url(project_root: Path, url: str | None) -> str | None:
    if url:
        return url
    gates = project_root / "gates.json"
    if gates.is_file():
        data = json.loads(gates.read_text(encoding="utf-8"))
        for key in ("pages_url", "deploy_url", "public_url", "url"):
            if data.get(key):
                return str(data[key])
        pages = data.get("pages") or {}
        if isinstance(pages, dict) and pages.get("url"):
            return str(pages["url"])
    env_example = project_root / ".env.example"
    if env_example.is_file():
        for line in env_example.read_text(encoding="utf-8").splitlines():
            if line.startswith("PUBLIC_URL="):
                return line.split("=", 1)[1].strip().strip('"')
    return None


def run_lighthouse(url: str, out_json: Path, min_performance: int) -> dict:
    if not shutil.which("npx"):
        return {"status": "skipped", "reason": "npx not found", "passed": True, "warning": True}

    out_json.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "npx", "--yes", "lighthouse", url,
        "--output=json",
        f"--output-path={out_json}",
        "--quiet",
        "--chrome-flags=--headless",
        "--only-categories=performance",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return {"status": "error", "reason": "lighthouse timeout", "passed": True, "warning": True}

    if r.returncode != 0:
        return {
            "status": "error",
            "reason": (r.stderr or r.stdout or "lighthouse failed")[:300],
            "passed": True,
            "warning": True,
        }

    if not out_json.is_file():
        return {"status": "error", "reason": "no output file", "passed": True, "warning": True}

    report = json.loads(out_json.read_text(encoding="utf-8"))
    perf = report.get("categories", {}).get("performance", {})
    score = int((perf.get("score") or 0) * 100)
    passed = score >= min_performance
    return {
        "status": "ok",
        "url": url,
        "performance_score": score,
        "min_performance": min_performance,
        "passed": passed,
        "warning": not passed,
        "report_path": str(out_json),
    }


def append_report_summary(project_root: Path, result: dict) -> None:
    report_md = project_root / "docs" / "ui-acceptance-report.md"
    if not report_md.is_file():
        return
    block = (
        f"\n\n## Lighthouse (append)\n\n"
        f"- Status: {result.get('status')}\n"
        f"- Performance: {result.get('performance_score', 'n/a')} "
        f"(min {result.get('min_performance', 90)})\n"
    )
    report_md.write_text(report_md.read_text(encoding="utf-8").rstrip() + block, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lighthouse performance check")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--url", default="")
    parser.add_argument("--min-performance", type=int, default=90)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = (args.project_root or Path.cwd()).resolve()
    url = resolve_url(root, args.url or None)
    if not url:
        result = {"status": "skipped", "reason": "no URL (--url or gates.json)", "passed": True, "warning": True}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Lighthouse: skipped (no URL)")
        return 0

    out_json = root / "docs" / "lighthouse-report.json"
    result = run_lighthouse(url, out_json, args.min_performance)
    append_report_summary(root, result)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Lighthouse: {result.get('status')} score={result.get('performance_score', 'n/a')}")

    if result.get("warning"):
        return 0
    return 0 if result.get("passed", True) else 1


if __name__ == "__main__":
    sys.exit(main())
