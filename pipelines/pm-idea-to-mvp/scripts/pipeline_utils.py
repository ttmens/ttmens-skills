#!/usr/bin/env python3
"""
pipeline_utils.py — Shared utilities for pm-idea-to-mvp pipeline scripts.

v6.2: Extracted from duplicated code in validate-gates.py, goal-check.py,
stage-complete.py. Provides:
- YAML parsing (with PyYAML fallback)
- File existence/line-count checks
- URL counting
- Content pattern matching
- Logging setup
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


# === Logging ===

def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """Setup standardized logging for pipeline scripts."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            f"%(asctime)s [{name}] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S"
        ))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


# === YAML Parsing ===

def load_yaml(path: Path) -> dict:
    """
    Load YAML file with PyYAML if available, else fallback parser.
    Handles the subset of YAML used in goals/*.yaml and harness-rules.yaml.
    """
    if not path.exists():
        return {}

    # Try PyYAML first
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: basic parser for goals YAML format
    return _parse_yaml_fallback(path)


def _parse_yaml_fallback(path: Path) -> dict:
    """Minimal YAML parser for goals files (no external deps)."""
    text = path.read_text(encoding="utf-8")
    result: dict[str, Any] = {}
    current_list = None
    current_item = None
    stage_name = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Top-level key: stage: xxx
        if line.startswith("stage:"):
            stage_name = stripped.split(":", 1)[1].strip().strip("'\"")
            result["stage"] = stage_name
            continue

        # goals: starts the list
        if stripped == "goals:":
            result["goals"] = []
            current_list = result["goals"]
            continue

        # List item start: - id: R1
        if stripped.startswith("- id:"):
            current_item = {}
            val = stripped.split(":", 1)[1].strip().strip("'\"")
            current_item["id"] = val
            if current_list is not None:
                current_list.append(current_item)
            continue

        # List item continuation: key: value
        if current_item is not None and ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip("'\"")
            try:
                val = int(val)
            except (ValueError, TypeError):
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    pass
            current_item[key] = val
            continue

    return result


def load_harness_rules(project_root: Path) -> dict:
    """Load harness-rules.yaml from project root."""
    rules_path = project_root / "harness-rules.yaml"
    if not rules_path.exists():
        return {}
    return load_yaml(rules_path)


# === File Checks ===

def check_file_exists(project_root: Path, filepath: str) -> dict:
    """Check if a file exists relative to project root."""
    full_path = project_root / filepath
    exists = full_path.exists()
    return {
        "file": filepath,
        "exists": exists,
        "pass": exists,
    }


def count_lines(filepath: Path) -> int:
    """Count non-empty lines in a file."""
    if not filepath.exists():
        return 0
    content = filepath.read_text(encoding="utf-8", errors="replace")
    return len([l for l in content.splitlines() if l.strip()])


def check_min_lines(project_root: Path, filepath: str, min_lines: int) -> dict:
    """Check if file has minimum non-empty lines."""
    full_path = project_root / filepath
    if not full_path.exists():
        return {"file": filepath, "pass": False, "detail": "File not found"}
    count = count_lines(full_path)
    return {
        "file": filepath,
        "pass": count >= min_lines,
        "line_count": count,
        "min_required": min_lines,
    }


def count_urls(content: str) -> int:
    """Count unique URLs in content."""
    url_pattern = r'https?://[^\s\)>\]\"\']+'
    urls = re.findall(url_pattern, content)
    return len(set(urls))


def check_url_count(project_root: Path, filepath: str, min_urls: int) -> dict:
    """Check if file has minimum unique URLs."""
    full_path = project_root / filepath
    if not full_path.exists():
        return {"file": filepath, "pass": False, "detail": "File not found"}
    content = full_path.read_text(encoding="utf-8", errors="replace")
    count = count_urls(content)
    return {
        "file": filepath,
        "pass": count >= min_urls,
        "url_count": count,
        "min_required": min_urls,
    }


def check_content_pattern(project_root: Path, filepath: str, pattern: str) -> dict:
    """Check if file content matches a regex pattern."""
    full_path = project_root / filepath
    if not full_path.exists():
        return {"file": filepath, "pass": False, "detail": "File not found"}
    content = full_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(pattern, content, re.IGNORECASE)
    return {
        "file": filepath,
        "pass": bool(match),
        "pattern": pattern,
        "matched": bool(match),
    }


# === Subprocess Helpers ===

def run_cmd(cmd: str, cwd: Path | None = None, timeout: int = 120) -> dict:
    """Run a shell command and return structured result."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=str(cwd) if cwd else None,
            capture_output=True, text=True, timeout=timeout,
        )
        return {
            "command": cmd,
            "exit_code": result.returncode,
            "pass": result.returncode == 0,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:500],
        }
    except subprocess.TimeoutExpired:
        return {"command": cmd, "pass": False, "detail": f"Timed out ({timeout}s)"}
    except Exception as e:
        return {"command": cmd, "pass": False, "detail": str(e)}


# === JSON Output ===

def print_json(data: dict) -> None:
    """Print JSON to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2))
