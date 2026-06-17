#!/usr/bin/env python3
"""PM Pipeline v8.0 structured plain-text notification builder (SSOT)."""
from __future__ import annotations

import os
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from pipeline_paths import resolve_projects_root  # noqa: E402
from pipeline_version import PIPELINE_VERSION  # noqa: E402

GITHUB_OWNER = os.environ.get("PM_GITHUB_OWNER", "ttmens")
PIPELINE_INDEX_URL = f"https://{GITHUB_OWNER}.github.io/pm-pipeline-index/"

# v8.0 merged stage labels
STAGE_LABEL = {
    "align": "需求对齐",
    "discover": "调研与论证",
    "design": "原型与规格",
    "mvp": "MVP 构建",
    "ship": "部署发布",
    "retro": "复盘进化",
    "import": "导入仓库",
    "research": "调研",
    "analysis": "论证",
    "spec": "规格",
    "operate": "运维",
    "grow": "增长",
}

STAGE_FROM_TITLE = {
    "grill": "align",
    "对齐": "align",
    "align": "align",
    "调研": "discover",
    "research": "discover",
    "论证": "discover",
    "analysis": "discover",
    "discover": "discover",
    "prd": "design",
    "spec": "design",
    "design": "design",
    "原型": "design",
    "mvp": "mvp",
    "ship": "ship",
    "部署": "ship",
    "operate": "retro",
    "运维": "retro",
    "grow": "retro",
    "增长": "retro",
    "retro": "retro",
    "进化": "retro",
    "棕地": "align",
}


def artifact_tab_id(rel_path: str) -> str:
    """Stable Pages tab anchor id (must match build-run-report.py)."""
    return rel_path.replace("/", "-").replace(".", "-").strip("-") or "index"


def pages_url(slug: str, artifact_path: str | None = None) -> str:
    s = slug.removeprefix("pm-")
    base = f"https://{GITHUB_OWNER}.github.io/pm-{s}/"
    if artifact_path:
        return f"{base}#{artifact_tab_id(artifact_path)}"
    return base


def repo_url(slug: str) -> str:
    s = slug.removeprefix("pm-")
    return f"https://github.com/{GITHUB_OWNER}/pm-{s}"


def project_dir(slug: str) -> Path:
    s = slug.removeprefix("pm-")
    return resolve_projects_root() / f"pm-{s}"


def extract_slug_from_task(title: str = "", body: str = "") -> str:
    combined = f"{title}\n{body}"
    m = re.search(r"Project root:\s*[^\s/\\]+[/\\]pm-([\w-]+)", combined, re.I)
    if m:
        return m.group(1)
    m = re.search(r"projects[/\\]pm-([\w-]+)", combined, re.I)
    if m:
        return m.group(1)
    m = re.search(r"—\s*([\w-]+)\s*$", title.strip())
    if m:
        return m.group(1).removeprefix("pm-")
    m = re.search(r"pm-([\w-]+)", combined, re.I)
    if m:
        return m.group(1)
    return ""


def infer_stage_from_task(title: str = "", body: str = "") -> str:
    m = re.search(r"stage:\s*(\w+)", body, re.I)
    if m:
        return m.group(1).lower()
    lower = title.lower()
    for key, stage in STAGE_FROM_TITLE.items():
        if key in lower:
            return stage
    return ""


def resolve_task_context(title: str = "", body: str = "") -> tuple[str, Path | None, str]:
    slug = extract_slug_from_task(title, body)
    stage = infer_stage_from_task(title, body)
    proj = project_dir(slug) if slug else None
    if proj and not proj.exists():
        proj = None
    return slug, proj, stage


def load_manifest(project_root: Path) -> dict:
    path = project_root / "artifacts.manifest.yaml"
    if not path.exists() or yaml is None:
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _deliverables_for_stage(manifest: dict, stage: str) -> list[dict]:
    stages = manifest.get("stages") or {}
    norm = stage.lower()
    if norm.startswith("mvp"):
        norm = "mvp"
    data = stages.get(norm) or stages.get(stage) or {}
    items = data.get("deliverables") or []
    return [x for x in items if isinstance(x, dict) and x.get("path")]


def check_deliverable(project_root: Path, rel_path: str, min_lines: int | None = None) -> dict:
    target = project_root / rel_path
    if rel_path.endswith("/"):
        target = project_root / rel_path.rstrip("/")
        ok = target.is_dir() and any(target.iterdir()) if target.exists() else False
        detail = "dir ok" if ok else "missing/empty"
        return {"path": rel_path, "ok": ok, "detail": detail}
    if not target.exists():
        return {"path": rel_path, "ok": False, "detail": "未生成"}
    if target.is_dir():
        ok = any(target.rglob("*"))
        return {"path": rel_path, "ok": ok, "detail": "dir ok" if ok else "empty dir"}
    lines = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
    if min_lines and lines < min_lines:
        return {"path": rel_path, "ok": False, "detail": f"{lines} 行 (< {min_lines})"}
    return {"path": rel_path, "ok": True, "detail": f"{lines} 行"}


def format_deliverable_section(project_root: Path, stage: str) -> str:
    manifest = load_manifest(project_root)
    items = _deliverables_for_stage(manifest, stage)
    if not items:
        return ""
    lines = ["", "本阶段产物:"]
    for item in items:
        rel = str(item.get("path", ""))
        min_lines = item.get("min_lines")
        chk = check_deliverable(project_root, rel, min_lines)
        mark = "✓" if chk["ok"] else "✗"
        lines.append(f"  {mark} {rel} ({chk['detail']})")
    return "\n".join(lines)


def format_deploy_summary(project_root: Path) -> str:
    path = project_root / "deploy.yaml"
    if not path.exists() or yaml is None:
        return ""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return ""
    try:
        from deploy_servers import resolve_deploy
        deploy = resolve_deploy(raw)
    except Exception:
        deploy = raw
    host = (deploy.get("host") or "").strip()
    if not host:
        return ""
    port = deploy.get("port") or 22
    user = (deploy.get("user") or "").strip()
    label = deploy.get("label") or deploy.get("server") or ""
    procs = deploy.get("processes") or {}
    proc_names = ", ".join(
        str(v.get("name", k)) for k, v in procs.items() if isinstance(v, dict)
    )[:120]
    lines = ["", "部署目标 (ship):"]
    if label:
        lines.append(f"  服务器: {label}")
    lines.append(f"  host: {host}:{port} user: {user or '?'}")
    if proc_names:
        lines.append(f"  processes: {proc_names}")
    return "\n".join(lines)


def format_view_section(project_root: Path, slug: str, stage: str) -> str:
    s = slug.removeprefix("pm-")
    manifest = load_manifest(project_root)
    items = _deliverables_for_stage(manifest, stage)
    first_path = items[0]["path"] if items else None
    if first_path and first_path.endswith("/"):
        first_path = None
    pages = pages_url(s, first_path)
    return "\n".join([
        "",
        "查看:",
        f"  Pages  {pages}",
        f"  Repo   {repo_url(s)}",
        f"  本地   {project_root}",
        f"  索引   {PIPELINE_INDEX_URL}",
    ])


def format_checkpoint_section(task_id: str) -> str:
    if not task_id:
        return ""
    return "\n".join([
        "",
        "需确认 — 请核实产物后继续",
        f"飞书回复: 确认 {task_id}",
        f"或发送: 跳过 {task_id}",
    ])


def build_pipeline_progress_table(
    slug: str,
    stages: list[dict],
) -> str:
    """v8.0: Build structured plain-text pipeline progress table."""
    lines = [
        f"── PM Pipeline: {slug} ──",
    ]
    for st in stages:
        name = st.get("stage", "?")
        label = STAGE_LABEL.get(name, name)
        status = st.get("status", "todo")
        marker = {"done": "✅", "running": "↔ ", "blocked": "⏸", "todo": "⏳"}.get(status, "  ")
        inline = f" {marker} {label}"
        if status == "blocked":
            reason = st.get("reason", "")
            inline += f" (需确认: {reason[:40]})" if reason else " (需确认)"
        if status == "done" and st.get("completed_at"):
            inline += f"  {st['completed_at'][:16]}"
        lines.append(inline)
    lines.append("──")
    return "\n".join(lines)


def build_deploy_checkpoint_msg(slug: str, pages_url_val: str, lighthouse_url: str = "") -> str:
    """v8.0: Build deploy checkpoint notification for Feishu."""
    s = slug.removeprefix("pm-")
    lines = [
        f"── 检查点: 部署确认 — {s} ──",
        f"RUNBOOK.md 已生成并通过验证。",
    ]
    if pages_url_val:
        lines.append(f"GitHub Pages: {pages_url_val}")
    if lighthouse_url:
        lines.append(f"Lighthouse: {lighthouse_url}")
    lines.extend([
        "",
        "回复:",
        "  '确认部署' → 执行部署",
        "  '拒绝: 原因' → 暂停并记录原因",
        "  '查看 RUNBOOK' → 发送 RUNBOOK 内容",
        "──",
    ])
    return "\n".join(lines)


def build_stage_message(
    stage: str,
    status: str,
    project_root: str | Path,
    task_id: str = "",
    extra: str = "",
    *,
    human_checkpoint: bool = False,
) -> str:
    """v8.0: Clean stage completion notification."""
    root = Path(project_root).resolve()
    slug = root.name.removeprefix("pm-")
    label = STAGE_LABEL.get(stage, stage)
    lines = [
        f"PM Pipeline v{PIPELINE_VERSION}",
        f"阶段: {label} ({stage})",
        f"状态: {status}",
        f"项目: pm-{slug}",
    ]
    if task_id:
        lines.append(f"任务: {task_id}")
    lines.append(format_deliverable_section(root, stage))
    if stage == "ship":
        lines.append(format_deploy_summary(root))
    lines.append(format_view_section(root, slug, stage))
    if human_checkpoint or "checkpoint" in status.lower() or "block" in status.lower():
        lines.append(format_checkpoint_section(task_id))
    if extra:
        lines.extend(["", extra])
    return "\n".join(line for line in lines if line is not None)


def build_kanban_event_message(
    kind: str,
    task_id: str,
    title: str = "",
    *,
    reason: str = "",
    handoff: str = "",
    body: str = "",
    slug: str = "",
    project_root: Path | None = None,
    stage: str = "",
    assignee_prefix: str = "",
) -> str:
    """v8.0: Build structured Kanban event notification."""
    if not slug and (title or body or reason):
        slug, project_root, stage = resolve_task_context(title, body or reason)
    if project_root is None and slug:
        candidate = project_dir(slug)
        project_root = candidate if candidate.exists() else None

    prefix = assignee_prefix or ""
    if kind == "completed":
        head = f"{prefix}已完成 {task_id} — {title[:120]}"
        if handoff:
            head += handoff if handoff.startswith("\n") else f"\n{handoff[:200]}"
    elif kind == "blocked":
        head = f"{prefix}已暂停 {task_id}"
        if reason:
            head += f": {reason[:160]}"
        if title:
            head += f"\n{title[:120]}"
    elif kind == "gave_up":
        head = f"{prefix}放弃 {task_id} (多次失败)"
        if reason:
            head += f"\n{reason[:200]}"
    elif kind == "crashed":
        head = f"{prefix}{task_id} worker 崩溃, 调度器将重试"
    elif kind == "timed_out":
        head = f"{prefix}{task_id} 超时, 将重试"
    else:
        head = f"{prefix}{task_id} — {kind}"

    parts = [head]

    if project_root and project_root.exists():
        st = stage or infer_stage_from_task(title, body or reason)
        if st:
            parts.append(format_deliverable_section(project_root, st))
        parts.append(format_view_section(project_root, slug or project_root.name.removeprefix("pm-"), st or "align"))
        if kind == "blocked":
            parts.append(format_checkpoint_section(task_id))
    elif slug:
        parts.extend([
            "",
            "查看:",
            f"  Pages  {pages_url(slug)}",
            f"  Repo   {repo_url(slug)}",
        ])
        if kind == "blocked":
            parts.append(format_checkpoint_section(task_id))

    return "\n".join(p for p in parts if p)
