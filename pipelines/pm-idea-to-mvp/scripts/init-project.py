#!/usr/bin/env python3
"""
init-project.py — Initialize all governance artifacts for a new pm-{slug} project.

v7.2: Creates the complete set of governance files that were previously missing
when decompose-pm-pipeline.py was not used. Ensures debates/, feedback.jsonl,
gates.json, and all goals/*.yaml files exist from day one.

Usage:
  python init-project.py --project-root <path> --slug <slug>
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_paths import resolve_pipeline_root

from pipeline_version import PIPELINE_VERSION


def init_templates(project_root: Path, slug: str, pipeline_root: Path) -> list[str]:
    """Copy SSOT templates: deploy.yaml, artifacts.manifest.yaml, design-system.yaml."""
    created: list[str] = []
    assets = pipeline_root / "assets"
    mappings = [
        ("deploy.template.yaml", "deploy.yaml", {"{slug}": slug}),
        ("artifacts.manifest.template.yaml", "artifacts.manifest.yaml", {}),
        ("design-system.template.yaml", "design-system.yaml", {"{slug}": slug}),
    ]
    for tpl_name, dest_name, repl in mappings:
        tpl = assets / tpl_name
        dest = project_root / dest_name
        if not tpl.exists() or dest.exists():
            continue
        text = tpl.read_text(encoding="utf-8")
        for k, v in repl.items():
            text = text.replace(k, v)
        dest.write_text(text, encoding="utf-8")
        created.append(dest_name)
    runs_dir = project_root / "runs"
    if not runs_dir.exists():
        runs_dir.mkdir(parents=True)
        created.append("runs/")
    return created


def init_governance(project_root: Path, slug: str) -> list[str]:
    """Initialize all governance artifacts. Returns list of created files."""
    created = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # 1. Create goals/ directory with all stage files
    goals_dir = project_root / "goals"
    if not goals_dir.exists():
        goals_dir.mkdir(parents=True)
        created.append("goals/")

    stages = ["align", "research", "analysis", "spec", "mvp", "ship", "retro"]
    for stage in stages:
        goal_file = goals_dir / f"{stage}.yaml"
        if not goal_file.exists():
            goal_file.write_text(
                f"# Stage: {stage}\n"
                f"stage: {stage}\n"
                f"goals:\n"
                f"  - id: {stage[0].upper()}{stage[1:3]}1\n"
                f"    description: '{stage} stage artifacts exist'\n"
                f"    type: file_exists\n"
                f"    target: 'TODO'\n",
                encoding="utf-8"
            )
            created.append(f"goals/{stage}.yaml")

    # 2. Create debates/ directory
    debates_dir = project_root / "debates"
    if not debates_dir.exists():
        debates_dir.mkdir(parents=True)
        created.append("debates/")

    # 3. Create feedback.jsonl
    fb_path = project_root / "feedback.jsonl"
    if not fb_path.exists():
        fb_path.write_text(
            json.dumps({"ts": now, "source": "init", "stage": "init",
                        "signal": "project initialized", "status": "recorded"}) + "\n",
            encoding="utf-8"
        )
        created.append("feedback.jsonl")

    # 4. Create gates.json from template
    gates_path = project_root / "gates.json"
    if not gates_path.exists():
        template = {
            "version": PIPELINE_VERSION,
            "mode": "loop",
            "stages": {
                s: {"status": "pending", "checkpoint": "human" if s in ("align", "ship") else "auto"}
                for s in ["brief", "align", "research", "analysis", "spec", "mvp", "ship", "operate", "grow", "retro"]
            }
        }
        gates_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
        created.append("gates.json")

    # 5. Create harness-rules.yaml
    harness_path = project_root / "harness-rules.yaml"
    if not harness_path.exists():
        harness_path.write_text(
            f"# Harness Rules v7.2\n"
            f"version: '{PIPELINE_VERSION}'\n"
            f"project:\n"
            f"  slug: '{slug}'\n"
            f"  tech_stack: node\n"
            f"  language: zh-CN\n"
            f"runtime:\n"
            f"  test_cmd: 'npm test'\n"
            f"  build_cmd: 'npm run build'\n"
            f"  health_url: ''\n"
            f"  workdir: '.'\n"
            f"human_checkpoints:\n"
            f"  - align\n"
            f"  - ship\n"
            f"inner_loop:\n"
            f"  max_iterations: 3\n",
            encoding="utf-8"
        )
        created.append("harness-rules.yaml")

    # 6. Create PROGRESS.md
    progress_path = project_root / "PROGRESS.md"
    if not progress_path.exists():
        progress_path.write_text(
            f"# 项目进度：{slug}\n\n"
            f"最后更新：{now}（by init-project.py）\n\n"
            f"## 阶段状态\n\n"
            f"| Stage | Status |\n|-------|--------|\n"
            f"| brief | ⏳ todo |\n| align | ⏳ todo |\n"
            f"| research | ⏳ todo |\n| analysis | ⏳ todo |\n"
            f"| spec | ⏳ todo |\n| mvp | ⏳ todo |\n"
            f"| ship | ⏳ todo |\n| operate | ⏳ todo |\n"
            f"| grow | ⏳ todo |\n| retro | ⏳ todo |\n",
            encoding="utf-8"
        )
        created.append("PROGRESS.md")

    # 7. Create evolution-notes.md
    evo_path = project_root / "evolution-notes.md"
    if not evo_path.exists():
        evo_path.write_text(
            f"# 进化笔记 — {slug}\n\n"
            f"记录流水线执行过程中的经验教训和改进提案。\n\n"
            f"---\n\n*初始化: {now}*\n",
            encoding="utf-8"
        )
        created.append("evolution-notes.md")

    return created


def init_playwright_e2e(project_root: Path, skills_root: Path) -> list[str]:
    """Scaffold e2e/ Playwright smoke tests from pipeline templates."""
    created: list[str] = []
    tpl_dir = skills_root / "pipelines" / "pm-idea-to-mvp" / "assets" / "templates"
    e2e_dir = project_root / "e2e"
    if not e2e_dir.exists():
        e2e_dir.mkdir(parents=True)
        created.append("e2e/")

    mappings = [
        ("playwright.config.template.ts", "playwright.config.ts"),
        ("e2e-smoke.template.spec.ts", "smoke.spec.ts"),
    ]
    for tpl_name, dest_name in mappings:
        tpl = tpl_dir / tpl_name
        dest = e2e_dir / dest_name
        if tpl.exists() and not dest.exists():
            shutil.copy2(tpl, dest)
            created.append(f"e2e/{dest_name}")

    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pkg = {}
        scripts = pkg.setdefault("scripts", {})
        if "test:e2e" not in scripts:
            scripts["test:e2e"] = "playwright test"
            pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            created.append("package.json (test:e2e script)")
    return created


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize governance artifacts for pm-{slug} project (v7.2)"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--slug", required=True, help="Project slug (e.g., knowledge-platform)")
    parser.add_argument(
        "--profile",
        action="append",
        default=[],
        choices=["playwright-e2e"],
        help="Optional profile hooks (e.g. playwright-e2e scaffolds e2e/)",
    )
    parser.add_argument("--skills-root", type=Path, default=None, help="ttmens-skills root for templates")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    created = init_governance(project_root, args.slug)
    pipeline_root = resolve_pipeline_root()
    created.extend(init_templates(project_root, args.slug, pipeline_root))

    skills_root = args.skills_root
    if skills_root is None:
        skills_root = Path(__file__).resolve().parents[3]
    if "playwright-e2e" in args.profile or (project_root / "package.json").exists():
        created.extend(init_playwright_e2e(project_root, skills_root))

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "project_root": str(project_root),
        "slug": args.slug,
        "created": created,
        "total_created": len(created),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Initialized {len(created)} governance artifacts:")
        for f in created:
            print(f"  ✅ {f}")
        if not created:
            print("  (all artifacts already exist)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
