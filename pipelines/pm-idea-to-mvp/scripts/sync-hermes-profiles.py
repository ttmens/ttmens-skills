#!/usr/bin/env python3
"""
sync-hermes-profiles.py — Re-bundle pm-idea-to-mvp v6 into 9 Hermes profiles.

Runs skill-self-audit steps 1-3 (script existence, version parity) and writes
thin stage-card SKILL.md + runtime-kanban-v6.0.md into each pm-* profile.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parents[4]  # .../hermes-data
if not (HERMES_HOME / "profiles").exists():
    HERMES_HOME = Path(rstr(Path(__file__).resolve().parents[3]))

SKILLS_ROOT = HERMES_HOME / "skills"
PIPELINE_ROOT = SKILLS_ROOT / "pipelines" / "pm-idea-to-mvp"
PROFILES_ROOT = HERMES_HOME / "profiles"
AGENT_ROOT = HERMES_HOME / "hermes-agent"
SCRIPTS_DIR = PIPELINE_ROOT / "scripts"
STAGE_CARDS = PIPELINE_ROOT / "references" / "hermes-stage-cards"
RUNTIME_DOC = PIPELINE_ROOT / "references" / "runtime-kanban-v6.0.md"

PIPELINE_HUB_ALLOWLIST = {
    "pm-idea-to-mvp", "grill-me", "grill-with-docs", "openspec", "opencode", "dogfood",
    "ui-ux-pro-max", "ui-acceptance-review", "pm-git-publish", "kanban-orchestrator",
    "kanban-worker", "c4-architecture", "kw-deploy-checklist", "docs-hygiene",
    "test-driven-development", "writing-plans", "requesting-code-review",
}

HUB_NOISE_SAMPLES = {"comfyui", "heartmula", "ascii-video", "audiocraft-audio-generation"}


def report_hub_noise() -> dict:
    """P2 audit: count non-pipeline hub skills (informational, no auto-prune)."""
    stats = {}
    for profile in PROFILE_CARDS:
        manifest = PROFILES_ROOT / profile / "skills" / ".bundled_manifest"
        if not manifest.exists():
            continue
        names = [ln.split(":")[0] for ln in manifest.read_text(encoding="utf-8").splitlines() if ":" in ln]
        noise = [n for n in names if n in HUB_NOISE_SAMPLES]
        stats[profile] = {"total_bundled": len(names), "noise_samples": noise}
    return stats


PROFILE_CARDS: dict[str, list[str]] = {
    "pm-orchestrator": ["orchestrator.md"],
    "pm-aligner": ["align.md"],
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
    "pm-aligner": (
        "python D:\\hermes-data\\skills\\pipelines\\pm-idea-to-mvp\\scripts\\stage-complete.py "
        "--project-root D:\\workspace\\projects\\pm-{slug} --stage align --task-id <this_task_id> --runtime"
    ),
    "pm-researcher": (
        "python D:\\hermes-data\\skills\\pipelines\\pm-idea-to-mvp\\scripts\\stage-complete.py "
        "--project-root D:\\workspace\\projects\\pm-{slug} --stage research --task-id <this_task_id>"
    ),
    "pm-analyst": (
        "python D:\\hermes-data\\skills\\pipelines\\pm-idea-to-mvp\\scripts\\stage-complete.py "
        "--project-root D:\\workspace\\projects\\pm-{slug} --stage analysis --task-id <this_task_id>"
    ),
    "pm-planner": (
        "python D:\\hermes-data\\skills\\pipelines\\pm-idea-to-mvp\\scripts\\stage-complete.py "
        "--project-root D:\\workspace\\projects\\pm-{slug} --stage spec --task-id <this_task_id> --runtime"
    ),
    "pm-builder": (
        "python D:\\hermes-data\\skills\\pipelines\\pm-idea-to-mvp\\scripts\\stage-complete.py "
        "--project-root D:\\workspace\\projects\\pm-{slug} --stage mvp --task-id <this_task_id> --runtime --verify-goals"
    ),
    "pm-shipper": (
        "python D:\\hermes-data\\skills\\pipelines\\pm-idea-to-mvp\\scripts\\stage-complete.py "
        "--project-root D:\\workspace\\projects\\pm-{slug} --stage ship --task-id <this_task_id> --runtime"
    ),
    "pm-operator": (
        "python D:\\hermes-data\\skills\\pipelines\\pm-idea-to-mvp\\scripts\\stage-complete.py "
        "--project-root D:\\workspace\\projects\\pm-{slug} --stage operate --task-id <this_task_id>"
    ),
    "pm-growth": (
        "python D:\\hermes-data\\skills\\pipelines\\pm-idea-to-mvp\\scripts\\stage-complete.py "
        "--project-root D:\\workspace\\projects\\pm-{slug} --stage grow --task-id <this_task_id>"
    ),
}


def read_version_from_script(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
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
        for ref in refs:
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
    ]
    for name in required:
        if not (SCRIPTS_DIR / name).exists():
            issues.append(f"MISSING required script: {name}")
    return issues


def audit_versions() -> list[str]:
    issues: list[str] = []
    decompose_v = read_version_from_script(SCRIPTS_DIR / "decompose-pm-pipeline.py")
    stage_v = read_version_from_script(SCRIPTS_DIR / "stage-complete.py")
    pm_pipeline = AGENT_ROOT / "hermes_cli" / "pm_pipeline.py"
    gateway_v = read_version_from_script(pm_pipeline) if pm_pipeline.exists() else None

    versions = {"decompose": decompose_v, "stage-complete": stage_v, "pm_pipeline": gateway_v}
    uniq = {v for v in versions.values() if v}
    if len(uniq) > 1:
        issues.append(f"VERSION MISMATCH: {versions}")
    if decompose_v != "6.0.0":
        issues.append(f"decompose expected 6.0.0, got {decompose_v}")
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
description: "Hermes stage slice v6.0 for {profile} ({card_names})"
version: 6.0.0
author: ttmens
platforms: [cli, hermes, linux, macos, windows]
metadata:
  hermes:
    tags: [pipeline, kanban, stage-card]
    profile: {profile}
---

# pm-idea-to-mvp — {profile} (v6.0 stage card)

> Thin worker slice. Full design doc: canonical `SKILL.md` in skills tree.
> Runtime: `references/runtime-kanban-v6.0.md`

{body}
"""


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
        shutil.copy2(RUNTIME_DOC, runtime_dest)
        # Remove stale v5.1 runtime doc if present
        stale = runtime_dest.parent / "runtime-kanban-v5.1.md"
        if stale.exists():
            stale.unlink()
    actions.append(f"SKILL.md ({len(content)} chars, cards: {cards})")

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
            text = text.replace("v5.1", "v6.0")
            text = text.replace("9 Kanban subtasks", "12 Kanban subtasks (MVP inner loop)")
            text = text.replace("Fixed 9-child graph", "Fixed 12-child graph (outer + MVP inner loop)")
            soul_path.write_text(text, encoding="utf-8")
            actions.append("SOUL.md stage-complete path → v6" if replaced else "SOUL.md (no stage-complete line)")

    return {"profile": profile, "actions": actions}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync pm-idea-to-mvp v6 to Hermes profiles")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--profile", default="", help="Single profile to sync")
    args = parser.parse_args()

    report: dict = {"critical": [], "warnings": [], "profiles": []}
    report["critical"].extend(audit_scripts())
    report["critical"].extend(audit_versions())

    targets = [args.profile] if args.profile else sorted(PROFILE_CARDS.keys())
    for prof in targets:
        if prof not in PROFILE_CARDS:
            report["warnings"].append(f"Unknown profile: {prof}")
            continue
        report["profiles"].append(sync_profile(prof, dry_run=args.dry_run))

    report["hub_noise"] = report_hub_noise()
    report["pass"] = len(report["critical"]) == 0
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
