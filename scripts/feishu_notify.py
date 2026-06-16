#!/usr/bin/env python3
"""Feishu notification for pm-idea-to-mvp — Open API (primary) + webhook (fallback)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipelines" / "pm-idea-to-mvp" / "scripts"))
from pipeline_notify import build_stage_message  # noqa: E402
from pipeline_version import PIPELINE_VERSION  # noqa: E402

HERMES_ENV = Path(os.environ.get("HERMES_HOME", r"D:\hermes-data")) / ".env"
FEISHU_API = {
    "feishu": "https://open.feishu.cn",
    "lark": "https://open.larksuite.com",
}


def _load_feishu_env() -> dict[str, str]:
    out: dict[str, str] = {}
    for key in (
        "FEISHU_APP_ID",
        "FEISHU_APP_SECRET",
        "FEISHU_DOMAIN",
        "FEISHU_HOME_CHANNEL",
        "FEISHU_HOME_CHANNEL_THREAD_ID",
        "FEISHU_WEBHOOK_URL",
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


def send_open_api(text: str, *, env: dict[str, str] | None = None) -> dict:
    env = env or _load_feishu_env()
    app_id = env.get("FEISHU_APP_ID", "")
    app_secret = env.get("FEISHU_APP_SECRET", "")
    chat_id = env.get("FEISHU_HOME_CHANNEL", "")
    report: dict = {"channel": "open_api", "sent": False}
    if not (app_id and app_secret and chat_id):
        report["detail"] = "missing FEISHU_APP_ID/SECRET/HOME_CHANNEL"
        return report

    domain = env.get("FEISHU_DOMAIN", "feishu")
    base = FEISHU_API.get(domain, FEISHU_API["feishu"])
    try:
        token = _tenant_token(app_id, app_secret, domain)
    except Exception as exc:
        report["detail"] = f"token error: {exc}"
        return report

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
            report["detail"] = f"API error: {data}"
            return report
        report["sent"] = True
        return report
    except urllib.error.HTTPError as exc:
        report["detail"] = f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:300]}"
        return report
    except Exception as exc:
        report["detail"] = str(exc)
        return report


def send_webhook(text: str, *, env: dict[str, str] | None = None) -> dict:
    env = env or _load_feishu_env()
    webhook = env.get("FEISHU_WEBHOOK_URL", "").strip()
    report: dict = {"channel": "webhook", "sent": False}
    if not webhook:
        report["detail"] = "FEISHU_WEBHOOK_URL not set"
        return report
    payload = {"msg_type": "text", "content": {"text": text}}
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            report["sent"] = resp.status == 200
        return report
    except Exception as exc:
        report["detail"] = str(exc)
        return report


def send_feishu(text: str) -> dict:
    """Try Open API first, then webhook; log to stderr if both fail."""
    env = _load_feishu_env()
    open_result = send_open_api(text, env=env)
    if open_result.get("sent"):
        open_result["pipeline_version"] = PIPELINE_VERSION
        return open_result
    webhook_result = send_webhook(text, env=env)
    if webhook_result.get("sent"):
        webhook_result["pipeline_version"] = PIPELINE_VERSION
        return webhook_result
    combined = {
        "pipeline_version": PIPELINE_VERSION,
        "sent": False,
        "open_api": open_result,
        "webhook": webhook_result,
    }
    print(json.dumps({"msg_type": "text", "content": {"text": text}}, ensure_ascii=False), file=sys.stderr)
    return combined


def build_message(
    stage: str,
    status: str,
    project_root: str,
    task_id: str,
    extra: str = "",
    *,
    human_checkpoint: bool = False,
) -> str:
    return build_stage_message(
        stage, status, project_root, task_id, extra,
        human_checkpoint=human_checkpoint,
    )


def notify_stage(
    stage: str,
    status: str,
    project_root: str,
    task_id: str = "",
    extra: str = "",
    *,
    human_checkpoint: bool = False,
) -> dict:
    text = build_message(
        stage, status, project_root, task_id, extra,
        human_checkpoint=human_checkpoint,
    )
    result = send_feishu(text)
    result["message_preview"] = text[:1200]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Feishu notify for pm-idea-to-mvp")
    parser.add_argument("--stage", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--extra", default="")
    parser.add_argument("--human-checkpoint", action="store_true")
    parser.add_argument("--heartbeat", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Build message only, do not send")
    args = parser.parse_args()

    status = args.status
    if args.human_checkpoint and "checkpoint" not in status.lower():
        status = f"CHECKPOINT ⏸ — {status}"

    text = build_message(
        args.stage,
        status,
        args.project_root,
        args.task_id,
        args.extra,
        human_checkpoint=args.human_checkpoint,
    )
    if args.dry_run:
        report = {"sent": False, "dry_run": True, "message_preview": text}
    else:
        report = notify_stage(
            args.stage,
            status,
            args.project_root,
            args.task_id,
            args.extra,
            human_checkpoint=args.human_checkpoint,
        )
    if args.heartbeat:
        report["heartbeat"] = True
    out = json.dumps(report, ensure_ascii=False, indent=2)
    try:
        print(out)
    except UnicodeEncodeError:
        print(out.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
    return 0 if report.get("sent") or report.get("dry_run") else 0


if __name__ == "__main__":
    sys.exit(main())
