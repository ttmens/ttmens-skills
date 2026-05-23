#!/usr/bin/env python3
"""
Aggregate and search Obsidian notes for summary generation.

Usage:
    python3 aggregate-notes.py <vault-path> [options]

Options:
    --date-from <date>    Start date (YYYY-MM-DD)
    --date-to <date>      End date (YYYY-MM-DD)
    --tag <tag>           Filter by tag (e.g., "#支付")
    --type <type>         Filter by note type: article, meeting, review, all
    --keyword <word>      Full-text search keyword
    --output-format <fmt> Output format: summary, json, markdown
    --top-dir <dir>       Search only under this subdirectory
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return {}, content
    frontmatter_text = match.group(1)
    body = content[match.end():]

    frontmatter = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def extract_date_from_content(content, frontmatter):
    """Extract date from frontmatter or filename."""
    # Try frontmatter first
    for key in ["date", "created", "updated"]:
        if key in frontmatter:
            date_str = frontmatter[key]
            # Try to parse YYYY-MM-DD
            match = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
            if match:
                return match.group(1)

    # Try filename
    return None


def extract_tags(content, frontmatter):
    """Extract tags from frontmatter or content."""
    tags = []

    # From frontmatter
    if "tags" in frontmatter:
        tag_str = frontmatter["tags"]
        # Handle both list format and comma-separated
        if tag_str.startswith("["):
            tag_str = tag_str.strip("[]")
        tags = [t.strip().strip('"').strip("'") for t in tag_str.split(",") if t.strip()]

    # From content (#hashtags)
    content_tags = re.findall(r"#([^\s#,]+)", content)
    for t in content_tags:
        tag_with_hash = f"#{t}"
        if tag_with_hash not in tags:
            tags.append(tag_with_hash)

    return tags


def scan_notes(vault_path, top_dir=None):
    """Scan vault for markdown notes."""
    notes = []
    search_dir = os.path.join(vault_path, top_dir) if top_dir else vault_path

    if not os.path.exists(search_dir):
        print(f"Warning: Directory not found: {search_dir}", file=sys.stderr)
        return notes

    for root, dirs, files in os.walk(search_dir):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
                continue

            frontmatter, body = extract_frontmatter(content)
            date = extract_date_from_content(content, frontmatter)
            tags = extract_tags(content, frontmatter)

            # Determine note type
            note_type = "general"
            type_val = frontmatter.get("type", "").lower()
            if type_val in ["article", "meeting", "review", "weekly-review", "monthly-review", "topic-review"]:
                note_type = type_val
            elif "summary" in tags or "article" in filepath.lower():
                note_type = "article"
            elif "meeting" in tags or "会议" in filepath.lower():
                note_type = "meeting"
            elif "review" in tags or "review" in filepath.lower():
                note_type = "review"

            notes.append({
                "path": filepath,
                "filename": filename,
                "title": frontmatter.get("title", filename.replace(".md", "")),
                "date": date,
                "tags": tags,
                "type": note_type,
                "frontmatter": frontmatter,
                "preview": body[:200].strip() if body else "",
            })

    return notes


def filter_notes(notes, date_from=None, date_to=None, tag=None, note_type=None, keyword=None):
    """Filter notes based on criteria."""
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
        filtered = [n for n in filtered if keyword.lower() in n["preview"].lower() or keyword.lower() in n["title"].lower()]

    return filtered


def format_summary(notes):
    """Format notes as a human-readable summary."""
    if not notes:
        return "没有找到匹配的笔记。"

    lines = [f"📋 笔记汇总 ({len(notes)}篇)\n"]

    # Group by type
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
    """Format notes as a markdown report."""
    lines = [f"# {title}\n", f"> 共 {len(notes)} 篇笔记\n"]

    for n in notes:
        date_str = f"({n['date']}) " if n["date"] else ""
        tags_str = " ".join(n["tags"])
        lines.append(f"### {date_str}{n['title']}")
        if tags_str:
            lines.append(f"*{tags_str}*")
        if n["preview"]:
            preview = n["preview"][:300]
            lines.append(f"> {preview}")
        lines.append("")
        lines.append(f"📄 [[{Path(n['path']).stem}]]")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Aggregate and search Obsidian notes")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--date-from", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--date-to", help="End date (YYYY-MM-DD)")
    parser.add_argument("--tag", help="Filter by tag (e.g., '#支付')")
    parser.add_argument("--type", help="Filter by note type: article, meeting, review, all")
    parser.add_argument("--keyword", help="Full-text search keyword")
    parser.add_argument("--output-format", choices=["summary", "json", "markdown"], default="summary")
    parser.add_argument("--top-dir", help="Search only under this subdirectory")

    args = parser.parse_args()

    notes = scan_notes(args.vault_path, top_dir=args.top_dir)
    filtered = filter_notes(notes, date_from=args.date_from, date_to=args.date_to,
                           tag=args.tag, note_type=args.type, keyword=args.keyword)

    if args.output_format == "json":
        # Simplify for JSON output (remove full frontmatter)
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
