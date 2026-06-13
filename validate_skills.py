#!/usr/bin/env python3
"""Shim — run scripts/validate_skills.py (repo layout v6.1)."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "scripts" / "validate_skills.py"), run_name="__main__")
