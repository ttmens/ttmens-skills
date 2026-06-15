#!/usr/bin/env python3
"""Merge retro evolution notes into pipeline-knowledge/ (structured sections)."""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_KNOWLEDGE = Path(__file__).resolve().parent.parent / "pipeline-knowledge"


def extract_section(text: str, heading: str) -> str:
    pattern = rf"##\s*{re.escape(heading)}[^\n]*\n(.*?)(?=\n##\s|\Z)"
    m = re.search(pattern, text, re.S | re.I)
    return m.group(1).strip() if m else ""


def append_unique(path: Path, slug: str, content: str) -> bool:
    if not content.strip():
        return False
    existing = path.read_text(encoding="utf-8") if path.exists() else f"# {path.stem.title()}\n\n"
    marker = f"<!-- run:{slug} -->"
    if marker in existing:
        return False
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    block = f"\n\n{marker}\n### {slug} ({stamp})\n\n{content.strip()}\n"
    path.write_text(existing.rstrip() + block + "\n", encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge retro knowledge into pipeline-knowledge/")
    parser.add_argument("--run", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run).resolve()
    slug = run_dir.name.replace("pm-", "", 1)
    retro = (run_dir / "05-retro.md").read_text(encoding="utf-8") if (run_dir / "05-retro.md").exists() else ""
    if not retro.strip():
        print("No 05-retro.md — skip")
        raise SystemExit(0)

    hits = extract_section(retro, "Hits") or extract_section(retro, "Skill effectiveness")
    misses = extract_section(retro, "Misses") or extract_section(retro, "Anti-patterns")
    evolution = extract_section(retro, "Evolution")

    PIPELINE_KNOWLEDGE.mkdir(parents=True, exist_ok=True)
    changed = []
    if append_unique(PIPELINE_KNOWLEDGE / "patterns.md", slug, hits or evolution):
        changed.append("patterns.md")
    if append_unique(PIPELINE_KNOWLEDGE / "anti-patterns.md", slug, misses):
        changed.append("anti-patterns.md")

    print(f"Merged retro for {slug}: {changed or 'no new sections'}")


if __name__ == "__main__":
    main()
