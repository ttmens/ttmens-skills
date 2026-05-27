#!/usr/bin/env python3
"""UI acceptance checker for Fintech dashboard projects (stock-copilot profile)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


DISCLAIMER_PATTERNS = [
    r"不构成任何投资建议",
    r"仅供个人研究参考",
    r"股市有风险",
]
FORBIDDEN_PATTERNS = [r"必涨", r"必买", r"保证收益"]
CDN_PATTERNS = [
    r"cdn\.tailwindcss\.com",
    r"unpkg\.com",
    r"jsdelivr\.net",
    r"cdnjs\.cloudflare\.com",
]


@dataclass
class CheckResult:
    name: str
    max_score: int
    score: int
    critical: bool = False
    details: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        if self.critical and self.score < self.max_score:
            return False
        return self.score >= self.max_score * 0.6


@dataclass
class AcceptanceReport:
    project_root: Path
    mode: str
    results: list[CheckResult] = field(default_factory=list)

    @property
    def total_score(self) -> int:
        return sum(r.score for r in self.results)

    @property
    def max_score(self) -> int:
        return sum(r.max_score for r in self.results)

    @property
    def critical_fail(self) -> bool:
        return any(r.critical and r.score < r.max_score for r in self.results)

    @property
    def passed(self) -> bool:
        if self.mode == "quick":
            return self.total_score >= self.max_score * 0.7 and not self.critical_fail
        return self.total_score >= 85 and not self.critical_fail


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def file_hash(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_css_vars(css: str) -> set[str]:
    return set(re.findall(r"--([a-zA-Z0-9_-]+)\s*:", css))


def check_theme_sync(root: Path) -> CheckResult:
    r = CheckResult("design_token_sync", 15, 0, critical=False)
    src = root / "src" / "site" / "theme.css"
    dst = root / "docs" / "assets" / "theme.css"
    if not src.is_file():
        r.details.append("No src/site/theme.css — skip sync check")
        r.score = r.max_score
        return r
    if not dst.is_file():
        r.score = 0
        r.details.append("docs/assets/theme.css missing")
        return r
    if file_hash(src) == file_hash(dst):
        r.score = r.max_score
        r.details.append("theme.css in sync")
    else:
        r.score = 5
        r.details.append("src/site/theme.css != docs/assets/theme.css")
    design = root / "docs" / "DESIGN.md"
    if design.is_file():
        doc = read_text(design)
        vars_src = extract_css_vars(read_text(src))
        key_tokens = {"price-up", "price-down", "signal-bull", "signal-bear", "canvas-deep"}
        documented = sum(1 for t in key_tokens if t in doc or t.replace("-", "_") in doc)
        if documented >= 3:
            r.score = min(r.max_score, r.score + 5)
            r.details.append("DESIGN.md documents key semantic tokens")
        else:
            r.details.append("DESIGN.md missing A-share price vs signal color docs")
    return r


def check_compliance(root: Path) -> CheckResult:
    r = CheckResult("compliance", 10, 0, critical=True)
    index = root / "docs" / "index.html"
    html = read_text(index)
    if not html:
        r.details.append("docs/index.html not found")
        return r
    hits = sum(1 for p in DISCLAIMER_PATTERNS if re.search(p, html))
    if hits >= 2:
        r.score += 8
        r.details.append("Disclaimer patterns found")
    else:
        r.details.append(f"Disclaimer weak ({hits}/{len(DISCLAIMER_PATTERNS)})")
    bad = [p for p in FORBIDDEN_PATTERNS if re.search(p, html)]
    if bad:
        r.details.append(f"Forbidden phrases: {bad}")
    else:
        r.score += 2
        r.details.append("No forbidden investment phrases in index")
    return r


def check_performance(root: Path) -> CheckResult:
    r = CheckResult("performance", 5, 5)
    docs = root / "docs"
    if not docs.is_dir():
        return r
    for html in docs.rglob("*.html"):
        text = read_text(html)
        for pat in CDN_PATTERNS:
            if re.search(pat, text, re.I):
                r.score = 0
                r.details.append(f"CDN reference in {html.relative_to(root)}: {pat}")
                return r
    r.details.append("No external CDN in HTML")
    return r


def check_ia(root: Path) -> CheckResult:
    r = CheckResult("information_architecture", 20, 0)
    index = read_text(root / "docs" / "index.html")
    gen = read_text(root / "src" / "site" / "generator.py")
    signals = [
        ("signal-dashboard", "市场温度/信号分布区"),
        ("stock-card", "自选股卡片"),
        ("signal-badge", "信号标签"),
        ("decision-score", "综合评分"),
    ]
    found = 0
    for token, label in signals:
        if token in index or token in gen:
            found += 1
            r.details.append(f"Found {label}")
    r.score = min(r.max_score, found * 5)
    if "filter-bar" in index or "filter-bar" in gen:
        r.score = min(r.max_score, r.score + 4)
        r.details.append("Filter bar present")
    return r


def check_interaction(root: Path) -> CheckResult:
    r = CheckResult("interaction", 15, 0)
    app_js = read_text(root / "docs" / "app" / "app.js")
    index = read_text(root / "docs" / "index.html")
    checks = [
        ("filter-search", "搜索"),
        ("filter-signal", "信号筛选"),
        ("filter-sort", "排序"),
        ("aria-label", "无障碍标签"),
    ]
    combined = app_js + index
    for token, label in checks:
        if token in combined:
            r.score += 3
            r.details.append(label)
    watchlist = root / "docs" / "app" / "watchlist.html"
    stock = root / "docs" / "app" / "stock.html"
    if watchlist.is_file() and stock.is_file():
        r.score = min(r.max_score, r.score + 3)
        r.details.append("Detail + watchlist app pages exist")
    return r


def check_hybrid(root: Path) -> CheckResult:
    r = CheckResult("static_dynamic", 15, 0)
    config = read_text(root / "docs" / "app" / "config.js")
    app_js = read_text(root / "docs" / "app" / "app.js")
    if "API_BASE" in config or "STOCK_COPILOT" in config:
        r.score += 5
        r.details.append("API config present")
    if "fetch(" in app_js or "API_BASE" in app_js:
        r.score += 5
        r.details.append("Dynamic fetch in app.js")
    if "unavailable" in app_js.lower() or "empty" in app_js.lower() or "暂无" in app_js:
        r.score += 5
        r.details.append("Empty/unavailable handling hints")
    latest = root / "docs" / "data" / "latest.json"
    if latest.is_file():
        r.score = min(r.max_score, r.score + 2)
        r.details.append("Static latest.json present")
    return r


def check_responsive(root: Path) -> CheckResult:
    r = CheckResult("responsive", 10, 0)
    css = read_text(root / "docs" / "assets" / "theme.css")
    index = read_text(root / "docs" / "index.html")
    if "viewport" in index:
        r.score += 4
        r.details.append("viewport meta present")
    if "@media" in css:
        r.score += 6
        r.details.append("CSS media queries present")
    else:
        r.details.append("No @media in theme.css")
    return r


def check_a11y(root: Path) -> CheckResult:
    r = CheckResult("a11y", 10, 0)
    index = read_text(root / "docs" / "index.html")
    app = read_text(root / "docs" / "app" / "app.js")
    combined = index + app
    if "aria-label" in combined:
        r.score += 5
        r.details.append("aria-label usage")
    if ":focus" in read_text(root / "docs" / "assets" / "theme.css") or "focus-visible" in combined:
        r.score += 5
        r.details.append("Focus styles")
    return r


QUICK_CHECKS = [check_theme_sync, check_compliance, check_performance]
FULL_CHECKS = [
    check_ia,
    check_interaction,
    check_hybrid,
    check_theme_sync,
    check_responsive,
    check_a11y,
    check_compliance,
    check_performance,
]


def run_acceptance(project_root: Path, mode: str) -> AcceptanceReport:
    report = AcceptanceReport(project_root=project_root.resolve(), mode=mode)
    checks = QUICK_CHECKS if mode == "quick" else FULL_CHECKS
    for fn in checks:
        report.results.append(fn(project_root))
    return report


def write_markdown_report(report: AcceptanceReport, out_path: Path) -> None:
    lines = [
        "# UI Acceptance Report",
        "",
        f"- Mode: **{report.mode}**",
        f"- Score: **{report.total_score}/{report.max_score}**",
        f"- Result: **{'PASS' if report.passed else 'FAIL'}**",
        "",
        "## Dimensions",
        "",
        "| Dimension | Score | Notes |",
        "|-----------|-------|-------|",
    ]
    for r in report.results:
        notes = "; ".join(r.details[:3]) or "-"
        crit = " (critical)" if r.critical else ""
        lines.append(f"| {r.name}{crit} | {r.score}/{r.max_score} | {notes} |")
    lines.extend(["", "## Pre/Post snapshots", "", "- [ ] pre: docs/archive/YYYY-MM-DD-pre.html", "- [ ] post: docs/archive/YYYY-MM-DD-post.html", ""])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def print_console(report: AcceptanceReport) -> None:
    print(f"UI Acceptance ({report.mode}): {report.total_score}/{report.max_score}")
    for r in report.results:
        status = "ok" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.score}/{r.max_score}")
        for d in r.details[:2]:
            print(f"         - {d}")
    print("Result:", "PASS" if report.passed else "FAIL")


def main() -> int:
    parser = argparse.ArgumentParser(description="UI acceptance checker")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--write-report", type=Path, default=None, help="Write markdown report path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    mode = "full" if args.full else "quick"
    report = run_acceptance(args.project_root.resolve(), mode)

    if args.write_report:
        write_markdown_report(report, args.write_report)
    elif mode == "full":
        default_report = args.project_root / "docs" / "ui-acceptance-report.md"
        write_markdown_report(report, default_report)

    if args.json:
        print(json.dumps({
            "passed": report.passed,
            "score": report.total_score,
            "max_score": report.max_score,
            "mode": mode,
        }, indent=2))
    else:
        print_console(report)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
