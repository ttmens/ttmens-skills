#!/usr/bin/env python3
"""
feishu-grill-preflight.py — Feishu 1-2 round grill before Kanban decompose (v6.1.0).

Subcommands:
  start   --session-key KEY --text "产品想法：..." --slug SLUG
  reply   --session-key KEY --text "用户回答"
  status  --session-key KEY
  cancel  --session-key KEY
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_VERSION = "7.1.0"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_paths import resolve_hermes_home, resolve_pipeline_root, resolve_projects_root  # noqa: E402

PROJECTS_ROOT = resolve_projects_root()
HERMES_HOME = resolve_hermes_home()
GRILL_DIR = HERMES_HOME / "feishu-grill"
PIPELINE_ROOT = resolve_pipeline_root()


def _load_grill_config() -> dict:
    default = {
        "max_rounds": 2,
        "questions": [
            {"id": "success_metric", "prompt": "【Grill 1/2】成功标准是什么？怎样算做完？"},
            {"id": "non_goals", "prompt": "【Grill 2/2】明确不做什么？（非目标、边界）"},
        ],
        "skip_if_brief_enriched": True,
    }
    path = PIPELINE_ROOT / "assets" / "trigger-routing.yaml"
    if not path.exists():
        return default
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        grill = data.get("grill") or {}
        return {
            "max_rounds": int(grill.get("max_rounds", 2)),
            "questions": grill.get("questions") or default["questions"],
            "skip_if_brief_enriched": bool(grill.get("skip_if_brief_enriched", True)),
        }
    except Exception:
        return default


def _session_path(session_key: str) -> Path:
    safe = re.sub(r"[^\w.-]", "_", session_key)[:120]
    GRILL_DIR.mkdir(parents=True, exist_ok=True)
    return GRILL_DIR / f"{safe}.json"


def _load_session(session_key: str) -> dict | None:
    p = _session_path(session_key)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _save_session(session_key: str, data: dict) -> None:
    _session_path(session_key).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _brief_has_grill(project_root: Path) -> bool:
    brief = project_root / "00-brief.md"
    if not brief.exists():
        return False
    text = brief.read_text(encoding="utf-8")
    return "## 飞书 Grill" in text and "成功标准" in text


def _write_enriched_brief(project_root: Path, title: str, idea_text: str, answers: dict) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    brief = project_root / "00-brief.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if brief.exists():
        content = brief.read_text(encoding="utf-8")
    else:
        content = f"# 产品想法\n\n**创建时间**: {now}\n\n## 标题\n{title}\n\n## 描述\n{idea_text}\n"
    grill_block = f"""
## 飞书 Grill

**成功标准**（Grill 1）:
{answers.get('success_metric', '').strip() or '（未答）'}

**非目标**（Grill 2）:
{answers.get('non_goals', '').strip() or '（未答）'}

**Grill 完成时间**: {now}
"""
    if "## 飞书 Grill" in content:
        content = re.sub(r"\n## 飞书 Grill[\s\S]*", grill_block, content)
    else:
        content = content.rstrip() + "\n" + grill_block
    brief.write_text(content, encoding="utf-8")


def cmd_start(session_key: str, text: str, slug: str) -> dict:
    cfg = _load_grill_config()
    project_root = PROJECTS_ROOT / f"pm-{slug.removeprefix('pm-')}"
    if cfg.get("skip_if_brief_enriched") and _brief_has_grill(project_root):
        return {"status": "skip", "grill_done": True, "reason": "brief_already_enriched", "slug": slug}

    questions = cfg.get("questions") or []
    if not questions:
        return {"status": "skip", "grill_done": True, "reason": "no_questions", "slug": slug}

    session = {
        "session_key": session_key,
        "slug": slug.removeprefix("pm-"),
        "idea_text": text.strip(),
        "round": 0,
        "answers": {},
        "status": "active",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    q0 = questions[0]
    session["current_question_id"] = q0["id"]
    _save_session(session_key, session)
    return {
        "status": "question",
        "grill_done": False,
        "round": 1,
        "max_rounds": cfg.get("max_rounds", 2),
        "question_id": q0["id"],
        "prompt": q0.get("prompt", q0["id"]),
        "slug": session["slug"],
    }


def cmd_reply(session_key: str, text: str) -> dict:
    cfg = _load_grill_config()
    session = _load_session(session_key)
    if not session or session.get("status") != "active":
        return {"status": "no_session", "grill_done": False}

    qid = session.get("current_question_id") or "answer"
    session.setdefault("answers", {})[qid] = text.strip()
    session["round"] = int(session.get("round", 0)) + 1

    questions = cfg.get("questions") or []
    max_rounds = min(int(cfg.get("max_rounds", 2)), len(questions))
    if session["round"] >= max_rounds:
        session["status"] = "done"
        slug = session["slug"]
        project_root = PROJECTS_ROOT / f"pm-{slug}"
        title = session.get("idea_text", "").splitlines()[0][:120]
        _write_enriched_brief(project_root, title, session.get("idea_text", ""), session["answers"])
        _save_session(session_key, session)
        return {
            "status": "done",
            "grill_done": True,
            "slug": slug,
            "project_root": str(project_root),
            "idea_text": session.get("idea_text", ""),
            "answers": session["answers"],
        }

    next_q = questions[session["round"]]
    session["current_question_id"] = next_q["id"]
    _save_session(session_key, session)
    return {
        "status": "question",
        "grill_done": False,
        "round": session["round"] + 1,
        "max_rounds": max_rounds,
        "question_id": next_q["id"],
        "prompt": next_q.get("prompt", next_q["id"]),
        "slug": session["slug"],
    }


def cmd_status(session_key: str) -> dict:
    session = _load_session(session_key)
    if not session:
        return {"status": "idle", "grill_done": False}
    return {
        "status": session.get("status", "unknown"),
        "grill_done": session.get("status") == "done",
        "round": session.get("round", 0),
        "slug": session.get("slug"),
        "idea_text": session.get("idea_text", ""),
        "answers": session.get("answers", {}),
    }


def cmd_cancel(session_key: str) -> dict:
    p = _session_path(session_key)
    if p.exists():
        p.unlink()
    return {"status": "cancelled"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Feishu grill preflight for pm-idea-to-mvp")
    parser.add_argument("action", choices=["start", "reply", "status", "cancel"])
    parser.add_argument("--session-key", required=True)
    parser.add_argument("--text", default="")
    parser.add_argument("--slug", default="")
    args = parser.parse_args()

    if args.action == "start":
        result = cmd_start(args.session_key, args.text, args.slug)
    elif args.action == "reply":
        result = cmd_reply(args.session_key, args.text)
    elif args.action == "status":
        result = cmd_status(args.session_key)
    else:
        result = cmd_cancel(args.session_key)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
