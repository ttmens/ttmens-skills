#!/usr/bin/env python3
"""Install ttmens-skills to Cursor, Hermes, and OpenCode skill directories."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

PROFILE_PATHS = {
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


def expand_home(path: str) -> Path:
    return Path(os.path.expanduser(path))


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def skill_dirs_from_marketplace(marketplace: dict) -> list[tuple[str, Path]]:
    items: list[tuple[str, Path]] = []
    for entry in marketplace.get("skills", {}).get("native", []):
        items.append((entry["id"], ROOT / entry["path"]))
    return items


def profile_skill_dirs(profile: str) -> list[tuple[str, Path]]:
    paths = PROFILE_PATHS.get(profile, [])
    return [(Path(p).name, ROOT / p) for p in paths]


def platform_dest(platform: str, platforms: dict, project: Path | None) -> Path:
    cfg = platforms["platforms"][platform]
    if project and platform in ("cursor", "opencode"):
        return project / cfg["project_dir"].lstrip("./")
    return expand_home(cfg["global_dir"])


def copy_skill_tree(src: Path, dest: Path, mode: str) -> None:
    if not src.exists():
        print(f"  skip missing: {src}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if dest.is_symlink():
            dest.unlink()
        elif dest.is_dir():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    if mode == "link" and os.name != "nt":
        dest.symlink_to(src.resolve())
        print(f"  link {src.relative_to(ROOT)} -> {dest}")
    else:
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)
        print(f"  copy {src.relative_to(ROOT)} -> {dest}")


def install_command_as_skill(cmd_file: Path, dest: Path, install_as: str, description: str = "") -> None:
    dest.mkdir(parents=True, exist_ok=True)
    body = cmd_file.read_text(encoding="utf-8") if cmd_file.exists() else ""
    if not description:
        m = re.search(r"^description:\s*(.+)$", body, re.MULTILINE)
        description = m.group(1).strip() if m else install_as
    skill_md = f"""---
name: {install_as}
description: "{description}"
source: borrowed
---

# {install_as}

Imported command workflow from vendor.

{body}
"""
    (dest / "SKILL.md").write_text(skill_md, encoding="utf-8")
    print(f"  wrap command -> {dest}")


def install_borrowed(manifest: dict, dest_root: Path, platforms_filter: list[str]) -> int:
    count = 0
    for entry in manifest.get("skills", []):
        if platforms_filter and not any(p in entry.get("platforms", []) for p in platforms_filter):
            continue
        source_rel = entry["source"]
        if source_rel.startswith("phuryn/"):
            base = ROOT / manifest["sources"]["phuryn"]["path"]
            rel = source_rel[len("phuryn/") :]
        elif source_rel.startswith("anthropic/"):
            base = ROOT / manifest["sources"]["anthropic"]["path"]
            rel = source_rel[len("anthropic/") :]
        else:
            print(f"  skip unknown source prefix: {source_rel}")
            continue
        src = base / rel
        dest = dest_root / entry["install_as"]
        if entry.get("type") == "command":
            install_command_as_skill(src, dest, entry["install_as"])
            count += 1
            continue
        if not src.exists():
            print(f"  skip missing vendor: {src}")
            continue
        copy_skill_tree(src, dest, "copy")
        count += 1
    return count


def install_skill_list(skills: list[tuple[str, Path]], dest_root: Path) -> int:
    count = 0
    for skill_id, src in skills:
        dest = dest_root / skill_id
        if not src.exists():
            print(f"  skip missing: {src}")
            continue
        copy_skill_tree(src, dest, "copy")
        count += 1
    return count


def run_install(
    targets: list[str],
    *,
    install_native: bool,
    do_borrowed: bool,
    profiles: list[str],
    project: Path | None,
    dry_run: bool,
) -> None:
    platforms = load_yaml(ROOT / "platforms.yaml")
    marketplace = load_yaml(ROOT / "marketplace.yaml")
    manifest_path = ROOT / "borrowed" / "manifest.yaml"
    manifest = load_yaml(manifest_path) if manifest_path.exists() else {}

    profile_skills: list[tuple[str, Path]] = []
    for p in profiles:
        profile_skills.extend(profile_skill_dirs(p))

    for platform in targets:
        proj = project if platform in ("cursor", "opencode") else None
        dest = platform_dest(platform, platforms, proj)
        print(f"\n=== {platform} -> {dest} ===")
        if dry_run:
            print("  (dry-run)")
            continue
        dest.mkdir(parents=True, exist_ok=True)
        n = b = pr = 0
        if install_native:
            n = install_skill_list(skill_dirs_from_marketplace(marketplace), dest)
        if do_borrowed and manifest:
            b = install_borrowed(manifest, dest, [platform])
        if profile_skills:
            pr = install_skill_list(profile_skills, dest)
        print(f"  installed native={n} borrowed={b} profile={pr}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install ttmens-skills")
    parser.add_argument("--cursor", action="store_true")
    parser.add_argument("--hermes", action="store_true")
    parser.add_argument("--opencode", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--both", action="store_true", help="cursor + hermes (legacy)")
    parser.add_argument("--core", action="store_true", help="17 native + 23 borrowed (default)")
    parser.add_argument("--native-only", action="store_true")
    parser.add_argument("--borrowed-only", action="store_true")
    parser.add_argument("--profile", action="append", default=[], choices=list(PROFILE_PATHS.keys()))
    parser.add_argument("--project", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    targets: list[str] = []
    if args.all or args.both or args.core:
        targets = ["cursor", "hermes", "opencode"]
    else:
        if args.cursor:
            targets.append("cursor")
        if args.hermes:
            targets.append("hermes")
        if args.opencode:
            targets.append("opencode")
    if not targets:
        targets = ["cursor", "hermes", "opencode"]

    # Default: core pack (native + borrowed)
    install_native = not args.borrowed_only
    install_borrowed = not args.native_only
    if not args.native_only and not args.borrowed_only:
        install_native = True
        install_borrowed = True

    run_install(
        targets,
        install_native=install_native,
        do_borrowed=install_borrowed,
        profiles=args.profile,
        project=args.project,
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
