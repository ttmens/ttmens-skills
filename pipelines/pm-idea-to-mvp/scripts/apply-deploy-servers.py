#!/usr/bin/env python3
"""Apply default deploy server to all pm-* projects."""
from __future__ import annotations

import yaml
from pathlib import Path

ROOT = Path(r"D:\workspace\projects")


def main() -> int:
    for proj in sorted(ROOT.glob("pm-*")):
        if not proj.is_dir():
            continue
        slug = proj.name.removeprefix("pm-")
        dest = proj / "deploy.yaml"
        data = yaml.safe_load(dest.read_text(encoding="utf-8")) if dest.exists() else {}
        data = data or {}
        data.setdefault("version", "1.0")
        data["server"] = data.get("server") or "dc1-priority"
        data["secret_refs"] = {"ssh_password": f"servers/{data['server']}"}
        if not data.get("project_path"):
            data["project_path"] = f"~/pm-{slug}"
        for k in ("host", "user"):
            if not data.get(k):
                data.pop(k, None)
        if data.get("port") in (22, "22", None, "") and data.get("server"):
            data.pop("port", None)
        dest.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"updated {proj.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
