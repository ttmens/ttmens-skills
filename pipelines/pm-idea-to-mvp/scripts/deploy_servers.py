#!/usr/bin/env python3
"""Resolve deploy.yaml + deploy-servers registry (secrets from .env only)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from pipeline_paths import resolve_hermes_home  # noqa: E402

_ENV_LOADED = False


def load_hermes_dotenv() -> None:
    """Load HERMES_HOME/.env into os.environ (idempotent, no overwrite)."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env_path = resolve_hermes_home() / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip("\"'")
            if k and k not in os.environ:
                os.environ[k] = v
    _ENV_LOADED = True


def registry_path() -> Path:
    return resolve_hermes_home() / "config" / "deploy-servers.yaml"


def load_registry() -> dict[str, Any]:
    path = registry_path()
    if yaml is None or not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return data.get("servers") or {}


def resolve_deploy(deploy: dict[str, Any]) -> dict[str, Any]:
    """Merge server registry into deploy; explicit deploy fields win."""
    out = dict(deploy or {})
    server_id = (out.get("server") or "").strip()
    if not server_id:
        return out
    reg = load_registry().get(server_id) or {}
    for key in ("host", "port", "user", "region", "notes", "label"):
        if key in reg and not out.get(key):
            out[key] = reg[key]
    if "password_env" in reg and not out.get("password_env"):
        out["password_env"] = reg["password_env"]
    return out


def resolve_ssh_password(deploy: dict[str, Any]) -> str:
    load_hermes_dotenv()
    merged = resolve_deploy(deploy)
    refs = merged.get("secret_refs") or {}
    key_name = refs.get("ssh_password", "")
    if key_name:
        env_key = f"BSM_{key_name.replace('/', '_').replace('-', '_').upper()}"
        val = os.environ.get(env_key, "").strip()
        if val:
            return val
    pwd_env = (merged.get("password_env") or "").strip()
    if pwd_env:
        val = os.environ.get(pwd_env, "").strip()
        if val:
            return val
    server_id = (merged.get("server") or "").strip()
    if server_id:
        sid = server_id.replace("-", "_").upper()
        val = os.environ.get(f"SSH_PASSWORD_{sid}", "").strip()
        if val:
            return val
    return os.environ.get("DEPLOY_SSH_PASSWORD", "").strip()
