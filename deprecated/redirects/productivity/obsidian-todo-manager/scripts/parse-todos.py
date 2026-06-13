#!/usr/bin/env python3
"""
Parse and filter Obsidian TODO.md entries.

Usage:
    python3 parse-todos.py <path-to-todo.md> [options]

Options:
    --tag <tag>       Filter by tag (e.g., "#prd")
    --status <status> Filter by status: pending, done, all
    --priority <p>    Filter by priority: P0, P1, P2, all
    --summary         Show summary counts
    --json            Output as JSON
"""

import argparse
import json
import re
import sys
from collections import defaultdict


# Priority section patterns
PRIORITY_SECTIONS = {
    "P0": r"^## 🔴 P0",
    "P1": r"^## 🟡 P1",
    "P2": r"^## 🟢 P2",
    "done": r"^## ✅ 已完成",
}

# Todo entry pattern
TODO_PATTERN = re.compile(
    r"^- \[([ x])\]\s+"           # [ ] or [x]
    r"(\d{4}-\d{2}-\d{2})\s*\|"  # date
    r"\s*(.+?)\s*\|"             # description
    r"\s*(#.+?)?\s*$"            # tags (optional)
)


def parse_todo_entry(line):
    """Parse a single todo line into a dict."""
    match = TODO_PATTERN.match(line.strip())
    if not match:
        return None

    status_char, date, description, tags_raw = match.groups()
    status = "done" if status_char == "x" else "pending"
    tags = []
    extra = ""

    if tags_raw:
        tags_raw = tags_raw.strip()
        # Split into tags and extra info
        parts = tags_raw.split("|")
        for part in parts:
            part = part.strip()
            if part.startswith("#"):
                tags.extend(part.split())
            else:
                extra = part

    return {
        "status": status,
        "date": date,
        "description": description.strip(),
        "tags": tags,
        "extra": extra,
        "raw": line.strip(),
    }


def parse_todo_file(filepath):
    """Parse a TODO.md file and return entries grouped by priority."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result = {"P0": [], "P1": [], "P2": [], "done": []}
    current_section = None

    for line in lines:
        stripped = line.strip()

        # Check for section headers
        if stripped.startswith("## "):
            for priority, pattern in PRIORITY_SECTIONS.items():
                if re.match(pattern, stripped):
                    current_section = priority
                    break
            continue

        # Parse todo entries
        if current_section and stripped.startswith("- ["):
            entry = parse_todo_entry(stripped)
            if entry:
                entry["priority"] = current_section if current_section != "done" else "done"
                result[current_section].append(entry)

    return result


def filter_entries(entries, tag=None, status=None, priority=None):
    """Filter entries based on criteria."""
    all_entries = []
    for p, items in entries.items():
        all_entries.extend(items)

    filtered = all_entries

    if status and status != "all":
        filtered = [e for e in filtered if e["status"] == status]

    if tag:
        filtered = [e for e in filtered if tag in e.get("tags", [])]

    if priority and priority != "all":
        filtered = [e for e in filtered if e.get("priority") == priority]

    return filtered


def format_summary(entries):
    """Format entries as a human-readable summary."""
    lines = []
    counts = defaultdict(int)

    for entry in entries:
        priority = entry.get("priority", "P2")
        counts[priority] += 1

    # Emoji mapping
    emojis = {"P0": "🔴", "P1": "🟡", "P2": "🟢", "done": "✅"}
    labels = {"P0": "P0 紧急", "P1": "P1 重要", "P2": "P2 常规", "done": "已完成"}

    for p in ["P0", "P1", "P2", "done"]:
        if counts[p] > 0:
            lines.append(f"{emojis[p]} {labels[p]} ({counts[p]}项)")
            # Show entries for this priority
            for entry in entries:
                if entry.get("priority") == p:
                    desc = entry["description"]
                    tags = " ".join(entry.get("tags", []))
                    extra = entry.get("extra", "")
                    line = f"  - {desc}"
                    if tags:
                        line += f" {tags}"
                    if extra:
                        line += f" | {extra}"
                    lines.append(line)
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Parse and filter Obsidian TODO.md entries")
    parser.add_argument("filepath", help="Path to TODO.md file")
    parser.add_argument("--tag", help="Filter by tag (e.g., '#prd')")
    parser.add_argument("--status", choices=["pending", "done", "all"], default="all", help="Filter by status")
    parser.add_argument("--priority", choices=["P0", "P1", "P2", "all"], default="all", help="Filter by priority")
    parser.add_argument("--summary", action="store_true", help="Show summary counts")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    try:
        entries = parse_todo_file(args.filepath)
    except FileNotFoundError:
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)

    filtered = filter_entries(entries, tag=args.tag, status=args.status, priority=args.priority)

    if args.json_output:
        print(json.dumps(filtered, ensure_ascii=False, indent=2))
    elif args.summary:
        print(format_summary(filtered))
    else:
        for entry in filtered:
            status_icon = "✅" if entry["status"] == "done" else "⬜"
            tags = " ".join(entry.get("tags", []))
            print(f"{status_icon} [{entry.get('priority', '?')}] {entry['description']} {tags}")


if __name__ == "__main__":
    main()
