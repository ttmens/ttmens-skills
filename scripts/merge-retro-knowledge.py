#!/usr/bin/env python3
"""Merge retro insights into pipeline-knowledge/."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipelines" / "pm-idea-to-mvp" / "scripts"))
from pipeline_paths import resolve_pipeline_root

PIPELINE_VERSION = "6.1.0"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    retro = project_root / "05-retro.md"
    pipeline_root = resolve_pipeline_root()
    knowledge = pipeline_root / "pipeline-knowledge"
    knowledge.mkdir(exist_ok=True)
    patterns = knowledge / "patterns.md"

    if not retro.exists():
        print(json.dumps({"error": "05-retro.md missing"}, ensure_ascii=False))
        return 1

    text = retro.read_text(encoding="utf-8", errors="replace")
    bullets = re.findall(r"^[-*]\s+(.+)$", text, re.MULTILINE)
    existing = patterns.read_text(encoding="utf-8") if patterns.exists() else "# Patterns\n\n"
    added = 0
    for b in bullets[:10]:
        if b not in existing:
            existing += f"\n- {b}\n"
            added += 1
    patterns.write_text(existing, encoding="utf-8")

    # feedback.jsonl → evolution-notes append
    fb = project_root / "feedback.jsonl"
    evo = project_root / "evolution-notes.md"
    if fb.exists():
        evo_body = evo.read_text(encoding="utf-8") if evo.exists() else "# Evolution\n\n"
        for line in fb.read_text(encoding="utf-8").splitlines():
            if line.strip():
                evo_body += f"\n{line.strip()}\n"
        evo.write_text(evo_body, encoding="utf-8")

    print(json.dumps({"patterns_added": added, "pipeline_version": PIPELINE_VERSION}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
