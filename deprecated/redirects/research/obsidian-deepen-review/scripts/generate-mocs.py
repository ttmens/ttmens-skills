#!/usr/bin/env python3
"""
自动生成 Obsidian MOC（Map of Content）内容地图。

用法:
    python3 generate-mocs.py <vault路径> [选项]

选项:
    --dry-run      预览模式，不实际写入文件
    --min-notes N  只有包含 N 篇以上笔记的文件夹才生成 MOC（默认 3）
    --top-dir <目录> 只处理指定子目录

功能:
    - 扫描所有文件夹
    - 为每个文件夹生成或更新 _MOC.md
    - 自动按标签分组笔记链接
    - 建立文件夹间的层级关系
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def extract_frontmatter(content):
    """提取 YAML frontmatter。"""
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return {}, content
    return _parse_fm(match.group(1)), content[match.end():]


def _parse_fm(text):
    fm = {}
    for line in text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip()
    return fm


def extract_tags(content, frontmatter):
    """提取笔记的标签。"""
    tags = []
    if "tags" in frontmatter:
        tag_str = frontmatter["tags"]
        if tag_str.startswith("["):
            tag_str = tag_str.strip("[]")
        tags = [t.strip().strip('"').strip("'") for t in tag_str.split(",") if t.strip()]

    # 从正文提取 #标签
    content_tags = re.findall(r"#([^\s#,]+)", content)
    for t in content_tags:
        tag = f"#{t}"
        if tag not in tags:
            tags.append(tag)

    return tags


def scan_folder(folder_path, vault_root):
    """扫描文件夹，返回笔记信息和子文件夹信息。"""
    notes = []
    subfolders = []

    try:
        entries = sorted(os.listdir(folder_path))
    except PermissionError:
        return notes, subfolders

    for entry in entries:
        full_path = os.path.join(folder_path, entry)

        if os.path.isdir(full_path):
            # 跳过隐藏目录
            if entry.startswith(".") or entry == "node_modules":
                continue
            subfolders.append(entry)

        elif entry.endswith(".md") and entry != "_MOC.md":
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            frontmatter, body = extract_frontmatter(content)
            tags = extract_tags(content, frontmatter)
            title = frontmatter.get("title", entry.replace(".md", ""))

            notes.append({
                "filename": entry,
                "title": title,
                "tags": tags,
                "type": frontmatter.get("type", "general").lower(),
            })

    return notes, subfolders


def group_notes_by_tags(notes):
    """按标签对笔记分组。"""
    tag_groups = {}

    for note in notes:
        for tag in note["tags"]:
            if tag not in tag_groups:
                tag_groups[tag] = []
            tag_groups[tag].append(note)

    # 过滤掉只有 1 篇笔记的标签组
    return {k: v for k, v in tag_groups.items() if len(v) >= 2}


def generate_moc_content(folder_name, notes, subfolders, rel_path, child_mocs):
    """生成 MOC 的 Markdown 内容。"""
    lines = []

    # Frontmatter
    lines.append("---")
    lines.append(f"type: moc")
    lines.append(f"generated: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"notes_count: {len(notes)}")
    lines.append(f"subfolders: {len(subfolders)}")
    lines.append("---")
    lines.append("")

    # 标题
    display_name = folder_name.replace("-", " ").replace("_", " ")
    lines.append(f"# 📂 {display_name}")
    lines.append("")

    # 子目录
    if subfolders:
        lines.append("## 📁 子目录")
        lines.append("")
        for sf in subfolders:
            link_name = sf
            lines.append(f"- [[{sf}/_MOC|{sf}]]")
        lines.append("")

    # 子文件夹的 MOC 链接
    if child_mocs:
        lines.append("## 🗺️ 内容地图")
        lines.append("")
        for child in child_mocs:
            lines.append(f"- [[{child}/_MOC|{child}]]")
        lines.append("")

    # 核心文档（没有标签的笔记）
    untagged = [n for n in notes if not n["tags"]]
    if untagged:
        lines.append("## 📄 核心文档")
        lines.append("")
        for note in untagged:
            link_name = Path(note["filename"]).stem
            title = note["title"]
            if link_name == title:
                lines.append(f"- [[{link_name}]]")
            else:
                lines.append(f"- [[{link_name}|{title}]]")
        lines.append("")

    # 按类型分组
    by_type = {}
    for note in notes:
        if note["tags"]:
            t = note["type"]
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(note)

    if by_type:
        lines.append("## 📑 按类型")
        lines.append("")
        type_labels = {
            "article": "📖 文章",
            "meeting": "📋 会议",
            "review": "📊 复盘",
            "general": "📝 笔记",
            "moc": "🗺️ 内容地图",
        }
        for note_type, type_notes in sorted(by_type.items()):
            label = type_labels.get(note_type, "📝 笔记")
            lines.append(f"### {label}")
            lines.append("")
            for note in type_notes:
                link_name = Path(note["filename"]).stem
                title = note["title"]
                if link_name == title:
                    lines.append(f"- [[{link_name}]]")
                else:
                    lines.append(f"- [[{link_name}|{title}]]")
            lines.append("")

    # 按标签分组
    tag_groups = group_notes_by_tags(notes)
    if tag_groups:
        lines.append("## 🏷️ 按标签")
        lines.append("")
        for tag in sorted(tag_groups.keys()):
            lines.append(f"### {tag}")
            lines.append("")
            for note in tag_groups[tag]:
                link_name = Path(note["filename"]).stem
                title = note["title"]
                if link_name == title:
                    lines.append(f"- [[{link_name}]]")
                else:
                    lines.append(f"- [[{link_name}|{title}]]")
            lines.append("")

    # 所有笔记列表
    lines.append("---")
    lines.append(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}，共 {len(notes)} 篇笔记*")

    return "\n".join(lines)


def find_child_mocs(folder_path, subfolders):
    """查找子文件夹中已有的 MOC 文件。"""
    child_mocs = []
    for sf in subfolders:
        moc_path = os.path.join(folder_path, sf, "_MOC.md")
        if os.path.exists(moc_path):
            child_mocs.append(sf)
    return child_mocs


def process_vault(vault_path, top_dir=None, min_notes=3, dry_run=False):
    """处理整个 vault，生成所有 MOC。"""
    search_dir = os.path.join(vault_path, top_dir) if top_dir else vault_path
    processed = []
    skipped = []

    for root, dirs, files in os.walk(search_dir):
        # 跳过隐藏目录
        dirs[:] = [d for d in sorted(dirs) if not d.startswith(".") and d != "node_modules"]

        notes, subfolders = scan_folder(root, vault_path)

        # 只处理包含足够笔记的文件夹
        # 根目录例外：即使没有笔记也生成（作为总导航）
        is_root = (root == search_dir)
        if not is_root and len(notes) < min_notes and not subfolders:
            skipped.append(root)
            continue

        child_mocs = find_child_mocs(root, subfolders)
        folder_name = os.path.basename(root)
        rel_path = os.path.relpath(root, vault_path)

        moc_content = generate_moc_content(folder_name, notes, subfolders, rel_path, child_mocs)
        moc_path = os.path.join(root, "_MOC.md")

        if dry_run:
            print(f"[预览] {rel_path}/_MOC.md — {len(notes)} 篇笔记, {len(subfolders)} 个子目录")
        else:
            # 检查是否需要更新
            if os.path.exists(moc_path):
                with open(moc_path, "r", encoding="utf-8") as f:
                    existing = f.read()
                if existing == moc_content:
                    continue  # 没有变化，跳过

            with open(moc_path, "w", encoding="utf-8") as f:
                f.write(moc_content)
            print(f"✅ 已生成: {rel_path}/_MOC.md ({len(notes)} 篇笔记)")

        processed.append(rel_path)

    return processed, skipped


def main():
    parser = argparse.ArgumentParser(description="自动生成 Obsidian MOC 内容地图")
    parser.add_argument("vault_path", help="Obsidian vault 路径")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际写入")
    parser.add_argument("--min-notes", type=int, default=3, help="最少笔记数才生成 MOC（默认 3）")
    parser.add_argument("--top-dir", help="只处理指定子目录")

    args = parser.parse_args()

    if not os.path.isdir(args.vault_path):
        print(f"错误: vault 路径不存在: {args.vault_path}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 扫描 vault: {args.vault_path}")
    if args.dry_run:
        print("（预览模式，不会写入文件）")
    print()

    processed, skipped = process_vault(
        args.vault_path,
        top_dir=args.top_dir,
        min_notes=args.min_notes,
        dry_run=args.dry_run,
    )

    print(f"\n📊 结果: 生成了 {len(processed)} 个 MOC，跳过了 {len(skipped)} 个文件夹")


if __name__ == "__main__":
    main()
