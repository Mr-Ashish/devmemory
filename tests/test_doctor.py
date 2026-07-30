"""R5: devmemory doctor readiness checks."""

from __future__ import annotations

import json
import os
from pathlib import Path

from click.testing import CliRunner

from devmemory.cli import main
from devmemory.doctor import (
    _mask_key,
    check_openrouter_key,
    check_sessions,
    run_doctor,
)


def test_mask_key_never_leaks_full_secret() -> None:
    key = "sk-or-v1-" + ("a" * 40)
    masked = _mask_key(key)
    assert key not in masked
    assert "sk-o" in masked or masked.startswith("sk-")
    assert "sha256:" in masked
    assert "…" in masked or "..." in masked


def test_run_doctor_on_package_repo() -> None:
    root = Path(__file__).resolve().parents[1]
    report = run_doctor(root)
    ids = {c.id for c in report.checks}
    assert {
        "python",
        "devmemory",
        "git",
        "hermes",
        "openrouter",
        "model",
        "sessions",
        "state",
        "gitignore",
        "hook",
    } <= ids
    assert report.ready_offline is True  # fixtures present
    assert report.ok is True
    # no raw key material in serialized report
    blob = json.dumps(report.to_dict())
    assert "sk-or-v1-" not in blob or "…" in blob
    # if key present it must be masked
    or_check = next(c for c in report.checks if c.id == "openrouter")
    if or_check.status == "ok":
        assert "…" in or_check.detail or "***" in or_check.detail


def test_doctor_sessions_warn_without_claude(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DEVMEMORY_CLAUDE_HISTORY", str(tmp_path / "no-history.jsonl"))
    monkeypatch.setenv("DEVMEMORY_CLAUDE_PROJECTS", str(tmp_path / "no-projects"))
    (tmp_path / "src").mkdir()
    # package fixtures still exist via package_root — sessions should warn not fail
    c = check_sessions(tmp_path)
    assert c.status in ("ok", "warn")
    assert "claude=" in c.detail


def test_doctor_openrouter_fail_when_unset(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("DEVMEMORY_ENV_FILE", raising=False)
    monkeypatch.chdir(tmp_path)
    # isolate from accidental .env loads in parents by pointing to empty env file
    empty = tmp_path / "empty.env"
    empty.write_text("# no key\n", encoding="utf-8")
    monkeypatch.setenv("DEVMEMORY_ENV_FILE", str(empty))
    # clear any key that load might have left
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    c = check_openrouter_key()
    # If the real user env still has a key in os.environ from parent, force clear again
    if c.status == "ok" and "OPENROUTER_API_KEY" in os.environ:
        # re-test pure path
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        c = check_openrouter_key()
    # When key truly absent:
    if not os.environ.get("OPENROUTER_API_KEY"):
        assert c.status == "fail"
        assert "OPENROUTER" in c.summary or "missing" in c.summary.lower()


def test_cli_doctor_json(tmp_path: Path) -> None:
    # use real package root so fixtures exist
    root = Path(__file__).resolve().parents[1]
    runner = CliRunner()
    result = runner.invoke(main, ["doctor", "--repo", str(root), "--json"])
    assert result.exit_code in (0, 1), result.output
    data = json.loads(result.output)
    assert "ready_live" in data
    assert "ready_offline" in data
    assert "checks" in data
    assert any(c["id"] == "hermes" for c in data["checks"])
    # never leak full keys
    assert "sk-or-v1-" + "a" * 20 not in result.output


def test_cli_doctor_table_and_machine_line() -> None:
    root = Path(__file__).resolve().parents[1]
    runner = CliRunner()
    result = runner.invoke(main, ["doctor", "--repo", str(root)])
    assert "doctor" in result.output.lower() or "Readiness" in result.output
    last = result.output.strip().splitlines()[-1]
    payload = json.loads(last)
    assert "ready_offline" in payload
    assert "fail" in payload


def test_cli_doctor_strict_exit_code() -> None:
    root = Path(__file__).resolve().parents[1]
    runner = CliRunner()
    # without forcing env, strict may pass or fail depending on machine
    result = runner.invoke(main, ["doctor", "--repo", str(root), "--strict", "--json"])
    data = json.loads(result.output)
    if data.get("ready_live"):
        assert result.exit_code == 0
    else:
        assert result.exit_code == 1
