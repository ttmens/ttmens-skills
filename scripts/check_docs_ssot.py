#!/usr/bin/env python3
"""
Documentation SSOT hygiene checker for product projects.

v6.2 enhancements:
- Cross-document consistency checks (tech stack, completion status)
- Detects conflicting claims between decisions.md and actual code
- Validates task completion claims against actual artifacts
- Pipeline-aware: checks goals/, PROGRESS.md, harness-rules.yaml existence
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Issue:
    severity: str  # error | warning | info
    rule: str
    message: str
    fixable: bool = False


@dataclass
class Report:
    project_root: Path
    issues: list[Issue] = field(default_factory=list)

    def add(self, severity: str, rule: str, message: str, fixable: bool = False) -> None:
        self.issues.append(Issue(severity, rule, message, fixable))

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def file_hash(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_status_files(docs: Path) -> list[Path]:
    design = docs / "design"
    candidates: list[Path] = []
    if design.is_dir():
        for p in design.glob("*CURRENT-STATUS*.md"):
            candidates.append(p)
    return sorted(candidates)


def check_duplicate_status(report: Report, docs: Path) -> None:
    files = find_status_files(docs)
    canonical = docs / "design" / "08-CURRENT-STATUS.md"
    duplicates: list[Path] = []
    for f in files:
        if "archive" in str(f):
            continue
        if f.resolve() == canonical.resolve():
            continue
        text = f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""
        if len(text) < 600 and ("已归档" in text or "08-CURRENT-STATUS" in text):
            continue
        duplicates.append(f)
    for f in duplicates:
        report.add(
            "error",
            "single-current-status",
            f"Duplicate CURRENT-STATUS: {f.relative_to(report.project_root)} (canonical: design/08-CURRENT-STATUS.md)",
            fixable=True,
        )


def check_design_md(report: Report, docs: Path) -> None:
    design_md = docs / "DESIGN.md"
    if not design_md.is_file():
        report.add("warning", "design-ssot", "Missing DESIGN.md — run ui-ux-pro-max maintenance mode")
        return
    theme_src = report.project_root / "src" / "site" / "theme.css"
    if theme_src.is_file():
        css_vars = set(re.findall(r"--([a-zA-Z0-9_-]+)\s*:", theme_src.read_text(encoding="utf-8", errors="replace")))
        doc_text = design_md.read_text(encoding="utf-8", errors="replace")
        key_tokens = {
            "price-up", "price-down", "signal-bull", "signal-bear",
            "canvas-deep", "accent-purple", "dim-hard", "font-cn", "border-hair",
        }
        documented = sum(1 for t in key_tokens if t in doc_text)
        if documented < len(key_tokens) - 2:
            missing = sorted(key_tokens - {t for t in key_tokens if t in doc_text})
            report.add(
                "warning",
                "design-token-drift",
                f"DESIGN.md missing key tokens: {', '.join(missing[:5])}",
            )


def check_theme_sync(report: Report, docs: Path, fix: bool) -> None:
    src = report.project_root / "src" / "site" / "theme.css"
    dst = docs / "assets" / "theme.css"
    if not src.is_file():
        return
    if not dst.is_file():
        report.add("error", "theme-sync", f"Missing published theme: {dst.relative_to(report.project_root)}", fixable=True)
        if fix:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            report.add("info", "theme-sync", f"Copied {src.name} → {dst}", fixable=False)
        return
    if file_hash(src) != file_hash(dst):
        report.add(
            "error",
            "theme-sync",
            "src/site/theme.css differs from docs/assets/theme.css",
            fixable=True,
        )
        if fix:
            shutil.copy2(src, dst)
            report.add("info", "theme-sync", "Synced theme.css to docs/assets/", fixable=False)


def check_ui_ux_style_banner(report: Report, docs: Path, fix: bool) -> None:
    path = docs / "UI-UX-Style.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    if "DESIGN.md" in text and ("deprecated" in text.lower() or "已废弃" in text or "SSOT" in text):
        return
    report.add(
        "warning",
        "deprecated-doc",
        "UI-UX-Style.md should point to docs/DESIGN.md as SSOT",
        fixable=True,
    )
    if fix:
        banner = (
            "> **已废弃** — 视觉 SSOT 见 [DESIGN.md](./DESIGN.md)。本文档仅作人类可读摘要。\n\n"
        )
        if not text.startswith(">"):
            path.write_text(banner + text, encoding="utf-8")
            report.add("info", "deprecated-doc", "Added deprecation banner to UI-UX-Style.md")


def fix_duplicate_status(report: Report, docs: Path) -> None:
    canonical = docs / "design" / "08-CURRENT-STATUS.md"
    archive = docs / "design" / "archive"
    archive.mkdir(parents=True, exist_ok=True)
    for f in find_status_files(docs):
        if "archive" in str(f):
            continue
        if f.resolve() == canonical.resolve():
            continue
        dest = archive / f.name
        if f.exists() and not dest.exists():
            shutil.move(str(f), str(dest))
            stub = docs / "design" / f.name
            stub.write_text(
                f"# 已归档\n\n请使用 [08-CURRENT-STATUS.md](./08-CURRENT-STATUS.md)。\n\n"
                f"历史版本: [archive/{f.name}](./archive/{f.name})\n",
                encoding="utf-8",
            )
            report.add("info", "single-current-status", f"Archived {f.name} → design/archive/")


def check_pipeline_governance(report: Report) -> None:
    """v6.2: Check that pipeline governance artifacts exist."""
    root = report.project_root

    # Check goals/ directory
    goals_dir = root / "goals"
    if not goals_dir.is_dir():
        report.add("warning", "pipeline-governance", "goals/ directory missing — stage goals not defined")
    else:
        expected_stages = ["align", "research", "analysis", "spec", "mvp", "ship", "retro"]
        missing = [s for s in expected_stages if not (goals_dir / f"{s}.yaml").exists()]
        if missing:
            report.add("warning", "pipeline-governance",
                       f"Missing goal files: {', '.join(missing)}")

    # Check PROGRESS.md
    if not (root / "PROGRESS.md").exists():
        report.add("warning", "pipeline-governance", "PROGRESS.md missing — no fine-grained progress tracking")

    # Check harness-rules.yaml
    if not (root / "harness-rules.yaml").exists():
        report.add("warning", "pipeline-governance", "harness-rules.yaml missing — no risk-based automation config")

    # Check feedback.jsonl
    if not (root / "feedback.jsonl").exists():
        report.add("info", "pipeline-governance", "feedback.jsonl missing — no cross-session feedback loop")


def check_tech_stack_consistency(report: Report) -> None:
    """v6.2: Detect conflicting tech stack claims across documents."""
    root = report.project_root

    # Collect tech stack mentions from key documents
    tech_mentions = {}  # doc_name -> set of tech keywords
    tech_patterns = {
        "postgresql": r"[Pp]ostgre[Ss]QL|[Pp]ostgres",
        "sqlite": r"[Ss][Qq][Ll][Ii]te",
        "mysql": r"[Mm][Yy][Ss][Qq][Ll]",
        "mongodb": r"[Mm]ongo[DB]*",
        "redis": r"[Rr]edis",
        "docker": r"[Dd]ocker",
        "pm2": r"PM2|[Pp]rocess [Mm]anager",
        "nextjs": r"[Nn]ext\.?[Jj][Ss]",
        "fastify": r"[Ff]astify",
        "express": r"[Ee]xpress\.?[Jj][Ss]?",
    }

    docs_to_check = [
        "decisions.md", "CONTEXT.md", "02-analysis.md",
        "03-prd.md", "DEPLOYMENT.md", "PRODUCT-DESIGN.md",
    ]

    for doc_name in docs_to_check:
        doc_path = root / doc_name
        if not doc_path.exists():
            continue
        content = doc_path.read_text(encoding="utf-8", errors="replace")
        found = set()
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, content):
                found.add(tech)
        if found:
            tech_mentions[doc_name] = found

    # Check for database conflicts (most common issue from pm-knowledge-platform)
    db_techs = {"postgresql", "sqlite", "mysql", "mongodb"}
    db_claims = {}
    for doc, techs in tech_mentions.items():
        db_found = techs & db_techs
        if db_found:
            db_claims[doc] = db_found

    if len(db_claims) >= 2:
        # Check if different docs claim different databases
        all_dbs = set()
        for dbs in db_claims.values():
            all_dbs.update(dbs)
        if len(all_dbs) > 1:
            # This is a potential conflict
            details = "; ".join(f"{doc}: {', '.join(dbs)}" for doc, dbs in db_claims.items())
            report.add("error", "tech-stack-conflict",
                       f"Database technology conflict across documents: {details}. "
                       f"Ensure decisions.md is the SSOT and other docs reference it.")


def check_task_completion_claims(report: Report) -> None:
    """v6.2: Verify that tasks marked complete in openspec/tasks.md have actual artifacts."""
    root = report.project_root
    tasks_file = root / "openspec" / "tasks.md"
    if not tasks_file.exists():
        return

    content = tasks_file.read_text(encoding="utf-8", errors="replace")

    # Find tasks marked as complete [x]
    completed_tasks = re.findall(r'- \[x\]\s+\*\*(T\d+)', content)
    if not completed_tasks:
        return

    # Check for common artifacts that should exist if tasks are truly complete
    expected_artifacts = {
        "04-mvp/README.md": "MVP implementation",
        "04-mvp/DESIGN.md": "Design system tokens",
        "04-mvp/UX-REVIEW.md": "UX acceptance review",
    }

    if len(completed_tasks) >= 3:  # If 3+ tasks are marked complete
        missing = []
        for artifact, desc in expected_artifacts.items():
            if not (root / artifact).exists():
                missing.append(f"{artifact} ({desc})")
        if missing:
            report.add("error", "task-completion-claim",
                       f"{len(completed_tasks)} tasks marked complete but artifacts missing: "
                       f"{', '.join(missing[:3])}. Verify actual completion before marking [x].")


def run_checks(project_root: Path, fix: bool) -> Report:
    report = Report(project_root=project_root.resolve())
    docs = project_root / "docs"

    # v6.2: Pipeline governance checks (always run)
    check_pipeline_governance(report)

    # v6.2: Cross-document consistency (always run)
    check_tech_stack_consistency(report)
    check_task_completion_claims(report)

    if not docs.is_dir():
        report.add("warning", "docs-root", "No docs/ directory — skipping project-specific checks")
        return report

    check_duplicate_status(report, docs)
    check_design_md(report, docs)
    check_theme_sync(report, docs, fix)
    check_ui_ux_style_banner(report, docs, fix)

    if fix:
        fix_duplicate_status(report, docs)

    return report


def print_report(report: Report, as_json: bool) -> None:
    if as_json:
        payload = {
            "ok": report.ok,
            "project_root": str(report.project_root),
            "issues": [
                {"severity": i.severity, "rule": i.rule, "message": i.message, "fixable": i.fixable}
                for i in report.issues
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    print(f"Docs hygiene: {report.project_root}")
    for i in report.issues:
        icon = {"error": "❌", "warning": "⚠️", "info": "✅"}.get(i.severity, "•")
        print(f"  {icon} [{i.rule}] {i.message}")
    print("Result:", "PASS" if report.ok else "FAIL")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check documentation SSOT hygiene")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--fix", action="store_true", help="Apply safe auto-fixes")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = run_checks(args.project_root.resolve(), args.fix)
    print_report(report, args.json)
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
