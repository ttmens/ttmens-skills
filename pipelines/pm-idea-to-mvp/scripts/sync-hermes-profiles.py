#!/usr/bin/env python3
"""Sync pm-idea-to-mvp v7.1 into 9 Hermes pm-* profiles."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_paths import resolve_hermes_home, resolve_pipeline_root, resolve_projects_root, resolve_skills_root  # noqa: E402
from pipeline_version import PIPELINE_VERSION, load_pipeline_version  # noqa: E402

HERMES_HOME = resolve_hermes_home()
SKILLS_ROOT = resolve_skills_root()
PIPELINE_ROOT = resolve_pipeline_root()
PROJECTS_ROOT = resolve_projects_root()
PROFILES_ROOT = HERMES_HOME / "profiles"
AGENT_ROOT = HERMES_HOME / "hermes-agent"
SCRIPTS_DIR = PIPELINE_ROOT / "scripts"
STAGE_CARDS = PIPELINE_ROOT / "references" / "hermes-stage-cards"
RUNTIME_DOC = PIPELINE_ROOT / "references" / "runtime-kanban-v7.1.md"

STAGE_COMPLETE = SCRIPTS_DIR / "stage-complete.py"


def _stage_exit_cmd(stage: str, extra: str = "") -> str:
    proj = PROJECTS_ROOT / "pm-{slug}"
    cmd = (
        f'python "{STAGE_COMPLETE}" '
        f'--project-root "{proj}" --stage {stage} --task-id <this_task_id>{extra}'
    )
    return cmd

PIPELINE_HUB_ALLOWLIST = {
    "pm-idea-to-mvp",
    "grill-me",
    "grill-with-docs",
    "openspec",
    "opencode",
    "dogfood",
    "ui-ux-pro-max",
    "ui-acceptance-review",
    "pm-git-publish",
    "c4-architecture",
    "kw-deploy-checklist",
    "docs-hygiene",
    "test-driven-development",
    "writing-plans",
    "requesting-code-review",
    "user-journey",
    "open-design",
    "prd-red-team-panel",
    "subagent-driven-development",
    "industry-benchmark",
}

HUB_NOISE_SAMPLES = {"comfyui", "heartmula", "ascii-video", "audiocraft-audio-generation"}

PROFILE_CARDS: dict[str, list[str]] = {
    "pm-orchestrator": ["orchestrator.md"],
    "pm-aligner": ["align.md", "feishu-grill.md", "brownfield.md"],
    "pm-researcher": ["research.md"],
    "pm-analyst": ["analysis.md"],
    "pm-planner": ["spec.md"],
    "pm-builder": ["mvp-plan.md", "mvp-iter.md", "retro.md"],
    "pm-shipper": ["ship.md"],
    "pm-operator": ["operate.md"],
    "pm-growth": ["grow.md"],
}

SCRIPT_RE = re.compile(r"scripts/[a-z0-9_-]+\.py", re.I)

SOUL_EXIT: dict[str, str] = {
    "pm-aligner": _stage_exit_cmd("align", " --runtime"),
    "pm-researcher": _stage_exit_cmd("research"),
    "pm-analyst": _stage_exit_cmd("analysis"),
    "pm-planner": _stage_exit_cmd("spec", " --runtime"),
    "pm-builder": _stage_exit_cmd("mvp", " --runtime --verify-goals"),
    "pm-shipper": _stage_exit_cmd("ship", " --runtime"),
    "pm-operator": _stage_exit_cmd("operate"),
    "pm-growth": _stage_exit_cmd("grow"),
}


def read_version_from_pm_pipeline() -> str | None:
    pm_pipeline = AGENT_ROOT / "hermes_cli" / "pm_pipeline.py"
    if not pm_pipeline.exists():
        return None
    text = pm_pipeline.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'def load_pipeline_version\(\)', text)
    if m:
        return load_pipeline_version()
    m = re.search(r'PIPELINE_VERSION\s*=\s*["\']([^"\']+)["\']', text)
    return m.group(1) if m else None


def audit_scripts() -> list[str]:
    issues: list[str] = []
    skill_md = PIPELINE_ROOT / "SKILL.md"
    external_scripts = {
        "scripts/check_docs_ssot.py": SKILLS_ROOT / "scripts" / "check_docs_ssot.py",
        "scripts/ui_acceptance.py": SKILLS_ROOT / "scripts" / "ui_acceptance.py",
    }
    if skill_md.exists():
        refs = sorted(set(SCRIPT_RE.findall(skill_md.read_text(encoding="utf-8", errors="replace"))))
        optional_scripts = {"scripts/lighthouse_check.py"}
        for ref in refs:
            if ref in optional_scripts:
                continue
            if ref in external_scripts:
                if not external_scripts[ref].exists():
                    issues.append(f"MISSING external script: {ref}")
                continue
            p = PIPELINE_ROOT / ref
            if not p.exists():
                issues.append(f"MISSING script referenced in SKILL.md: {ref}")
    required = [
        "decompose-pm-pipeline.py",
        "stage-complete.py",
        "validate-gates.py",
        "goal-check.py",
        "progress-tracker.py",
        "kanban-status-report.py",
        "feishu-grill-preflight.py",
        "pipeline_version.py",
    ]
    for name in required:
        if not (SCRIPTS_DIR / name).exists():
            issues.append(f"MISSING required script: {name}")
    return issues


def audit_versions() -> list[str]:
    issues: list[str] = []
    ssot = load_pipeline_version()
    decompose_v = None
    decompose_path = SCRIPTS_DIR / "decompose-pm-pipeline.py"
    if decompose_path.exists():
        text = decompose_path.read_text(encoding="utf-8", errors="replace")
        if "from pipeline_version import PIPELINE_VERSION" in text:
            decompose_v = ssot
        else:
            m = re.search(r'PIPELINE_VERSION\s*=\s*["\']([^"\']+)["\']', text)
            decompose_v = m.group(1) if m else None
    gateway_v = read_version_from_pm_pipeline()
    versions = {"ssot": ssot, "decompose": decompose_v, "pm_pipeline": gateway_v}
    if len({v for v in versions.values() if v}) > 1:
        issues.append(f"VERSION MISMATCH: {versions}")
    trigger_path = PIPELINE_ROOT / "assets" / "trigger-routing.yaml"
    if trigger_path.exists():
        for line in trigger_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("version:"):
                tr_v = line.split(":", 1)[1].strip().strip('"').strip("'")
                if tr_v != ssot:
                    issues.append(f"trigger-routing version {tr_v} != SSOT {ssot}")
                break
    return issues


def build_skill_md(profile: str, cards: list[str]) -> str:
    body_parts = []
    for card in cards:
        p = STAGE_CARDS / card
        if p.exists():
            body_parts.append(p.read_text(encoding="utf-8").strip())
    body = "\n\n---\n\n".join(body_parts)
    card_names = ", ".join(cards)
    return f"""---
name: pm-idea-to-mvp
description: "Hermes stage slice v{PIPELINE_VERSION} for {profile} ({card_names})"
version: {PIPELINE_VERSION}
author: ttmens
platforms: [cli, hermes, linux, macos, windows]
metadata:
  hermes:
    tags: [pipeline, kanban, stage-card]
    profile: {profile}
    curator:
      skip: true
---

# pm-idea-to-mvp — {profile} (v{PIPELINE_VERSION} stage card)

> Thin worker slice. Full design: `skills/pipelines/pm-idea-to-mvp/SKILL.md`
> Runtime: `references/runtime-kanban-v6.0.md`
> Trigger routing SSOT: `assets/trigger-routing.yaml`

{body}
"""


def prune_hub_manifest(profile: str, dry_run: bool = False) -> dict:
    manifest = PROFILES_ROOT / profile / "skills" / ".bundled_manifest"
    if not manifest.exists():
        return {"profile": profile, "skipped": "no manifest"}
    lines = manifest.read_text(encoding="utf-8").splitlines()
    kept, removed = [], []
    for line in lines:
        if ":" not in line:
            continue
        name = line.split(":", 1)[0].strip()
        if name in PIPELINE_HUB_ALLOWLIST:
            kept.append(line)
        else:
            removed.append(name)
    if not dry_run and removed:
        manifest.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    return {"profile": profile, "kept": len(kept), "removed": len(removed), "removed_samples": removed[:8]}


def report_hub_noise() -> dict:
    stats = {}
    for profile in PROFILE_CARDS:
        manifest = PROFILES_ROOT / profile / "skills" / ".bundled_manifest"
        if not manifest.exists():
            continue
        names = [ln.split(":")[0] for ln in manifest.read_text(encoding="utf-8").splitlines() if ":" in ln]
        noise = [n for n in names if n in HUB_NOISE_SAMPLES]
        stats[profile] = {"total_bundled": len(names), "noise_samples": noise}
    return stats


def sync_profile(profile: str, dry_run: bool = False) -> dict:
    cards = PROFILE_CARDS[profile]
    prof_dir = PROFILES_ROOT / profile
    skill_dest = prof_dir / "skills" / "pm-idea-to-mvp" / "SKILL.md"
    runtime_dest = prof_dir / "skills" / "pipelines" / "pm-idea-to-mvp" / "references" / "runtime-kanban-v6.0.md"
    actions = []

    content = build_skill_md(profile, cards)
    if not dry_run:
        skill_dest.parent.mkdir(parents=True, exist_ok=True)
        skill_dest.write_text(content, encoding="utf-8")
        runtime_dest.parent.mkdir(parents=True, exist_ok=True)
        if RUNTIME_DOC.exists():
            shutil.copy2(RUNTIME_DOC, runtime_dest)
        for stale in runtime_dest.parent.glob("runtime-kanban-v5*.md"):
            stale.unlink(missing_ok=True)
    actions.append(f"SKILL.md v{PIPELINE_VERSION} ({len(content)} chars)")

    if profile in SOUL_EXIT and not dry_run:
        soul_path = prof_dir / "SOUL.md"
        if soul_path.exists():
            lines = soul_path.read_text(encoding="utf-8").splitlines()
            new_lines = []
            replaced = False
            for line in lines:
                if "stage-complete.py" in line and "python " in line:
                    new_lines.append(SOUL_EXIT[profile])
                    replaced = True
                else:
                    new_lines.append(line)
            text = "\n".join(new_lines)
            if not text.endswith("\n"):
                text += "\n"
            text = text.replace("v5.1", f"v{PIPELINE_VERSION}")
            text = text.replace("v6.0", f"v{PIPELINE_VERSION}")
            text = text.replace("v6.1", f"v{PIPELINE_VERSION}")
            soul_path.write_text(text, encoding="utf-8")
            actions.append("SOUL.md stage-complete path updated" if replaced else "SOUL.md (no stage-complete line)")

    return {"profile": profile, "actions": actions}


def main() -> None:
    parser = argparse.ArgumentParser(description=f"Sync pm-idea-to-mvp v{PIPELINE_VERSION} to Hermes profiles")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--profile", default="", help="Single profile to sync")
    parser.add_argument("--prune-hub", action="store_true", help="Trim .bundled_manifest to pipeline allowlist")
    args = parser.parse_args()

    report: dict = {"pipeline_version": PIPELINE_VERSION, "critical": [], "warnings": [], "profiles": []}
    report["critical"].extend(audit_scripts())
    report["critical"].extend(audit_versions())

    targets = [args.profile] if args.profile else sorted(PROFILE_CARDS.keys())
    for prof in targets:
        if prof not in PROFILE_CARDS:
            report["warnings"].append(f"Unknown profile: {prof}")
            continue
        report["profiles"].append(sync_profile(prof, dry_run=args.dry_run))
        if args.prune_hub:
            report.setdefault("hub_prune", []).append(prune_hub_manifest(prof, dry_run=args.dry_run))

    report["hub_noise"] = report_hub_noise()
    report["pass"] = len(report["critical"]) == 0
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
