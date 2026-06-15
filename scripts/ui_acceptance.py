#!/usr/bin/env python3
"""UI acceptance checker — profile-driven (generic | stock-copilot | auto)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

SKILLS_ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = SKILLS_ROOT / "pipelines" / "pm-idea-to-mvp" / "assets" / "ui-acceptance-profiles"

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
    profile_id: str
    results: list[CheckResult] = field(default_factory=list)
    pass_threshold_full: int = 85
    pass_threshold_quick_ratio: float = 0.70

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
            return self.total_score >= self.max_score * self.pass_threshold_quick_ratio and not self.critical_fail
        return self.total_score >= self.pass_threshold_full and not self.critical_fail


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def file_hash(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def glob_text(root: Path, patterns: list[str]) -> str:
    parts: list[str] = []
    for pat in patterns:
        for p in root.glob(pat):
            if p.is_file():
                parts.append(read_text(p))
    return "\n".join(parts)


def glob_files(root: Path, patterns: list[str]) -> list[Path]:
    out: list[Path] = []
    for pat in patterns:
        for p in root.glob(pat):
            if p.is_file():
                out.append(p)
    return out


def load_yaml_file(path: Path) -> dict[str, Any]:
    if yaml is None or not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def merge_profile(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if k == "checks" and isinstance(v, dict):
            checks = dict(out.get("checks") or {})
            for ck, cv in v.items():
                if isinstance(cv, dict) and isinstance(checks.get(ck), dict):
                    merged = dict(checks[ck])
                    merged.update(cv)
                    checks[ck] = merged
                else:
                    checks[ck] = cv
            out["checks"] = checks
        else:
            out[k] = v
    return out


def resolve_profile(project_root: Path, profile_arg: str) -> dict[str, Any]:
    project_cfg = load_yaml_file(project_root / "ui-acceptance.yaml")
    if profile_arg == "auto":
        profile_id = project_cfg.get("profile") or project_cfg.get("id") or "generic"
    else:
        profile_id = profile_arg

    base_path = PROFILES_DIR / f"{profile_id}.yaml"
    if not base_path.is_file():
        base_path = PROFILES_DIR / "generic.yaml"

    profile = load_yaml_file(base_path)
    extends = profile.get("extends")
    if extends and extends != profile.get("id"):
        parent = load_yaml_file(PROFILES_DIR / f"{extends}.yaml")
        profile = merge_profile(parent, profile)

    if project_cfg:
        profile = merge_profile(profile, project_cfg)

    profile.setdefault("id", profile_id)
    return profile


# --- Generic profile checks ---


def generic_design_tokens(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("design_token_sync", 15, 0)
    design_rel = cfg.get("design_md", "04-mvp/DESIGN.md")
    design = root / design_rel
    if not design.is_file():
        r.details.append(f"{design_rel} missing")
        return r
    doc = read_text(design)
    keys = cfg.get("min_palette_keys", ["primary", "surface"])
    found = sum(1 for k in keys if k in doc.lower())
    r.score = min(r.max_score, found * 5)
    r.details.append(f"DESIGN.md palette keys {found}/{len(keys)}")
    css_files = glob_files(root, cfg.get("css_globs", ["04-mvp/**/*.css"]))
    if css_files:
        r.score = min(r.max_score, r.score + 5)
        r.details.append(f"{len(css_files)} CSS file(s) found")
    else:
        r.details.append("No CSS files matched css_globs")
    return r


def generic_journey(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("journey_coverage", 10, 0)
    jpath = root / cfg.get("file", "03b-user-journey.md")
    if not jpath.is_file():
        r.details.append("User journey file missing")
        return r
    text = read_text(jpath)
    r.score += 5
    r.details.append("Journey file present")
    markers = cfg.get("screen_map_markers", ["屏幕", "screen"])
    if any(m in text for m in markers):
        r.score = r.max_score
        r.details.append("Screen mapping section found")
    else:
        r.details.append("Screen mapping markers not found")
    return r


def generic_ia(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("information_architecture", 20, 0)
    html_text = glob_text(root, cfg.get("html_globs", ["04-mvp/**/*.html", "docs/**/*.html"]))
    if not html_text.strip():
        r.details.append("No HTML files found")
        return r
    r.score += 5
    r.details.append("HTML artifacts present")

    if cfg.get("required_paths_from_journey"):
        journey = read_text(root / "03b-user-journey.md")
        screens = re.findall(r"\|\s*([^\|]+?)\s*\|", journey)
        screens = [s.strip() for s in screens if s.strip() and s.strip() not in ("屏幕", "Screen", "------")]
        hits = sum(1 for s in screens[:8] if len(s) > 1 and s.lower() in html_text.lower())
        r.score += min(15, hits * 3)
        r.details.append(f"Journey screens referenced in HTML: {hits}")
    else:
        r.score = min(r.max_score, r.score + 10)
    return r


def generic_interaction(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("interaction", 15, 0)
    combined = glob_text(root, cfg.get("html_globs", [])) + glob_text(root, cfg.get("js_globs", []))
    hints = cfg.get("min_interactive_hints", ["button", "form"])
    per = max(1, 15 // max(len(hints), 1))
    for h in hints:
        if h.lower() in combined.lower():
            r.score += per
            r.details.append(h)
    r.score = min(r.max_score, r.score)
    return r


def generic_static_dynamic(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("static_dynamic", 15, 0)
    js = glob_text(root, cfg.get("js_globs", []))
    html = glob_text(root, cfg.get("html_globs", []))
    combined = js + html
    for hint in cfg.get("dynamic_hints", ["fetch("]):
        if hint in combined:
            r.score += 5
            r.details.append(f"Dynamic hint: {hint}")
            break
    for hint in cfg.get("empty_state_hints", ["empty", "暂无"]):
        if hint.lower() in combined.lower():
            r.score += 5
            r.details.append("Empty/unavailable handling hints")
            break
    if combined.strip():
        r.score = min(r.max_score, max(r.score, 5))
        r.details.append("UI source files present")
    return r


def generic_compliance(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("compliance", 10, 0, critical=True)
    if not cfg.get("enabled"):
        r.score = r.max_score
        r.details.append("Compliance check disabled for profile")
        return r
    index = root / cfg.get("index_html", "docs/index.html")
    html = read_text(index)
    if not html:
        r.details.append("Index HTML not found")
        return r
    disclaimers = cfg.get("disclaimer_patterns", [])
    hits = sum(1 for p in disclaimers if re.search(re.escape(p), html))
    if hits >= max(1, len(disclaimers) // 2):
        r.score += 8
        r.details.append("Disclaimer patterns found")
    forbidden = cfg.get("forbidden_patterns", [])
    bad = [p for p in forbidden if re.search(re.escape(p), html)]
    if bad:
        r.details.append(f"Forbidden phrases: {bad}")
    else:
        r.score += 2
        r.details.append("No forbidden phrases")
    return r


def generic_performance(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("performance", 5, 5)
    if not cfg.get("forbid_cdn", True):
        return r
    for html in glob_files(root, cfg.get("scan_globs", ["**/*.html"])):
        text = read_text(html)
        for pat in CDN_PATTERNS:
            if re.search(pat, text, re.I):
                r.score = 0
                r.details.append(f"CDN in {html.relative_to(root)}: {pat}")
                return r
    r.details.append("No external CDN in scanned HTML")
    return r


def generic_responsive(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("responsive", 10, 0)
    html = glob_text(root, cfg.get("html_globs", []))
    css = glob_text(root, cfg.get("css_globs", []))
    if "viewport" in html.lower():
        r.score += 4
        r.details.append("viewport meta present")
    if "@media" in css:
        r.score += 6
        r.details.append("CSS media queries present")
    else:
        r.details.append("No @media in CSS")
    return r


def generic_a11y(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("a11y", 10, 0)
    combined = (
        glob_text(root, cfg.get("html_globs", []))
        + glob_text(root, cfg.get("js_globs", []))
        + glob_text(root, cfg.get("css_globs", []))
    )
    if "aria-label" in combined or "aria-labelledby" in combined:
        r.score += 5
        r.details.append("ARIA labels present")
    if ":focus" in combined or "focus-visible" in combined:
        r.score += 5
        r.details.append("Focus styles")
    return r


# --- Legacy stock-copilot checks ---


def legacy_theme_sync(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("design_token_sync", 15, 0)
    src = root / cfg.get("src_theme", "src/site/theme.css")
    dst = root / cfg.get("dst_theme", "docs/assets/theme.css")
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
    design = root / cfg.get("design_md", "docs/DESIGN.md")
    if design.is_file():
        doc = read_text(design)
        key_tokens = set(cfg.get("key_tokens", []))
        documented = sum(1 for t in key_tokens if t in doc or t.replace("-", "_") in doc)
        if documented >= max(1, len(key_tokens) * 3 // 5):
            r.score = min(r.max_score, r.score + 5)
            r.details.append("DESIGN.md documents key semantic tokens")
        else:
            r.details.append("DESIGN.md missing key token docs")
    return r


def legacy_ia(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("information_architecture", 20, 0)
    index = read_text(root / "docs" / "index.html")
    gen = read_text(root / "src" / "site" / "generator.py")
    combined = index + gen
    for item in cfg.get("signals", []):
        token = item.get("id", item) if isinstance(item, dict) else item
        label = item.get("label", token) if isinstance(item, dict) else token
        if token in combined:
            r.score = min(r.max_score, r.score + 5)
            r.details.append(f"Found {label}")
    for token in cfg.get("extra_tokens", []):
        if token in combined:
            r.score = min(r.max_score, r.score + 4)
            r.details.append(f"{token} present")
    return r


def legacy_interaction(root: Path, cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("interaction", 15, 0)
    app_js = read_text(root / "docs" / "app" / "app.js")
    index = read_text(root / "docs" / "index.html")
    combined = app_js + index
    for item in cfg.get("tokens", []):
        token = item.get("id", item) if isinstance(item, dict) else item
        label = item.get("label", token) if isinstance(item, dict) else token
        if token in combined:
            r.score += 3
            r.details.append(label)
    pages = cfg.get("app_pages", [])
    if pages and all((root / rel).is_file() for rel in pages):
        r.score = min(r.max_score, r.score + 3)
        r.details.append("Detail + watchlist app pages exist")
    return r


def legacy_hybrid(root: Path, _cfg: dict[str, Any]) -> CheckResult:
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


def legacy_a11y(root: Path, _cfg: dict[str, Any]) -> CheckResult:
    r = CheckResult("a11y", 10, 0)
    index = read_text(root / "docs" / "index.html")
    app = read_text(root / "docs" / "app" / "app.js")
    combined = index + app
    css = read_text(root / "docs" / "assets" / "theme.css")
    if "aria-label" in combined:
        r.score += 5
        r.details.append("aria-label usage")
    if ":focus" in css or "focus-visible" in combined:
        r.score += 5
        r.details.append("Focus styles")
    return r


def legacy_responsive(root: Path, _cfg: dict[str, Any]) -> CheckResult:
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


def build_checks(profile: dict[str, Any], mode: str) -> list[Callable[[Path], CheckResult]]:
    checks_cfg = profile.get("checks") or {}
    engine = profile.get("engine")

    if engine == "legacy" or profile.get("id") == "stock-copilot":
        dt = checks_cfg.get("design_tokens") or {}
        ia = checks_cfg.get("ia") or {}
        inter = checks_cfg.get("interaction") or {}
        comp = checks_cfg.get("compliance") or {}
        perf = checks_cfg.get("performance") or {"forbid_cdn": True, "scan_globs": ["docs/**/*.html"]}

        quick = [
            lambda root: legacy_theme_sync(root, dt),
            lambda root: generic_compliance(root, comp),
            lambda root: generic_performance(root, perf),
        ]
        full = [
            lambda root: legacy_ia(root, ia),
            lambda root: legacy_interaction(root, inter),
            lambda root: legacy_hybrid(root, {}),
            lambda root: legacy_theme_sync(root, dt),
            lambda root: legacy_responsive(root, {}),
            lambda root: legacy_a11y(root, {}),
            lambda root: generic_compliance(root, comp),
            lambda root: generic_performance(root, perf),
        ]
        return quick if mode == "quick" else full

    dt = checks_cfg.get("design_tokens") or {}
    journey = checks_cfg.get("journey") or {}
    ia = checks_cfg.get("ia") or {}
    inter = checks_cfg.get("interaction") or {}
    hybrid = checks_cfg.get("static_dynamic") or {}
    comp = checks_cfg.get("compliance") or {}
    perf = checks_cfg.get("performance") or {}
    resp = checks_cfg.get("responsive") or {}
    a11y = checks_cfg.get("a11y") or {}

    quick = [
        lambda root: generic_design_tokens(root, dt),
        lambda root: generic_compliance(root, comp),
        lambda root: generic_performance(root, perf),
    ]
    full = [
        lambda root: generic_journey(root, journey),
        lambda root: generic_ia(root, ia),
        lambda root: generic_interaction(root, inter),
        lambda root: generic_static_dynamic(root, hybrid),
        lambda root: generic_design_tokens(root, dt),
        lambda root: generic_responsive(root, resp),
        lambda root: generic_a11y(root, a11y),
        lambda root: generic_compliance(root, comp),
        lambda root: generic_performance(root, perf),
    ]
    return quick if mode == "quick" else full


def run_acceptance(project_root: Path, mode: str, profile: dict[str, Any]) -> AcceptanceReport:
    thresholds = profile.get("pass_threshold") or {}
    report = AcceptanceReport(
        project_root=project_root.resolve(),
        mode=mode,
        profile_id=str(profile.get("id", "generic")),
        pass_threshold_full=int(thresholds.get("full_score", 85)),
        pass_threshold_quick_ratio=float(thresholds.get("quick_ratio", 0.70)),
    )
    for fn in build_checks(profile, mode):
        report.results.append(fn(project_root))
    return report


def write_markdown_report(report: AcceptanceReport, out_path: Path) -> None:
    lines = [
        "# UI Acceptance Report",
        "",
        f"- Profile: **{report.profile_id}**",
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
    lines.extend([
        "",
        "## Pre/Post snapshots",
        "",
        "- [ ] pre: docs/ui-snapshots/pre.png",
        "- [ ] post: docs/ui-snapshots/post.png",
        "",
    ])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def print_console(report: AcceptanceReport) -> None:
    print(f"UI Acceptance ({report.mode}, profile={report.profile_id}): {report.total_score}/{report.max_score}")
    for r in report.results:
        status = "ok" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.score}/{r.max_score}")
        for d in r.details[:2]:
            print(f"         - {d}")
    print("Result:", "PASS" if report.passed else "FAIL")


def main() -> int:
    parser = argparse.ArgumentParser(description="UI acceptance checker")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--profile", choices=["auto", "generic", "stock-copilot"], default="auto")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--write-report", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.project_root.resolve()
    profile = resolve_profile(root, args.profile)
    mode = "full" if args.full else "quick"
    report = run_acceptance(root, mode, profile)

    if args.write_report:
        write_markdown_report(report, args.write_report)
    elif mode == "full":
        write_markdown_report(report, root / "docs" / "ui-acceptance-report.md")

    if args.json:
        print(json.dumps({
            "passed": report.passed,
            "score": report.total_score,
            "max_score": report.max_score,
            "mode": mode,
            "profile": report.profile_id,
        }, indent=2))
    else:
        print_console(report)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
