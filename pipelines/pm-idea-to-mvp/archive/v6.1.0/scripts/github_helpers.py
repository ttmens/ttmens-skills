"""GitHub API helpers for PM pipeline (no gh CLI required)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

GITHUB_OWNER = os.environ.get("PM_GITHUB_OWNER", "ttmens")
HERMES_ENV = Path(os.environ.get("HERMES_HOME", r"D:\hermes-data")) / ".env"


def load_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    if HERMES_ENV.exists():
        for line in HERMES_ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("GITHUB_TOKEN=") and not line.strip().startswith("#"):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("GITHUB_TOKEN not found in env or HERMES_HOME/.env")


def _api(method: str, path: str, body: dict | None = None) -> Any:
    token = load_token()
    url = f"https://api.github.com{path}"
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "hermes-pm-pipeline",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed ({e.code}): {detail}") from e


def verify_user() -> str:
    return _api("GET", "/user")["login"]


def repo_exists(name: str, owner: str = GITHUB_OWNER) -> bool:
    try:
        _api("GET", f"/repos/{owner}/{name}")
        return True
    except RuntimeError as e:
        if "404" in str(e):
            return False
        raise


def create_repo(name: str, description: str = "", private: bool = False, owner: str = GITHUB_OWNER) -> dict:
    if repo_exists(name, owner):
        return _api("GET", f"/repos/{owner}/{name}")
    return _api(
        "POST",
        "/user/repos" if owner == verify_user() else f"/orgs/{owner}/repos",
        {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": False,
        },
    )


def enable_pages(name: str, branch: str = "main", path: str = "/docs", owner: str = GITHUB_OWNER) -> dict:
    try:
        return _api(
            "POST",
            f"/repos/{owner}/{name}/pages",
            {"source": {"branch": branch, "path": path}},
        )
    except RuntimeError as e:
        if "409" in str(e) or "already exists" in str(e).lower():
            return _api("GET", f"/repos/{owner}/{name}/pages")
        raise


def list_pm_repos(owner: str = GITHUB_OWNER) -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        batch = _api("GET", f"/users/{owner}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        for r in batch:
            if r.get("name", "").startswith("pm-"):
                repos.append(r)
        if len(batch) < 100:
            break
        page += 1
    return sorted(repos, key=lambda r: r.get("updated_at", ""), reverse=True)


def pages_url(repo_name: str, owner: str = GITHUB_OWNER) -> str:
    return f"https://{owner}.github.io/{repo_name}/"


def repo_url(repo_name: str, owner: str = GITHUB_OWNER) -> str:
    return f"https://github.com/{owner}/{repo_name}"
