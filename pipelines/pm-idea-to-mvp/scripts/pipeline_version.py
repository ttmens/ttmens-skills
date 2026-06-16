#!/usr/bin/env python3
"""Load pm-idea-to-mvp pipeline version from SSOT (assets/pipeline-version.yaml)."""

from __future__ import annotations

import functools
from pathlib import Path


def _pipeline_root() -> Path:
    return Path(__file__).resolve().parent.parent


@functools.lru_cache(maxsize=1)
def load_pipeline_version() -> str:
    root = _pipeline_root()
    for name in ("assets/pipeline-version.yaml", "stage-skills.yaml"):
        path = root / name
        if not path.exists():
            continue
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            version = data.get("version")
            if version:
                return str(version).strip()
        except Exception:
            continue
    return "7.1.0"


PIPELINE_VERSION: str = load_pipeline_version()
