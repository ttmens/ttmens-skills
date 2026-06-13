#!/usr/bin/env python3
"""
扫描和聚合 Obsidian 笔记，用于周报/月报/主题复盘生成。

用法:
    python3 aggregate-notes.py <vault路径> [选项]

选项:
    --date-from <日期>     起始日期 (YYYY-MM-DD)
    --date-to <日期>       结束日期 (YYYY-MM-DD)
    --tag <标签>           按标签筛选 (如 "#支付")
    --type <类型>          按笔记类型筛选: article, meeting, review, all
    --keyword <关键词>     全文搜索关键词
    --output-format <格式> 输出格式: summary, json, markdown
    --top-dir <目录>       只搜索指定子目录
"""

import argparse
import json
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
    fm_text = match.group(1)
    body = content[match.end():]

    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip()

    return fm, body


def extract_date(content, frontmatter, filename):
    """从 frontmatter 或文件名中提取日期。"""
    # 优先从 frontmatter
    for key in ["date", "created", "updated", "generated"]:
        if key in frontmatter:
            date_str = frontmatter[key]
            m = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
            if m:
                return m.group(1)

    # 从文件名提取
    m = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if m:
        return m.group(1)

    return None


def extract_tags(content, frontmatter):
    """从 frontmatter 或正文中提取标签。"""
    tags = []

    # 从 frontmatter
    if "tags" in frontmatter:
        tag_str = frontmatter["tags"]
        if tag_str.startswith("["):
            tag_str = tag_str.strip("[]")
        tags = [t.strip().strip('"').strip("'") for t in tag_str.split(",") if t.strip()]

    # 从正文提取 #标签
    content_tags = re.findall(r"#([^\s#,]+)", content)
    for t in content_tags:
        tag_with_hash = f"#{t}"
        if tag_with_hash not in tags:
            tags.append(tag_with_hash)

    return tags


def scan_notes(vault_path, top_dir=None):
    """扫描 vault 中的所有 markdown 笔记。"""
    notes = []
    search_dir = os.path.join(vault_path, top_dir) if top_dir else vault_path

    if not os.path.exists(search_dir):
        print(f"警告: 目录不存在: {search_dir}", file=sys.stderr)
        return notes

    for root, dirs, files in os.walk(search_dir):
        # 跳过隐藏目录和 .obsidian
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]

        for filename in files:
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, vault_path)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"警告: 无法读取 {filepath}: {e}", file=sys.stderr)
                continue

            frontmatter, body = extract_frontmatter(content)
            date = extract_date(content, frontmatter, filename)
            tags = extract_tags(content, frontmatter)

            # 判断笔记类型
            note_type = "general"
            type_val = frontmatter.get("type", "").lower()
            if type_val in ["article", "meeting", "review", "weekly-review", "monthly-review", "topic-review"]:
                note_type = type_val
            elif "summary" in tags or "文章" in rel_path.lower():
                note_type = "article"
            elif "meeting" in tags or "会议" in rel_path:
                note_type = "meeting"
            elif "review" in tags or "review" in rel_path.lower():
                note_type = "review"
            elif "moc" in filename.lower():
                note_type = "moc"

            notes.append({
                "path": filepath,
                "rel_path": rel_path,
                "filename": filename,
                "title": frontmatter.get("title", filename.replace(".md", "")),
                "date": date,
                "tags": tags,
                "type": note_type,
                "frontmatter": frontmatter,
                "preview": body[:300].strip() if body else "",
                "word_count": len(body),
            })

    # 按日期排序
    notes.sort(key=lambda n: n["date"] or "", reverse=True)
    return notes


def filter_notes(notes, date_from=None, date_to=None, tag=None, note_type=None, keyword=None):
    """按条件筛选笔记。"""
    filtered = notes

    if date_from:
        filtered = [n for n in filtered if n["date"] and n["date"] >= date_from]

    if date_to:
        filtered = [n for n in filtered if n["date"] and n["date"] <= date_to]

    if tag:
        tag_clean = tag.lstrip("#")
        filtered = [n for n in filtered if any(tag_clean in t or t == tag for t in n["tags"])]

    if note_type and note_type != "all":
        filtered = [n for n in filtered if n["type"] == note_type or note_type in n["type"]]

    if keyword:
        keyword_lower = keyword.lower()
        filtered = [n for n in filtered
                    if keyword_lower in n["preview"].lower()
                    or keyword_lower in n["title"].lower()
                    or keyword_lower in " ".join(n["tags"]).lower()]

    return filtered


def format_summary(notes):
    """格式化笔记为人类可读的汇总。"""
    if not notes:
        return "没有找到匹配的笔记。"

    lines = [f"📋 笔记汇总 ({len(notes)}篇)\n"]

    # 按类型分组
    by_type = {}
    for n in notes:
        t = n["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(n)

    type_emojis = {
        "article": "📖",
        "meeting": "📋",
        "review": "📊",
        "moc": "🗺️",
        "general": "📝",
    }

    for note_type, type_notes in sorted(by_type.items()):
        emoji = type_emojis.get(note_type, "📝")
        lines.append(f"{emoji} {note_type} ({len(type_notes)}篇)")
        for n in type_notes:
            date_str = f"[{n['date']}] " if n["date"] else ""
            tags_str = " ".join(n["tags"][:3])
            lines.append(f"  - {date_str}{n['title']} {tags_str}")
        lines.append("")

    return "\n".join(lines)


def format_markdown_report(notes, title="笔记汇总"):
    """格式化笔记为 Markdown 报告。"""
    lines = [f"# {title}\n", f"> 共 {len(notes)} 篇笔记\n"]

    # 按类型分组
    by_type = {}
    for n in notes:
        t = n["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(n)

    type_headers = {
        "article": "📖 阅读",
        "meeting": "📋 会议",
        "review": "📊 复盘",
        "general": "📝 笔记",
        "moc": "🗺️ 内容地图",
    }

    for note_type, type_notes in sorted(by_type.items()):
        header = type_headers.get(note_type, "📝 笔记")
        lines.append(f"\n## {header} ({len(type_notes)}篇)\n")
        for n in type_notes:
            date_str = f"（{n['date']}）" if n["date"] else ""
            tags_str = " ".join(n["tags"][:3])
            # 使用文件名生成 wikilink（不含路径和扩展名）
            link_name = Path(n["filename"]).stem
            lines.append(f"### {date_str} [[{link_name}]]")
            if tags_str:
                lines.append(f"*{tags_str}*")
            if n["preview"]:
                preview = n["preview"][:300]
                lines.append(f"> {preview}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="扫描和聚合 Obsidian 笔记")
    parser.add_argument("vault_path", help="Obsidian vault 路径")
    parser.add_argument("--date-from", help="起始日期 (YYYY-MM-DD)")
    parser.add_argument("--date-to", help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--tag", help="按标签筛选 (如 '#支付')")
    parser.add_argument("--type", help="按笔记类型筛选: article, meeting, review, all")
    parser.add_argument("--keyword", help="全文搜索关键词")
    parser.add_argument("--output-format", choices=["summary", "json", "markdown"], default="summary", dest="output_format")
    parser.add_argument("--top-dir", help="只搜索指定子目录", dest="top_dir")

    args = parser.parse_args()

    notes = scan_notes(args.vault_path, top_dir=args.top_dir)
    filtered = filter_notes(notes, date_from=args.date_from, date_to=args.date_to,
                           tag=args.tag, note_type=args.type, keyword=args.keyword)

    if args.output_format == "json":
        # 简化 JSON 输出（去掉完整的 frontmatter）
        output = []
        for n in filtered:
            out = {k: v for k, v in n.items() if k != "frontmatter"}
            output.append(out)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.output_format == "markdown":
        print(format_markdown_report(filtered))
    else:
        print(format_summary(filtered))


if __name__ == "__main__":
    main()
