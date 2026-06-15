import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "pipelines" / "pm-idea-to-mvp" / "scripts"
ROOT_SCRIPTS = ROOT / "scripts"


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


def test_detect_agent_env_source_mode():
    r = subprocess.run(
        [sys.executable, str(ROOT_SCRIPTS / "detect_agent_env.py"), "--json", "--cwd", str(ROOT)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data.get("source_mode") is True
    assert data.get("install_needed") is False


def test_stage_complete_help():
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "stage-complete.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0


def test_self_check_temp_project():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "04-mvp").mkdir()
        (root / "04-mvp" / "README.md").write_text("# mvp\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(ROOT_SCRIPTS / "self_check.py"), "--project-root", str(root)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode in (0, 1)
        data = json.loads(r.stdout)
        assert "checks" in data


def test_renamed_scripts_help():
    for name in ("bootstrap_github_repo.py", "merge_retro_sections.py"):
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / name), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, name + r.stderr


def test_ui_acceptance_generic_profile():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        mvp = root / "04-mvp"
        mvp.mkdir()
        (root / "03b-user-journey.md").write_text(
            "# 用户旅程\n\n## 屏幕映射\n| 屏幕 | 旅程ID |\n| Home | J1 |\n| Settings | J2 |\n",
            encoding="utf-8",
        )
        (mvp / "DESIGN.md").write_text(
            "# Design\n## Palette\n- primary: #3366ff\n- surface: #fff\n- text: #111\n",
            encoding="utf-8",
        )
        (mvp / "index.html").write_text(
            '<html><head><meta name="viewport" content="width=device-width"></head>'
            '<body><nav>Home Settings</nav><a href="settings.html">Settings</a>'
            '<button aria-label="go">Go</button><form></form>'
            '<p class="empty">暂无数据</p></body></html>',
            encoding="utf-8",
        )
        (mvp / "settings.html").write_text(
            "<html><body><nav>Settings</nav><main>Settings page</main></body></html>",
            encoding="utf-8",
        )
        (mvp / "app.js").write_text(
            "fetch('/api/data').then(r => r.json()).catch(() => {});\n",
            encoding="utf-8",
        )
        (mvp / "app.css").write_text(
            "body { color: var(--text); }\n"
            "button:focus-visible { outline: 2px solid #3366ff; }\n"
            "@media (max-width: 600px) { body {} }",
            encoding="utf-8",
        )
        r = subprocess.run(
            [
                sys.executable,
                str(ROOT_SCRIPTS / "ui_acceptance.py"),
                "--full",
                "--profile",
                "generic",
                "--project-root",
                str(root),
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        data = json.loads(r.stdout)
        assert data.get("profile") == "generic"
        assert data.get("passed") is True, r.stdout + r.stderr


def test_lighthouse_check_help():
    r = subprocess.run(
        [sys.executable, str(ROOT_SCRIPTS / "lighthouse_check.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0


def test_install_skills_dry_run():
    r = subprocess.run(
        [sys.executable, str(ROOT_SCRIPTS / "install_skills.py"), "--dry-run", "--core", "--all"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(ROOT),
    )
    assert r.returncode == 0


def test_install_ui_profiles_dry_run():
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT_SCRIPTS / "install_skills.py"),
            "--dry-run",
            "--native-only",
            "--profile",
            "ui-pro-max-full",
            "--profile",
            "playwright-e2e",
            "--profile",
            "ux-principles",
            "--cursor",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr


def test_init_project_playwright_profile():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "init-project.py"),
                "--project-root",
                str(root),
                "--slug",
                "test-app",
                "--profile",
                "playwright-e2e",
                "--skills-root",
                str(ROOT),
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, r.stderr
        assert (root / "e2e" / "playwright.config.ts").exists()
        assert (root / "e2e" / "smoke.spec.ts").exists()


if __name__ == "__main__":
    test_eval_stage_operate_rubric()
    test_phase_transition_writes_gates()
    test_harness_runner_dry()
    test_no_duplicate_ssot_scripts_in_domains()
    test_detect_agent_env_source_mode()
    test_stage_complete_help()
    test_self_check_temp_project()
    test_renamed_scripts_help()
    test_ui_acceptance_generic_profile()
    test_lighthouse_check_help()
    test_install_skills_dry_run()
    test_install_ui_profiles_dry_run()
    test_init_project_playwright_profile()
    print("OK: pipeline script tests passed")
