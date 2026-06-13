#!/usr/bin/env python3
# Do not edit logic here — SSOT is scripts/feishu_notify.py
"""Delegate to repo-root feishu_notify.py."""import runpy
from pathlib import Path

root_script = Path(__file__).resolve().parents[3] / "scripts" / "feishu_notify.py"
runpy.run_path(str(root_script), run_name="__main__")
