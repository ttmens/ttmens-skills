#!/usr/bin/env python3
"""Generate docs/SKILLS_CATALOG.md from marketplace.yaml and borrowed/manifest.yaml."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs" / "SKILLS_CATALOG.md"
MARKER_START = "<!-- AUTO:CATALOG -->"
MARKER_END = "<!-- /AUTO:CATALOG -->"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def render_catalog(marketplace: dict, manifest: dict) -> str:
    m = marketplace
    counts = m.get("counts", {})
    native_n = counts.get("native", 0)
    borrowed_n = counts.get("borrowed", 0)
    total = counts.get("total", native_n + borrowed_n)
    entry = m.get("pipeline", {}).get("entry", "pm-idea-to-mvp")
    stages = m.get("pipeline", {}).get("stages", [])
    gates = {"align": "G1", "spec": "G2", "mvp": "G3"}

    lines = [
        MARKER_START,
        "# Skills Catalog",
        "",
        "> Maintainer index — auto-generated. Reader-facing docs: [README.md](../README.md).",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"**Counts:** {native_n} native + {borrowed_n} borrowed = **{total}** core skills",
        "",
        "## Pipeline",
        "",
        f"Entry: `{entry}` — stages: {', '.join(stages)}",
        "",
        "| Stage | Gate |",
        "|-------|------|",
    ]
    for s in stages:
        lines.append(f"| {s} | {gates.get(s, '—')} |")

    lines.extend(["", "## Native skills (core)", ""])
    lines.append("| ID | Path | Role | Stages | Platforms | What | Use when |")
    lines.append("|----|------|------|--------|-----------|------|----------|")
    for e in m.get("skills", {}).get("native", []):
        st = ", ".join(e.get("stages", []))
        pl = ", ".join(e.get("platforms", []))
        what = e.get("what", "").replace("|", "\\|")
        when = e.get("use_when", "").replace("|", "\\|")
        lines.append(
            f"| `{e['id']}` | `{e['path']}` | {e.get('role', '')} | {st} | {pl} | {what} | {when} |"
        )

    lines.extend(["", "## Borrowed skills (core)", ""])
    lines.append("| Install as | Source | Stage | Platforms |")
    lines.append("|------------|--------|-------|-----------|")
    for e in manifest.get("skills", []):
        st = e.get("stage", "")
        pl = ", ".join(e.get("platforms", []))
        lines.append(f"| `{e.get('install_as', e['id'])}` | `{e.get('source', '')}` | {st} | {pl} |")

    profiles = m.get("profiles", {})
    if profiles:
        lines.extend(["", "## Optional profiles", ""])
        for pid, meta in profiles.items():
            label = meta.get("label", pid)
            skills = ", ".join(f"`{s}`" for s in meta.get("skills", []))
            lines.append(f"### {pid} — {label}")
            lines.append("")
            lines.append(f"Path: `{meta.get('path', '')}` — skills: {skills}")
            lines.append("")
            lines.append("Install: `./install.sh --profile {pid} --all`")
            lines.append("")

    lines.extend(["", "## Native by stage", ""])
    for stage in stages:
        hits = [
            e
            for e in m.get("skills", {}).get("native", [])
            if stage in e.get("stages", []) or "all" in e.get("stages", [])
        ]
        if not hits:
            continue
        lines.append(f"### {stage}")
        lines.append("")
        for e in hits:
            lines.append(f"- `{e['id']}` — `{e['path']}`")
        lines.append("")

    lines.extend(
        [
            "",
            "## Platforms",
            "",
            "| Platform | Global | Project | Docs |",
            "|----------|--------|---------|------|",
            "| Cursor | `~/.cursor/skills/` | `.cursor/skills/` | [cursor.md](platforms/cursor.md) |",
            "| Hermes | `~/.hermes/skills/` | — | [hermes.md](platforms/hermes.md) |",
            "| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` | [opencode.md](platforms/opencode.md) |",
            "",
            "## Vendor attribution",
            "",
            "Borrowed skills copy from `vendor/` at install. See [borrowed/ATTRIBUTION.md](../borrowed/ATTRIBUTION.md).",
            "",
            MARKER_END,
        ]
    )
    return "\n".join(lines)


def sync_write(marketplace: dict, manifest: dict) -> None:
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(render_catalog(marketplace, manifest), encoding="utf-8")
    print(f"Wrote {CATALOG}")


def sync_check(marketplace: dict, manifest: dict) -> int:
    if not CATALOG.exists():
        print(f"{CATALOG} missing; run with --write")
        return 1
    expected = render_catalog(marketplace, manifest)
    actual = CATALOG.read_text(encoding="utf-8")
    # Compare body between markers; timestamp line changes each run
    if MARKER_START not in actual or MARKER_END not in actual:
        print("SKILLS_CATALOG.md missing AUTO:CATALOG markers")
        return 1
    start = actual.index(MARKER_START)
    end = actual.index(MARKER_END) + len(MARKER_END)
    exp_start = expected.index(MARKER_START)
    exp_end = expected.index(MARKER_END) + len(MARKER_END)
    # Strip generated timestamp line for comparison
    def strip_ts(block: str) -> str:
        return "\n".join(
            ln for ln in block.splitlines() if not ln.startswith("Generated:")
        )

    if strip_ts(actual[start:end]) != strip_ts(expected[exp_start:exp_end]):
        print("SKILLS_CATALOG.md out of sync; run: python scripts/sync_readme.py --write")
        return 1
    print("SKILLS_CATALOG.md in sync")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    marketplace = load_yaml(ROOT / "marketplace.yaml")
    manifest = load_yaml(ROOT / "borrowed" / "manifest.yaml")
    if args.check:
        return sync_check(marketplace, manifest)
    sync_write(marketplace, manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
