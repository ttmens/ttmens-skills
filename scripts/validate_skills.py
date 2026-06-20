#!/usr/bin/env python3
"""Validate ttmens-skills marketplace, native paths, borrowed vendor refs, pipeline scripts (v9.1)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []

# v9.1: only core pipeline scripts remain
PIPELINE_SCRIPTS = [
    "consume-feedback.py",
    "init-project.py",
    "inner-loop-driver.py",
    "pipeline_paths.py",
    "pipeline_version.py",
]

PIPELINE_ASSETS = [
    "harness-rules.yaml",
]

ROOT_SCRIPTS = [
    "detect_agent_env.py",
    "feishu_notify.py",
    "publish_repo.py",
    "merge-retro-knowledge.py",
    "self_check.py",
    "deploy-verify.py",
    "check_docs_ssot.py",
    "ui_acceptance.py",
    "lighthouse_check.py",
    "validate_skills.py",
    "install_skills.py",
]

VENDOR_SUBMODULES = [
    "vendor/phuryn-pm-skills",
    "vendor/knowledge-work-plugins",
    "vendor/ui-ux-pro-max-skill",
    "vendor/e2e-agent-skills",
    "vendor/uxuiprinciples-agent-skills",
]

UI_ACCEPTANCE_GENERIC = (
    ROOT / "pipelines" / "pm-idea-to-mvp" / "assets" / "ui-acceptance-profiles" / "generic.yaml"
)

DUPLICATE_SCRIPT_ALLOWLIST = {"feishu_notify.py"}

ENTRY_DOC_VERSION = "9.1.0"

LEGACY_ROOT_DIRS = [
    "skills",
    "workflow",
    "design",
    "pm-idea-to-mvp",
    "productivity",
    "research",
]

SSOT_SCRIPT_NAMES = {"check_docs_ssot.py", "ui_acceptance.py"}
SKILL_TREE_PREFIXES = ("domains", "profiles")

REQUIRED_DOCS = [
    "docs/ARCHITECTURE.md",
    "docs/DEPLOY_CONVENTIONS.md",
    "docs/CODING_CONVENTIONS.md",
    "docs/GIT_WORKFLOW.md",
]

DEPLOY_TEMPLATE_PATHS = [
    "templates/hermes/config/deploy-servers.template.yaml",
    "pipelines/pm-idea-to-mvp/assets/deploy.template.yaml",
]


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    print(f"WARN: {msg}")


def load_yaml(path: Path) -> dict:
    if not path.exists():
        err(f"Missing: {path}")
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def check_skill_md(path: Path, label: str) -> None:
    skill = path / "SKILL.md" if path.is_dir() else path
    if not skill.exists():
        err(f"{label}: no SKILL.md at {path}")
        return
    text = skill.read_text(encoding="utf-8-sig")
    if not text.lstrip().startswith("---"):
        err(f"{label}: SKILL.md missing frontmatter")
        return
    end = text.find("---", 3)
    if end < 0:
        err(f"{label}: unclosed frontmatter")
        return
    fm = text[3:end]
    if "name:" not in fm:
        err(f"{label}: frontmatter missing name")
    if "description:" not in fm:
        err(f"{label}: frontmatter missing description")


def check_no_duplicate_script_names() -> None:
    root_names = {p.name for p in (ROOT / "scripts").glob("*.py")}
    pipe_dir = ROOT / "pipelines" / "pm-idea-to-mvp" / "scripts"
    if not pipe_dir.is_dir():
        return
    pipe_names = {p.name for p in pipe_dir.glob("*.py")}
    overlap = (root_names & pipe_names) - DUPLICATE_SCRIPT_ALLOWLIST
    if overlap:
        err(f"duplicate script names across scripts/ and pipeline scripts/: {sorted(overlap)}")


def check_no_tracked_bytecode() -> None:
    r = subprocess.run(
        ["git", "ls-files", "--", "*.pyc", "**/__pycache__/**"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if r.returncode != 0:
        return
    for line in r.stdout.splitlines():
        line = line.strip()
        if line:
            err(f"bytecode file should not be committed: {line}")


def check_entry_doc_versions() -> None:
    skill_md = ROOT / "pipelines" / "pm-idea-to-mvp" / "SKILL.md"
    if not skill_md.exists():
        return
    text = skill_md.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return
    fm = text.split("---", 2)[1]
    if f"version: {ENTRY_DOC_VERSION}" not in fm and f'version: "{ENTRY_DOC_VERSION}"' not in fm:
        err(f"SKILL.md frontmatter version should be {ENTRY_DOC_VERSION}")
    for rel in ("AGENTS.md", "README.md", "templates/cursor/AGENTS.md"):
        doc = ROOT / rel
        if doc.exists() and ENTRY_DOC_VERSION not in doc.read_text(encoding="utf-8"):
            err(f"{rel} missing pipeline version {ENTRY_DOC_VERSION}")


def check_pipeline_scripts_importable() -> None:
    scripts_dir = ROOT / "pipelines" / "pm-idea-to-mvp" / "scripts"
    for name in ("inner-loop-driver.py", "init-project.py", "consume-feedback.py"):
        r = subprocess.run(
            [sys.executable, str(scripts_dir / name), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            err(f"{name} --help failed: {(r.stderr or r.stdout)[:200]}")


def check_deploy_templates() -> None:
    registry_tpl = ROOT / "templates" / "hermes" / "config" / "deploy-servers.template.yaml"
    if registry_tpl.exists():
        text = registry_tpl.read_text(encoding="utf-8")
        if "key_path" not in text:
            err("deploy-servers.template.yaml missing key_path field")
        if "password_env" not in text:
            err("deploy-servers.template.yaml missing password_env field")

    deploy_tpl = ROOT / "pipelines" / "pm-idea-to-mvp" / "assets" / "deploy.template.yaml"
    if deploy_tpl.exists():
        text = deploy_tpl.read_text(encoding="utf-8")
        if "ssh_key" not in text:
            err("deploy.template.yaml missing secret_refs.ssh_key")


def check_required_docs() -> None:
    for rel in REQUIRED_DOCS:
        if not (ROOT / rel).exists():
            err(f"required doc missing: {rel}")


def check_no_legacy_root_dirs() -> None:
    for name in LEGACY_ROOT_DIRS:
        p = ROOT / name
        if p.is_dir():
            err(f"legacy root directory must be removed or migrated: {name}/")


def check_no_duplicate_ssot_scripts() -> None:
    for prefix in SKILL_TREE_PREFIXES:
        base = ROOT / prefix
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.name in SSOT_SCRIPT_NAMES:
                err(
                    f"duplicate SSOT script {path.name} under {prefix}/ — "
                    f"use scripts/{path.name} only"
                )


def check_no_removed_script_references() -> None:
    """Hard dependencies on removed v9 scripts should not appear in entry docs."""
    removed = ("stage-complete.py", "decompose-pm-pipeline.py", "goal-check.py", "validate-gates.py")
    skip_markers = ("不靠", "不再", "removed", "已删", "v9 无", "无 stage")
    for rel in ("AGENTS.md", "templates/cursor/AGENTS.md"):
        doc = ROOT / rel
        if not doc.exists():
            continue
        for i, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            if any(m in line for m in skip_markers):
                continue
            for script in removed:
                if script in line:
                    err(f"{rel}:{i} still references removed script {script}")
                    break


def main() -> int:
    marketplace = load_yaml(ROOT / "marketplace.yaml")
    platforms = load_yaml(ROOT / "platforms.yaml")
    manifest = load_yaml(ROOT / "borrowed" / "manifest.yaml")

    if not platforms.get("platforms"):
        err("platforms.yaml: empty platforms")

    if not (ROOT / "scenarios.yaml").exists():
        err("scenarios.yaml missing")

    for entry in marketplace.get("skills", {}).get("native", []):
        p = ROOT / entry["path"]
        check_skill_md(p, f"native:{entry['id']}")

    for entry in manifest.get("skills", []):
        source = entry.get("source", "")
        if source.startswith("phuryn/"):
            base = ROOT / manifest["sources"]["phuryn"]["path"]
            rel = source[len("phuryn/") :]
        elif source.startswith("anthropic/"):
            base = ROOT / manifest["sources"]["anthropic"]["path"]
            rel = source[len("anthropic/") :]
        else:
            err(f"borrowed:{entry['id']}: unknown source prefix")
            continue
        src = base / rel
        if entry.get("type") == "command":
            if not src.exists():
                err(f"borrowed:{entry['id']}: missing command {src}")
        else:
            check_skill_md(src, f"borrowed:{entry['id']}")

    debate_manifest = load_yaml(ROOT / "borrowed" / "manifest-debate.yaml")
    for entry in debate_manifest.get("skills", []):
        source = entry.get("source", "")
        if source.startswith("phuryn/"):
            base = ROOT / debate_manifest["sources"]["phuryn"]["path"]
            rel = source[len("phuryn/") :]
            src = base / rel
            check_skill_md(src, f"debate-borrowed:{entry['id']}")

    profile_paths = {
        "obsidian": [
            "profiles/obsidian/obsidian-todo-manager",
            "profiles/obsidian/obsidian-deepen-review",
            "profiles/obsidian/obsidian-note-summarizer",
        ],
        "deep-research": ["profiles/deep-research/industry-benchmark"],
        "hermes": [
            "profiles/hermes-plan/plan",
            "profiles/hermes-opencode/opencode",
        ],
        "hermes-kanban": [
            f"profiles/hermes-kanban/{p}"
            for p in [
                "pm-aligner", "pm-researcher", "pm-analyst", "pm-planner",
                "pm-builder", "pm-shipper", "pm-operator", "pm-growth",
            ]
        ],
        "ui-pro-max-full": ["profiles/ui-pro-max-full"],
        "playwright-e2e": ["profiles/playwright-e2e"],
        "ux-principles": ["profiles/ux-principles"],
    }
    for profile, paths in profile_paths.items():
        if profile not in marketplace.get("profiles", {}):
            err(f"profiles: {profile} in validator but missing from marketplace.yaml")
        for rel in paths:
            check_skill_md(ROOT / rel, f"profile:{profile}:{Path(rel).name}")

    if "debate" not in marketplace.get("profiles", {}):
        err("profiles: debate missing from marketplace.yaml")

    if not UI_ACCEPTANCE_GENERIC.exists():
        err("ui-acceptance-profiles: missing generic.yaml")

    for sub in VENDOR_SUBMODULES:
        p = ROOT / sub
        if not p.is_dir():
            warn(f"submodule path missing: {sub} (run git submodule update --init)")
            continue
        has_content = any(x.name != ".git" for x in p.iterdir())
        if not has_content:
            warn(f"submodule not initialized: {sub} (run git submodule update --init)")

    scripts_dir = ROOT / "pipelines" / "pm-idea-to-mvp" / "scripts"
    for name in PIPELINE_SCRIPTS:
        if not (scripts_dir / name).exists():
            err(f"required pipeline script missing: {name}")
    for name in PIPELINE_ASSETS:
        if not (scripts_dir / name).exists():
            err(f"required pipeline asset missing: {name}")

    for name in ROOT_SCRIPTS:
        if not (ROOT / "scripts" / name).exists():
            err(f"root script missing: {name}")

    check_required_docs()
    check_deploy_templates()
    check_no_legacy_root_dirs()
    check_no_duplicate_ssot_scripts()
    check_no_duplicate_script_names()
    check_no_tracked_bytecode()
    check_entry_doc_versions()
    check_no_removed_script_references()
    check_pipeline_scripts_importable()

    r2 = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "detect_agent_env.py"), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(ROOT),
    )
    if r2.returncode not in (0, 1):
        err("detect_agent_env.py --json failed unexpectedly")

    native_count = len(marketplace.get("skills", {}).get("native", []))
    borrowed_count = len(manifest.get("skills", []))
    counts = marketplace.get("counts", {})
    if counts.get("native") != native_count:
        err(f"counts.native={counts.get('native')} but found {native_count} native skills")
    if counts.get("borrowed") != borrowed_count:
        err(f"counts.borrowed={counts.get('borrowed')} but found {borrowed_count} borrowed skills")
    if counts.get("total") != native_count + borrowed_count:
        err(f"counts.total mismatch: expected {native_count + borrowed_count}")

    if ERRORS:
        print("VALIDATION FAILED:")
        for e in ERRORS:
            print(f"  - {e}")
        return 1
    print(f"OK: {native_count} native + {borrowed_count} borrowed skills; v9.1 pipeline validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
