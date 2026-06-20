#!/usr/bin/env python3
"""Detect agent platform, SKILLS_ROOT, project root, and install status."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_REL = Path("pipelines/pm-idea-to-mvp/SKILL.md")
STAGE_COMPLETE_REL = Path("pipelines/pm-idea-to-mvp/scripts/inner-loop-driver.py")


def _expand(path: str) -> Path:
    return Path(os.path.expanduser(path))


def _has_pipeline(skills_root: Path) -> bool:
    return (skills_root / PIPELINE_REL).is_file()


def _load_platforms() -> dict:
    path = ROOT / "platforms.yaml"
    if yaml is None or not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _detect_project_root(cwd: Path) -> Path | None:
    env = os.environ.get("PROJECT_ROOT")
    if env:
        p = _expand(env)
        if p.is_dir():
            return p.resolve()
    markers = ("00-brief.md", "gates.json", "docs/workflow_state.yaml")
    for base in [cwd, *cwd.parents]:
        if any((base / m).exists() for m in markers):
            return base.resolve()
    return None


def _resolve_skills_root(cwd: Path, platforms: dict) -> tuple[Path | None, bool, str | None]:
    """Return (skills_root, source_mode, platform_hint)."""
    for base in [cwd, *cwd.parents]:
        if (base / "marketplace.yaml").exists() and _has_pipeline(base):
            return base.resolve(), True, None

    plat_cfg = platforms.get("platforms", {})
    project = _detect_project_root(cwd)

    if project:
        for name in ("cursor", "opencode"):
            cfg = plat_cfg.get(name, {})
            proj_dir = cfg.get("project_dir", "").lstrip("./")
            if proj_dir:
                candidate = project / proj_dir
                if _has_pipeline(candidate):
                    return candidate.resolve(), False, name

    checks: list[tuple[str, Path]] = []
    if (cwd / ".cursor" / "hooks.json").exists() or (cwd / ".cursor" / "skills").is_dir():
        checks.append(("cursor", _expand(plat_cfg.get("cursor", {}).get("global_dir", "~/.cursor/skills"))))
    if os.environ.get("HERMES_HOME") or os.environ.get("HERMES_PIPELINE_ROOT"):
        checks.append(("hermes", _expand(plat_cfg.get("hermes", {}).get("global_dir", "~/.hermes/skills"))))
    if (cwd / ".opencode" / "skills").is_dir():
        checks.append(("opencode", _expand(plat_cfg.get("opencode", {}).get("global_dir", "~/.config/opencode/skills"))))

    env_root = os.environ.get("SKILLS_ROOT")
    if env_root:
        candidate = _expand(env_root)
        if _has_pipeline(candidate):
            return candidate.resolve(), False, None

    for name, path in checks:
        if _has_pipeline(path):
            return path.resolve(), False, name

    for name, key in (
        ("cursor", "~/.cursor/skills"),
        ("hermes", "~/.hermes/skills"),
        ("opencode", "~/.config/opencode/skills"),
    ):
        cfg = plat_cfg.get(name, {})
        candidate = _expand(cfg.get("global_dir", key))
        if _has_pipeline(candidate):
            return candidate.resolve(), False, name

    if _has_pipeline(ROOT):
        return ROOT.resolve(), True, None
    return None, False, None


def _detect_platform(cwd: Path, skills_root: Path | None, project: Path | None, hint: str | None) -> str:
    if hint:
        return hint
    if project and (project / ".cursor" / "skills").is_dir():
        return "cursor"
    if project and (project / ".opencode" / "skills").is_dir():
        return "opencode"
    if os.environ.get("HERMES_HOME") or os.environ.get("HERMES_PIPELINE_ROOT"):
        return "hermes"
    if (cwd / ".cursor").exists():
        return "cursor"
    if (cwd / ".opencode").exists():
        return "opencode"
    if skills_root and "hermes" in str(skills_root).lower():
        return "hermes"
    return "unknown"


def _recommended_install(platform: str) -> str:
    base = f'python "{ROOT / "scripts" / "install_skills.py"}" --core --profile debate'
    if platform == "cursor":
        return f"{base} --platform cursor --project ."
    if platform == "hermes":
        return f"{base} --platform hermes --profile hermes-kanban"
    if platform == "opencode":
        return f"{base} --platform opencode --project ."
    return f"{base} --all"


def build_report(cwd: Path | None = None) -> dict:
    cwd = (cwd or Path.cwd()).resolve()
    platforms = _load_platforms()
    skills_root, source_mode, hint = _resolve_skills_root(cwd, platforms)
    project_root = _detect_project_root(cwd)
    platform = _detect_platform(cwd, skills_root, project_root, hint)
    install_needed = skills_root is None or not _has_pipeline(skills_root)
    return {
        "platform": platform,
        "skills_root": str(skills_root) if skills_root else None,
        "project_root": str(project_root) if project_root else None,
        "source_mode": source_mode,
        "install_needed": install_needed,
        "pipeline_version": _read_pipeline_version(skills_root) if skills_root else None,
        "recommended_install_cmd": _recommended_install(platform),
        "validate_cmd": f'python "{(skills_root or ROOT) / "scripts" / "validate_skills.py"}"',
    }


def _read_pipeline_version(skills_root: Path) -> str | None:
    skill_md = skills_root / PIPELINE_REL
    if not skill_md.exists() or yaml is None:
        return None
    text = skill_md.read_text(encoding="utf-8")
    if text.startswith("---"):
        try:
            front = text.split("---", 2)[1]
            data = yaml.safe_load(front) or {}
            return str(data.get("version", "")) or None
        except Exception:
            return None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect agent environment for ttmens-skills")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--cwd", type=Path, default=None, help="Working directory to inspect")
    args = parser.parse_args()

    report = build_report(args.cwd)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for k, v in report.items():
            print(f"{k}: {v}")
    return 0 if not report["install_needed"] else 1


if __name__ == "__main__":
    sys.exit(main())
