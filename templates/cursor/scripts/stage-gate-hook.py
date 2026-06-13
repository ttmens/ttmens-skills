#!/usr/bin/env python3
import json
from pathlib import Path
import sys

p = Path(".cursor/stage-status.json")
if p.exists():
    d = json.loads(p.read_text(encoding="utf-8"))
    if not d.get("all_passed", True):
        print(f"[ttmens-skills] stage {d.get('stage')} gates failed — commit allowed with warning")
sys.exit(0)
