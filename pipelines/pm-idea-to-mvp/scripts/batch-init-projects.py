#!/usr/bin/env python3
"""Batch init-project.py for all pm-* directories under PROJECTS_ROOT."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_paths import resolve_projects_root  # noqa: E402

INIT = SCRIPT_DIR / "init-project.py"
PROJECTS_ROOT = resolve_projects_root()


def main() -> int:
    results: list[dict] = []
    for proj in sorted(PROJECTS_ROOT.glob("pm-*")):
        if not proj.is_dir():
            continue
        slug = proj.name.removeprefix("pm-")
        proc = subprocess.run(
            [sys.executable, str(INIT), "--project-root", str(proj), "--slug", slug, "--json"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        results.append(
            {
                "slug": slug,
                "ok": proc.returncode == 0,
                "stdout": (proc.stdout or "")[-500:],
                "stderr": (proc.stderr or "")[-300:],
            }
        )
    ok = sum(1 for r in results if r["ok"])
    print(f"init complete: {ok}/{len(results)} projects under {PROJECTS_ROOT}")
    for r in results:
        status = "OK" if r["ok"] else "FAIL"
        print(f"  [{status}] pm-{r['slug']}")
        if not r["ok"] and r["stderr"]:
            print(f"       {r['stderr'].strip()[:200]}")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
