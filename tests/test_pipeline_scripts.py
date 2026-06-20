import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "pipelines" / "pm-idea-to-mvp" / "scripts"
ROOT_SCRIPTS = ROOT / "scripts"


def test_inner_loop_driver_help():
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "inner-loop-driver.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0


def test_init_project_help():
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "init-project.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0


def test_consume_feedback_help():
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "consume-feedback.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0


def test_pipeline_version():
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "pipeline_version.py")],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SCRIPTS),
    )
    # pipeline_version defines PIPELINE_VERSION constant
    spec = __import__("importlib.util").util.spec_from_file_location(
        "pv", SCRIPTS / "pipeline_version.py"
    )
    mod = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.PIPELINE_VERSION == "9.1.0"


def test_init_project_creates_governance():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "init-project.py"),
                "--project-root",
                str(root),
                "--slug",
                "test-slug",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, r.stdout + r.stderr
        data = json.loads(r.stdout)
        assert data.get("slug") == "test-slug"
        assert (root / "gates.json").exists()
        assert (root / "harness-rules.yaml").exists()


def test_no_duplicate_ssot_scripts_in_domains():
    forbidden = {"check_docs_ssot.py", "ui_acceptance.py"}
    for prefix in ("domains", "profiles"):
        base = ROOT / prefix
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


def test_validate_skills_passes():
    r = subprocess.run(
        [sys.executable, str(ROOT_SCRIPTS / "validate_skills.py")],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stdout + r.stderr
