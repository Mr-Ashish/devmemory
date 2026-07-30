"""R3: Claude Code stop/SessionEnd hook scripts."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts" / "claude-code-hook.sh"
INSTALL = ROOT / "scripts" / "install-claude-hook.sh"


@pytest.fixture(autouse=True)
def _chmod_scripts() -> None:
    for p in (HOOK, INSTALL):
        mode = p.stat().st_mode
        p.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _run_hook(
    payload: dict,
    *,
    env: dict | None = None,
    timeout: float = 15.0,
) -> subprocess.CompletedProcess[str]:
    base = os.environ.copy()
    base["DEVMEMORY_HOOK_BG"] = "0"  # foreground for tests
    base["DEVMEMORY_HOOK_VERBOSE"] = "1"
    base["DEVMEMORY_HOOK_OFFLINE"] = "1"
    base["DEVMEMORY_HOOK_DEBOUNCE_S"] = "0"
    base["DEVMEMORY_BIN"] = str(ROOT / ".venv" / "bin" / "devmemory")
    if not Path(base["DEVMEMORY_BIN"]).exists():
        # fallback to PATH after pip install -e
        base.pop("DEVMEMORY_BIN", None)
    if env:
        base.update(env)
    return subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=base,
        timeout=timeout,
        cwd=str(ROOT),
    )


def test_hook_script_exists_and_executable() -> None:
    assert HOOK.is_file()
    assert os.access(HOOK, os.X_OK)
    assert INSTALL.is_file()


def test_hook_empty_stdin_exits_zero() -> None:
    r = subprocess.run(
        ["bash", str(HOOK)],
        input="",
        text=True,
        capture_output=True,
        env={**os.environ, "DEVMEMORY_HOOK_VERBOSE": "1"},
        timeout=5,
    )
    assert r.returncode == 0


def test_hook_skips_stop_by_default(tmp_path: Path) -> None:
    log = tmp_path / "hooks.log"
    r = _run_hook(
        {
            "hook_event_name": "Stop",
            "session_id": "sess-stop-1",
            "cwd": str(tmp_path),
            "stop_hook_active": False,
        },
        env={"DEVMEMORY_HOOK_LOG": str(log), "DEVMEMORY_HOOK_ON_STOP": "0"},
    )
    assert r.returncode == 0
    text = log.read_text(encoding="utf-8") if log.exists() else ""
    assert "Stop ignored" in text or "skip: Stop" in text


def test_hook_skips_when_stop_hook_active(tmp_path: Path) -> None:
    log = tmp_path / "hooks.log"
    r = _run_hook(
        {
            "hook_event_name": "SessionEnd",
            "session_id": "sess-active",
            "cwd": str(tmp_path),
            "stop_hook_active": True,
        },
        env={"DEVMEMORY_HOOK_LOG": str(log)},
    )
    assert r.returncode == 0
    assert "stop_hook_active" in log.read_text(encoding="utf-8")


def test_hook_session_end_offline_dry_run(tmp_path: Path) -> None:
    """SessionEnd on a mini repo runs offline extract dry-run without writing secrets."""
    # minimal git repo so assemble is happy
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"],
        cwd=tmp_path,
        check=True,
    )

    log = tmp_path / "hook.log"
    # Use fixture via forcing no session match → falls through? We pass unknown session
    # and let extract fail soft, OR pass no session_id so default resolution uses fixtures
    # when run against ROOT. For tmp_path, session not found should not crash hook (rc=0).
    r = _run_hook(
        {
            "hook_event_name": "SessionEnd",
            "session_id": "missing-session-xyz",
            "cwd": str(tmp_path),
            "stop_hook_active": False,
        },
        env={
            "DEVMEMORY_HOOK_LOG": str(log),
            "DEVMEMORY_HOOK_OFFLINE": "1",
            "DEVMEMORY_HOOK_BG": "0",
            "DEVMEMORY_HOOK_DEBOUNCE_S": "0",
            "PATH": f"{ROOT / '.venv' / 'bin'}:{os.environ.get('PATH', '')}",
            "DEVMEMORY_BIN": str(ROOT / ".venv" / "bin" / "devmemory"),
        },
        timeout=30,
    )
    assert r.returncode == 0
    body = log.read_text(encoding="utf-8") if log.exists() else r.stderr
    # Hook must log something and not leave secrets
    assert "sk-or" not in body
    assert "OPENROUTER_API_KEY=" not in body
    # Either ran extract (warn on missing session) or noted run
    assert "run:" in body or "warn:" in body or "skip:" in body or "ok:" in body


def test_hook_session_end_with_fixture_via_repo_root(tmp_path: Path) -> None:
    """When cwd is the package repo, SessionEnd dry-run with no session id works offline."""
    log = tmp_path / "hooks.log"
    stamp_parent = ROOT / ".devmemory" / "hook-stamps"
    # Use unique session empty + force to avoid debounce flake across runs
    r = _run_hook(
        {
            "hook_event_name": "SessionEnd",
            "cwd": str(ROOT),
            "stop_hook_active": False,
        },
        env={
            "DEVMEMORY_HOOK_LOG": str(log),
            "DEVMEMORY_HOOK_OFFLINE": "1",
            "DEVMEMORY_HOOK_BG": "0",
            "DEVMEMORY_HOOK_FORCE": "1",
            "DEVMEMORY_HOOK_DEBOUNCE_S": "0",
            "DEVMEMORY_BIN": str(ROOT / ".venv" / "bin" / "devmemory"),
            "PATH": f"{ROOT / '.venv' / 'bin'}:{os.environ.get('PATH', '')}",
        },
        timeout=60,
    )
    assert r.returncode == 0
    text = log.read_text(encoding="utf-8")
    assert "run:" in text
    # dry-run: the *command line* logged after "run:" must not pass --apply
    run_lines = [ln for ln in text.splitlines() if "run:" in ln]
    assert run_lines, text
    assert " --apply" not in run_lines[-1]
    assert "--offline" in run_lines[-1]
    # machine JSON from extract should record apply:false when present
    if '"apply":' in text:
        assert '"apply": false' in text


def test_hook_debounce(tmp_path: Path) -> None:
    log = tmp_path / "hooks.log"
    env = {
        "DEVMEMORY_HOOK_LOG": str(log),
        "DEVMEMORY_HOOK_OFFLINE": "1",
        "DEVMEMORY_HOOK_BG": "0",
        "DEVMEMORY_HOOK_DEBOUNCE_S": "3600",
        "DEVMEMORY_HOOK_ON_STOP": "1",
        "DEVMEMORY_BIN": str(ROOT / ".venv" / "bin" / "devmemory"),
        "PATH": f"{ROOT / '.venv' / 'bin'}:{os.environ.get('PATH', '')}",
    }
    payload = {
        "hook_event_name": "SessionEnd",
        "session_id": f"debounce-{time.time_ns()}",
        "cwd": str(tmp_path),
        "stop_hook_active": False,
    }
    r1 = _run_hook(payload, env=env, timeout=30)
    r2 = _run_hook(payload, env=env, timeout=30)
    assert r1.returncode == 0 and r2.returncode == 0
    text = log.read_text(encoding="utf-8")
    assert "debounced" in text


def test_install_print_fragment() -> None:
    r = subprocess.run(
        ["bash", str(INSTALL), "--print"],
        text=True,
        capture_output=True,
        timeout=10,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "SessionEnd" in data["hooks"]
    cmd = data["hooks"]["SessionEnd"][0]["hooks"][0]["command"]
    assert cmd.endswith("claude-code-hook.sh")
    assert Path(cmd).is_file()


def test_install_merges_project_settings(tmp_path: Path) -> None:
    claude = tmp_path / ".claude"
    claude.mkdir()
    settings = claude / "settings.json"
    settings.write_text(
        json.dumps({"permissions": {"allow": ["Bash(ls)"]}, "hooks": {}}),
        encoding="utf-8",
    )
    r = subprocess.run(
        ["bash", str(INSTALL), "--repo", str(tmp_path)],
        text=True,
        capture_output=True,
        timeout=10,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(settings.read_text(encoding="utf-8"))
    assert data["permissions"]["allow"] == ["Bash(ls)"]
    assert "SessionEnd" in data["hooks"]
    cmd = data["hooks"]["SessionEnd"][0]["hooks"][0]["command"]
    assert "claude-code-hook.sh" in cmd
    # idempotent second install
    r2 = subprocess.run(
        ["bash", str(INSTALL), "--repo", str(tmp_path)],
        text=True,
        capture_output=True,
        timeout=10,
        cwd=str(ROOT),
    )
    assert r2.returncode == 0
    data2 = json.loads(settings.read_text(encoding="utf-8"))
    assert len(data2["hooks"]["SessionEnd"]) == 1
