#!/usr/bin/env python3
"""Feishu notify — delegate to skills/scripts/feishu_notify.py (SSOT)."""
import runpy
from pathlib import Path

root_script = Path(__file__).resolve().parents[3] / "scripts" / "feishu_notify.py"
runpy.run_path(str(root_script), run_name="__main__")
