#!/usr/bin/env python3
"""
pipeline_paths.py — Resolve pipeline root directory.

Provides resolve_pipeline_root() which returns the absolute path to
the pm-idea-to-mvp pipeline directory within the SKILLS_ROOT.
"""

import os
import sys
from pathlib import Path


def resolve_pipeline_root() -> Path:
    """
    Resolve the pm-idea-to-mvp pipeline root directory.

    Strategy:
    1. Check HERMES_PIPELINE_ROOT env var (explicit override)
    2. Walk up from this script's location to find pipelines/pm-idea-to-mvp
    3. Check common SKILLS_ROOT locations
    """
    # 1. Explicit override
    env_root = os.environ.get("HERMES_PIPELINE_ROOT")
    if env_root:
        p = Path(env_root)
        if p.exists():
            return p.resolve()

    # 2. Relative to this script
    script_dir = Path(__file__).resolve().parent
    # scripts/ is inside pipelines/pm-idea-to-mvp/scripts/
    pipeline_root = script_dir.parent  # pipelines/pm-idea-to-mvp
    if pipeline_root.name == "pm-idea-to-mvp":
        return pipeline_root

    # 3. Walk up looking for pipelines/pm-idea-to-mvp
    for parent in script_dir.parents:
        candidate = parent / "pipelines" / "pm-idea-to-mvp"
        if candidate.exists() and (candidate / "SKILL.md").exists():
            return candidate

    # 4. Check HERMES_HOME / SKILLS_ROOT env vars
    for env_var in ("SKILLS_ROOT", "HERMES_HOME"):
        base = os.environ.get(env_var)
        if base:
            candidate = Path(base) / "pipelines" / "pm-idea-to-mvp"
            if candidate.exists():
                return candidate.resolve()

    # 5. Fallback: assume we're in the right place
    return script_dir.parent.resolve()


def resolve_skills_root() -> Path:
    """Resolve the SKILLS_ROOT (ttmens-skills repo root)."""
    env_root = os.environ.get("SKILLS_ROOT")
    if env_root:
        p = Path(env_root).expanduser()
        if p.exists():
            return p.resolve()

    pipeline_root = resolve_pipeline_root()
    for parent in pipeline_root.parents:
        if (parent / "pipelines" / "pm-idea-to-mvp" / "SKILL.md").exists():
            return parent
    return pipeline_root.parent.parent.resolve()


def resolve_hermes_home() -> Path:
    """Resolve Hermes home directory (~/.hermes or HERMES_HOME)."""
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env).expanduser().resolve()
    for candidate in (
        Path(r"D:/hermes-data"),
        Path.home() / ".hermes",
    ):
        if candidate.exists():
            return candidate.resolve()
    return Path.home() / ".hermes"


def resolve_projects_root() -> Path:
    """Resolve pm-{slug} projects parent directory."""
    env = os.environ.get("PROJECTS_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    for candidate in (
        Path(r"D:/workspace/projects"),
        resolve_hermes_home().parent / "workspace" / "projects",
    ):
        if candidate.exists():
            return candidate.resolve()
    return Path.home() / "projects"


if __name__ == "__main__":
    print(f"pipeline_root: {resolve_pipeline_root()}")
    print(f"skills_root: {resolve_skills_root()}")
    print(f"hermes_home: {resolve_hermes_home()}")
    print(f"projects_root: {resolve_projects_root()}")
