#!/usr/bin/env python3
"""Validate ttmens-skills marketplace, native paths, and borrowed vendor refs."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def load_yaml(path: Path) -> dict:
    if not path.exists():
        err(f"Missing: {path}")
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def check_skill_md(path: Path, label: str) -> None:
    skill = path / "SKILL.md" if path.is_dir() else path
    if not skill.exists():
        err(f"{label}: no SKILL.md at {path}")
        return
    text = skill.read_text(encoding="utf-8-sig")
    if not text.lstrip().startswith("---"):
        err(f"{label}: SKILL.md missing frontmatter")
        return
    end = text.find("---", 3)
    if end < 0:
        err(f"{label}: unclosed frontmatter")
        return
    fm = text[3:end]
    if "name:" not in fm:
        err(f"{label}: frontmatter missing name")
    if "description:" not in fm:
        err(f"{label}: frontmatter missing description")


def main() -> int:
    marketplace = load_yaml(ROOT / "marketplace.yaml")
    platforms = load_yaml(ROOT / "platforms.yaml")
    manifest = load_yaml(ROOT / "borrowed" / "manifest.yaml")

    if not platforms.get("platforms"):
        err("platforms.yaml: empty platforms")

    for entry in marketplace.get("skills", {}).get("native", []):
        p = ROOT / entry["path"]
        check_skill_md(p, f"native:{entry['id']}")

    for entry in manifest.get("skills", []):
        source = entry.get("source", "")
        if source.startswith("phuryn/"):
            base = ROOT / manifest["sources"]["phuryn"]["path"]
            rel = source[len("phuryn/") :]
        elif source.startswith("anthropic/"):
            base = ROOT / manifest["sources"]["anthropic"]["path"]
            rel = source[len("anthropic/") :]
        else:
            err(f"borrowed:{entry['id']}: unknown source prefix")
            continue
        src = base / rel
        if entry.get("type") == "command":
            if not src.exists():
                err(f"borrowed:{entry['id']}: missing command {src}")
        else:
            check_skill_md(src, f"borrowed:{entry['id']}")

    profile_paths = {
        "obsidian": [
            "profiles/obsidian/obsidian-todo-manager",
            "profiles/obsidian/obsidian-deepen-review",
            "profiles/obsidian/obsidian-note-summarizer",
        ],
        "deep-research": ["profiles/deep-research/industry-benchmark"],
        "hermes": [
            "profiles/hermes-plan/plan",
            "profiles/hermes-opencode/opencode",
        ],
    }
    for profile, paths in profile_paths.items():
        if profile not in marketplace.get("profiles", {}):
            err(f"profiles: {profile} in validator but missing from marketplace.yaml")
        for rel in paths:
            check_skill_md(ROOT / rel, f"profile:{profile}:{Path(rel).name}")

    # Count consistency
    native_count = len(marketplace.get("skills", {}).get("native", []))
    borrowed_count = len(manifest.get("skills", []))
    counts = marketplace.get("counts", {})
    if counts.get("native") != native_count:
        err(f"counts.native={counts.get('native')} but found {native_count} native skills")
    if counts.get("borrowed") != borrowed_count:
        err(f"counts.borrowed={counts.get('borrowed')} but found {borrowed_count} borrowed skills")
    if counts.get("total") != native_count + borrowed_count:
        err(f"counts.total mismatch: expected {native_count + borrowed_count}")

    if ERRORS:
        print("VALIDATION FAILED:")
        for e in ERRORS:
            print(f"  - {e}")
        return 1
    print(f"OK: {native_count} native + {borrowed_count} borrowed skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
