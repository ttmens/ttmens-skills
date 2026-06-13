#!/usr/bin/env python3
"""Pre-commit hook: warn if stage-status shows failing gates (Cursor)."""
import json
import sys
from pathlib import Path

status = Path(".cursor/stage-status.json")
if status.exists():
    data = json.loads(status.read_text(encoding="utf-8"))
    if not data.get("all_passed", True):
        print(f"Warning: pipeline stage '{data.get('stage')}' gates not passed.")
        sys.exit(0)
sys.exit(0)
