#!/usr/bin/env python3
"""Send PM pipeline stage notifications to Feishu home channel."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

HERMES_ENV = Path(os.environ.get("HERMES_HOME", r"D:\hermes-data")) / ".env"
FEISHU_API = {
    "feishu": "https://open.feishu.cn",
    "lark": "https://open.larksuite.com",
}


def _load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    for key in (
        "FEISHU_APP_ID",
        "FEISHU_APP_SECRET",
        "FEISHU_DOMAIN",
        "FEISHU_HOME_CHANNEL",
        "FEISHU_HOME_CHANNEL_THREAD_ID",
    ):
        val = os.environ.get(key, "").strip()
        if val:
            out[key] = val
    if HERMES_ENV.exists():
        for line in HERMES_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip("\"'")
            if k.startswith("FEISHU_") and k not in out and v:
                out[k] = v
    return out


def _tenant_token(app_id: str, app_secret: str, domain: str) -> str:
    base = FEISHU_API.get(domain, FEISHU_API["feishu"])
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/open-apis/auth/v3/tenant_access_token/internal",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    token = data.get("tenant_access_token")
    if not token:
        raise RuntimeError(f"Feishu token failed: {data}")
    return token


def send_text(text: str, *, env: dict[str, str] | None = None) -> bool:
    """Post text to FEISHU_HOME_CHANNEL. Returns True on success, False if skipped/failed."""
    env = env or _load_env()
    app_id = env.get("FEISHU_APP_ID", "")
    app_secret = env.get("FEISHU_APP_SECRET", "")
    chat_id = env.get("FEISHU_HOME_CHANNEL", "")
    if not (app_id and app_secret and chat_id):
        print("[feishu_notify] skipped: missing FEISHU_APP_ID/SECRET/HOME_CHANNEL")
        return False

    domain = env.get("FEISHU_DOMAIN", "feishu")
    base = FEISHU_API.get(domain, FEISHU_API["feishu"])
    try:
        token = _tenant_token(app_id, app_secret, domain)
    except Exception as exc:
        print(f"[feishu_notify] token error: {exc}")
        return False

    payload: dict = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False),
    }
    thread_id = env.get("FEISHU_HOME_CHANNEL_THREAD_ID", "").strip()
    if thread_id:
        payload["thread_id"] = thread_id

    url = f"{base}/open-apis/im/v1/messages?receive_id_type=chat_id"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("code", 0) != 0:
            print(f"[feishu_notify] API error: {data}")
            return False
        print("[feishu_notify] sent")
        return True
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"[feishu_notify] HTTP {exc.code}: {detail}")
        return False
    except Exception as exc:
        print(f"[feishu_notify] send failed: {exc}")
        return False


def notify_stage(
    slug: str,
    stage: str,
    gate: str,
    *,
    summary: str = "",
    human_checkpoint: bool = False,
    task_id: str = "",
) -> bool:
    pages = f"https://ttmens.github.io/pm-{slug}/"
    repo = f"https://github.com/ttmens/pm-{slug}"
    lines = [
        f"【PM 流水线】pm-{slug} — {stage} 完成",
        f"产物页：{pages}",
        f"仓库：{repo}",
        f"Gate：{gate}",
    ]
    if summary:
        lines.append(f"摘要：{summary}")
    if human_checkpoint:
        lines.append("⏸ 人工检查点 — 请确认后继续")
        if task_id:
            lines.append(f"任务：{task_id}")
            lines.append(f"确认后执行：hermes kanban unblock {task_id}")
        else:
            lines.append("确认后执行：hermes kanban unblock <task_id>")
        lines.append("（unblock 后 worker 将 kanban_complete 并进入下一阶段）")
    return send_text("\n".join(lines))


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--gate", default="pass")
    p.add_argument("--summary", default="")
    p.add_argument("--human-checkpoint", action="store_true")
    p.add_argument("--task-id", default="")
    args = p.parse_args()
    ok = notify_stage(
        args.slug.removeprefix("pm-"),
        args.stage,
        args.gate,
        summary=args.summary,
        human_checkpoint=args.human_checkpoint,
        task_id=args.task_id,
    )
    raise SystemExit(0 if ok else 1)
