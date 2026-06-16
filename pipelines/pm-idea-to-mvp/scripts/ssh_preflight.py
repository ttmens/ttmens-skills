#!/usr/bin/env python3
"""SSH preflight via paramiko — reads deploy.yaml + deploy-servers registry + .env."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required", file=sys.stderr)
    sys.exit(1)

try:
    import paramiko
except ImportError:
    print("paramiko required: pip install paramiko", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from deploy_servers import resolve_deploy, resolve_ssh_password  # noqa: E402


def load_deploy(project_root: Path) -> dict:
    path = project_root / "deploy.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--command", default="echo SSH_OK")
    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    deploy = resolve_deploy(load_deploy(project_root))
    host = deploy.get("host") or os.environ.get("DEPLOY_HOST", "")
    port = int(deploy.get("port") or os.environ.get("DEPLOY_PORT", 22))
    user = deploy.get("user") or os.environ.get("DEPLOY_USER", "")
    password = resolve_ssh_password(deploy)
    if not all([host, user, password]):
        print(json.dumps({
            "ok": False,
            "error": "missing host/user/password — check deploy.yaml server + .env SSH_PASSWORD_*",
            "host": host,
            "user": user,
            "server": deploy.get("server", ""),
        }))
        return 1
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=port, username=user, password=password, timeout=15)
        _, stdout, stderr = client.exec_command(args.command, timeout=30)
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
        ok = "SSH_OK" in out or (not err and stdout.channel.recv_exit_status() == 0)
        print(json.dumps({
            "ok": ok,
            "host": host,
            "port": port,
            "server": deploy.get("server", ""),
            "stdout": out[:500],
            "stderr": err[:300],
        }, ensure_ascii=False))
        return 0 if ok else 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "host": host, "port": port}))
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
