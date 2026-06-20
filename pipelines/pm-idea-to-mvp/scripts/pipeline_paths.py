#!/usr/bin/env python3
"""Resolve pipeline, skills, and Hermes paths for pm-idea-to-mvp scripts."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_pipeline_root() -> Path:
    """Return absolute path to pipelines/pm-idea-to-mvp."""
    env_root = os.environ.get("HERMES_PIPELINE_ROOT")
    if env_root:
        p = Path(env_root)
        if p.exists():
            return p.resolve()

    script_dir = Path(__file__).resolve().parent
    pipeline_root = script_dir.parent
    if pipeline_root.name == "pm-idea-to-mvp":
        return pipeline_root

    for parent in script_dir.parents:
        candidate = parent / "pipelines" / "pm-idea-to-mvp"
        if candidate.exists() and (candidate / "SKILL.md").exists():
            return candidate

    for env_var in ("SKILLS_ROOT", "HERMES_HOME"):
        base = os.environ.get(env_var)
        if base:
            candidate = Path(base) / "pipelines" / "pm-idea-to-mvp"
            if candidate.exists():
                return candidate.resolve()
            candidate = Path(base) / "skills" / "pipelines" / "pm-idea-to-mvp"
            if candidate.exists():
                return candidate.resolve()

    return pipeline_root.resolve()


def resolve_skills_root() -> Path:
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
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env).expanduser().resolve()
    for candidate in (Path(r"D:/hermes-data"), Path.home() / ".hermes"):
        if candidate.exists():
            return candidate.resolve()
    return Path.home() / ".hermes"


def resolve_projects_root() -> Path:
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
