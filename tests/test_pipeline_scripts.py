import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "pipelines" / "pm-idea-to-mvp" / "scripts"


def test_eval_stage_operate_rubric():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "RUNBOOK.md").write_text(
            "部署步骤\n回滚方案\n监控告警\nhealth check 探活\n故障响应 incident\n",
            encoding="utf-8",
        )
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "eval-stage.py"), "--stage", "operate", "--project-root", str(root)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, r.stdout + r.stderr
        data = json.loads(r.stdout)
        assert data.get("passed") is True


def test_phase_transition_writes_gates():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "gates.json").write_text('{"stages": {}}', encoding="utf-8")
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "phase-transition.py"),
                "--project-root",
                str(root),
                "--condition",
                "design_flaw_detected",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0
        gates = json.loads((root / "gates.json").read_text(encoding="utf-8"))
        assert "stages" in gates


def test_harness_runner_dry():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "harness-rules.yaml").write_text(
            "version: '6.0'\ndecisions:\n  refactor:\n    risk: low\n    action: auto_verify\n",
            encoding="utf-8",
        )
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "harness-runner.py"),
                "--project-root",
                str(root),
                "--stage",
                "mvp",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0


def test_no_duplicate_ssot_scripts_in_domains():
    root = Path(__file__).resolve().parent.parent
    forbidden = {"check_docs_ssot.py", "ui_acceptance.py"}
    for prefix in ("domains", "profiles"):
        base = root / prefix
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.name in forbidden:
                raise AssertionError(f"duplicate SSOT script: {path}")


if __name__ == "__main__":
    test_eval_stage_operate_rubric()
    test_phase_transition_writes_gates()
    test_harness_runner_dry()
    test_no_duplicate_ssot_scripts_in_domains()
    print("OK: pipeline script tests passed")
