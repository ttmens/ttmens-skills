#!/usr/bin/env python3
"""Build static GitHub Pages report (docs/index.html) for a PM pipeline run."""
from __future__ import annotations

import argparse
import html
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
import sys

sys.path.insert(0, str(SCRIPT_DIR))
from github_helpers import GITHUB_OWNER, pages_url, repo_url  # noqa: E402

ARTIFACTS = [
    ("RUN.md", "运行说明"),
    ("00-brief.md", "Brief"),
    ("CONTEXT.md", "Context"),
    ("decisions.md", "Decisions"),
    ("01-research.md", "Research"),
    ("01b-benchmark.md", "Benchmark"),
    ("02-analysis.md", "Analysis"),
    ("03b-user-journey.md", "UserJourney"),
    ("03-prd.md", "PRD"),
    ("05-retro.md", "Retro"),
    ("06-refine-retro.md", "RefineRetro"),
    ("RUNBOOK.md", "Ship"),
    ("07-ops-notes.md", "Operate"),
    ("06-growth.md", "Grow"),
    ("docs/ui-acceptance-report.md", "UIAcceptance"),
]

C4_FILES = [
    ("architecture/c4-context.md", "C4 Context"),
    ("architecture/c4-container.md", "C4 Container"),
    ("architecture/c4-component.md", "C4 Component"),
]


def git_head(run_dir: Path) -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=run_dir, text=True, stderr=subprocess.DEVNULL)
        return out.strip()
    except Exception:
        return "n/a"


def load_gates(run_dir: Path) -> dict:
    p = run_dir / "gates.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"overall": "unknown", "stages": {}}


def md_block(path: Path) -> str:
    if not path.exists():
        return "<p><em>Not generated yet.</em></p>"
    text = path.read_text(encoding="utf-8")
    return f'<pre class="md-source">{html.escape(text)}</pre>'


def c4_section(run_dir: Path) -> str:
    parts = []
    for rel, label in C4_FILES:
        p = run_dir / rel
        if p.exists():
            parts.append(f"<h3>{html.escape(label)}</h3>{md_block(p)}")
    if not parts:
        return "<p><em>C4 architecture not generated yet.</em></p>"
    return "\n".join(parts)


def ux_review_section(run_dir: Path) -> str:
    p = run_dir / "04-mvp/UX-REVIEW.md"
    if not p.exists():
        return "<p><em>UX-REVIEW not generated yet.</em></p>"
    return md_block(p)


def mvp_section(run_dir: Path) -> str:
    readme = run_dir / "04-mvp/README.md"
    if not readme.exists():
        return "<p><em>MVP not built yet.</em></p>"
    text = readme.read_text(encoding="utf-8")
    ux = ux_review_section(run_dir)
    files = []
    mvp = run_dir / "04-mvp"
    for p in sorted(mvp.rglob("*")):
        if p.is_file() and p.name not in {".gitkeep"}:
            rel = p.relative_to(mvp).as_posix()
            if len(files) < 40:
                files.append(rel)
    file_list = "".join(f"<li>{html.escape(f)}</li>" for f in files)
    return f"""
    <pre class="md-source">{html.escape(text)}</pre>
    <h3>UX Review</h3>
    {ux}
    <h3>Files</h3><ul>{file_list}</ul>
    <p><em>Flask MVP is not executed on GitHub Pages. Run locally per README.</em></p>
    """


def sync_prototype(run_dir: Path, docs_dir: Path) -> bool:
    src = run_dir / "02b-prototype"
    dst = docs_dir / "prototype"
    if not (src / "index.html").exists():
        return False
    import shutil

    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return True


def openspec_section(run_dir: Path) -> str:
    parts = []
    for rel in ("openspec/proposal.md", "openspec/design.md", "openspec/tasks.md"):
        p = run_dir / rel
        if p.exists():
            parts.append(f"<h3>{html.escape(rel)}</h3>{md_block(p)}")
    specs = run_dir / "openspec/specs"
    if specs.exists():
        for p in sorted(specs.glob("*.md")):
            rel = p.relative_to(run_dir).as_posix()
            parts.append(f"<h3>{html.escape(rel)}</h3>{md_block(p)}")
    if not parts:
        return "<p><em>OpenSpec not generated yet.</em></p>"
    return "\n".join(parts)


def prototype_section(has_proto: bool) -> str:
    if has_proto:
        return '<iframe class="proto-frame" src="prototype/index.html" title="prototype"></iframe>'
    return "<p><em>No static prototype (02b-prototype/index.html) yet.</em></p>"


def gate_badges(gates: dict) -> str:
    stages = gates.get("stages", {})
    if not stages:
        return '<span class="badge unknown">gates not validated</span>'
    parts = []
    for name, data in stages.items():
        cls = "pass" if data.get("pass") else "fail"
        parts.append(f'<span class="badge {cls}">{html.escape(name)}</span>')
    overall = gates.get("overall", "unknown")
    parts.append(f'<span class="badge overall {overall}">overall: {html.escape(str(overall))}</span>')
    return " ".join(parts)


def build_html(run_dir: Path, slug: str) -> str:
    gates = load_gates(run_dir)
    repo_name = f"pm-{slug}"
    pages = pages_url(repo_name)
    repo = repo_url(repo_name)
    head = git_head(run_dir)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    docs_dir = run_dir / "docs"
    has_proto = sync_prototype(run_dir, docs_dir)

    tabs = []
    panels = []
    for fname, label in ARTIFACTS:
        tid = fname.replace(".", "-")
        tabs.append(f'<button class="tab" data-tab="{tid}">{label}</button>')
        panels.append(f'<div class="panel" id="{tid}">{md_block(run_dir / fname)}</div>')

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PM Pipeline — {html.escape(slug)}</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; background:#0f1419; color:#e7ecf3; }}
    body {{ margin:0; padding:16px; max-width:960px; margin-inline:auto; }}
    h1 {{ font-size:1.4rem; margin-bottom:8px; }}
    .meta {{ color:#9aa7b5; font-size:.9rem; margin-bottom:16px; }}
    .meta a {{ color:#6cb6ff; }}
    .badges {{ margin:12px 0 20px; display:flex; flex-wrap:wrap; gap:8px; }}
    .badge {{ padding:4px 10px; border-radius:999px; font-size:.8rem; background:#243044; }}
    .badge.pass {{ background:#1f4d2e; color:#9be7b0; }}
    .badge.fail {{ background:#5a2323; color:#ffb4b4; }}
    .badge.overall.pass {{ background:#2d4a7a; }}
    .tabs {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px; }}
    .tab {{ background:#1a2332; color:#dce6f2; border:1px solid #2b3b52; padding:8px 12px; border-radius:8px; cursor:pointer; }}
    .tab.active {{ background:#2d4a7a; border-color:#4d7ec2; }}
    .panel {{ display:none; background:#151d29; border:1px solid #2b3b52; border-radius:12px; padding:16px; }}
    .panel.active {{ display:block; }}
    .md-render {{ line-height:1.55; }}
    .md-render h2 {{ margin-top:1.2em; }}
    pre.md-source {{ display:none; }}
    .proto-frame {{ width:100%; min-height:420px; border:1px solid #2b3b52; border-radius:8px; background:#fff; }}
    section {{ margin-top:24px; }}
  </style>
</head>
<body>
  <h1>PM Idea → MVP — {html.escape(slug)}</h1>
  <div class="meta">
    Repo: <a href="{html.escape(repo)}">{html.escape(repo)}</a> ·
    Pages: <a href="{html.escape(pages)}">{html.escape(pages)}</a><br/>
    Commit: {html.escape(head)} · Built: {now}
  </div>
  <div class="badges">{gate_badges(gates)}</div>

  <div class="tabs" id="tabs">
    {''.join(tabs)}
    <button class="tab" data-tab="openspec-panel">OpenSpec</button>
    <button class="tab" data-tab="c4-panel">C4</button>
    <button class="tab" data-tab="journey-panel">Journey</button>
    <button class="tab" data-tab="mvp-panel">MVP</button>
    <button class="tab" data-tab="proto-panel">Prototype</button>
  </div>

  {''.join(panels)}
  <div class="panel" id="openspec-panel">{openspec_section(run_dir)}</div>
  <div class="panel" id="c4-panel">{c4_section(run_dir)}</div>
  <div class="panel" id="journey-panel">{md_block(run_dir / "03b-user-journey.md")}</div>
  <div class="panel" id="mvp-panel">{mvp_section(run_dir)}</div>
  <div class="panel" id="ship-panel">
    <h3>RUNBOOK</h3>{md_block(run_dir / "RUNBOOK.md")}
    <h3>UI Acceptance (full)</h3>{md_block(run_dir / "docs/ui-acceptance-report.md")}
    <h3>Ops Notes</h3>{md_block(run_dir / "07-ops-notes.md")}
    <h3>Growth</h3>{md_block(run_dir / "06-growth.md")}
  </div>
  <div class="panel" id="proto-panel">{prototype_section(has_proto)}</div>

  <script>
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.panel');
    function activate(id) {{
      tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === id));
      panels.forEach(p => p.classList.toggle('active', p.id === id));
    }}
    tabs.forEach(t => t.addEventListener('click', () => activate(t.dataset.tab)));
    document.querySelectorAll('.md-source').forEach((pre, i) => {{
      const panel = pre.parentElement;
      const div = document.createElement('div');
      div.className = 'md-render';
      div.innerHTML = marked.parse(pre.textContent);
      panel.insertBefore(div, pre);
    }});
    activate(tabs[0]?.dataset.tab || 'RUN-md');
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="Run directory (git repo root)")
    parser.add_argument("--slug", default=None, help="Repo slug without pm- prefix")
    args = parser.parse_args()

    run_dir = Path(args.run).resolve()
    slug = args.slug or run_dir.name.replace("pm-", "", 1)
    docs_dir = run_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "assets").mkdir(exist_ok=True)

    html_out = build_html(run_dir, slug)
    (docs_dir / "index.html").write_text(html_out, encoding="utf-8")
    print(f"Wrote {docs_dir / 'index.html'}")
    print(f"Pages URL: {pages_url(f'pm-{slug}')}")


if __name__ == "__main__":
    main()
