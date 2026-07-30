"""R7.5: hook tool-edit gate — skip chat-only SessionEnd extracts."""

from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

from devmemory.hook_gate import (
    EDIT_TOOL_NAMES,
    should_run_extract_for_session,
    text_has_tool_edits,
    transcript_has_tool_edits,
)

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts" / "claude-code-hook.sh"


@pytest.fixture(autouse=True)
def _chmod_hook() -> None:
    mode = HOOK.stat().st_mode
    HOOK.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n",
        encoding="utf-8",
    )
    return path


def test_edit_tool_names_include_write_edit() -> None:
    assert "Write" in EDIT_TOOL_NAMES
    assert "Edit" in EDIT_TOOL_NAMES


def test_text_has_tool_edits_detects_json_markers() -> None:
    assert text_has_tool_edits('{"type":"tool_use","name":"Write","input":{}}')
    assert text_has_tool_edits('{"tool":"Edit","event":"tool_complete"}')
    assert not text_has_tool_edits('{"type":"text","text":"hello chat only"}')
    assert not text_has_tool_edits('{"type":"tool_use","name":"Bash","input":{}}')


def test_transcript_jsonl_with_write(tmp_path: Path) -> None:
    p = _write_jsonl(
        tmp_path / "sess.jsonl",
        [
            {"type": "user", "message": {"role": "user", "content": "hi"}},
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_1",
                            "name": "Write",
                            "input": {"file_path": "a.py", "content": "x=1"},
                        }
                    ],
                },
            },
        ],
    )
    assert transcript_has_tool_edits(p) is True


def test_transcript_jsonl_chat_only(tmp_path: Path) -> None:
    p = _write_jsonl(
        tmp_path / "chat.jsonl",
        [
            {"type": "user", "message": {"role": "user", "content": "explain auth"}},
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Auth uses JWT…"}],
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_2",
                            "name": "Bash",
                            "input": {"command": "ls"},
                        }
                    ],
                },
            },
        ],
    )
    assert transcript_has_tool_edits(p) is False


def test_transcript_missing_returns_none(tmp_path: Path) -> None:
    assert transcript_has_tool_edits(tmp_path / "nope.jsonl") is None


def test_should_run_no_transcript_allows() -> None:
    run, reason = should_run_extract_for_session(
        require_edits=True,
        hook_transcript=None,
        session_id="x",
        repo_root=Path("/tmp/no-such-repo-devmemory"),
    )
    assert run is True
    assert "no_transcript" in reason or "allow" in reason


def test_should_run_skips_chat_only(tmp_path: Path) -> None:
    p = _write_jsonl(
        tmp_path / "chat.jsonl",
        [{"message": {"content": [{"type": "text", "text": "hi"}]}}],
    )
    run, reason = should_run_extract_for_session(
        require_edits=True,
        hook_transcript=str(p),
    )
    assert run is False
    assert "no_tool_edits" in reason


def test_should_run_when_edits_present(tmp_path: Path) -> None:
    p = _write_jsonl(
        tmp_path / "ed.jsonl",
        [
            {
                "message": {
                    "content": [
                        {"type": "tool_use", "name": "Edit", "input": {"file_path": "x"}}
                    ]
                }
            }
        ],
    )
    run, reason = should_run_extract_for_session(
        require_edits=True,
        hook_transcript=str(p),
    )
    assert run is True
    assert "tool_edits" in reason


def test_should_run_require_edits_off(tmp_path: Path) -> None:
    p = _write_jsonl(tmp_path / "chat.jsonl", [{"text": "chat only"}])
    run, reason = should_run_extract_for_session(
        require_edits=False,
        hook_transcript=str(p),
    )
    assert run is True
    assert reason == "require_edits=off"


def _run_hook(payload: dict, env: dict, timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
    base = os.environ.copy()
    base.update(
        {
            "DEVMEMORY_HOOK_BG": "0",
            "DEVMEMORY_HOOK_VERBOSE": "1",
            "DEVMEMORY_HOOK_OFFLINE": "1",
            "DEVMEMORY_HOOK_DEBOUNCE_S": "0",
            "DEVMEMORY_BIN": str(ROOT / ".venv" / "bin" / "devmemory"),
            "PATH": f"{ROOT / '.venv' / 'bin'}:{os.environ.get('PATH', '')}",
            "PYTHONPATH": str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
        }
    )
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


def test_hook_skips_chat_only_transcript(tmp_path: Path) -> None:
    transcript = _write_jsonl(
        tmp_path / "t.jsonl",
        [
            {
                "message": {
                    "content": [{"type": "text", "text": "just chatting about architecture"}]
                }
            }
        ],
    )
    log = tmp_path / "hooks.log"
    r = _run_hook(
        {
            "hook_event_name": "SessionEnd",
            "session_id": "chat-only-1",
            "cwd": str(tmp_path),
            "transcript_path": str(transcript),
            "stop_hook_active": False,
        },
        env={
            "DEVMEMORY_HOOK_LOG": str(log),
            "DEVMEMORY_HOOK_REQUIRE_EDITS": "1",
        },
    )
    assert r.returncode == 0
    text = log.read_text(encoding="utf-8")
    assert "no tool edits" in text or "no_tool_edits" in text
    assert "run:" not in text


def test_hook_runs_when_transcript_has_write(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x=1\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "i"],
        cwd=tmp_path,
        check=True,
    )
    transcript = _write_jsonl(
        tmp_path / "t.jsonl",
        [
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Write",
                            "input": {"file_path": "src/a.py", "content": "x=2"},
                        }
                    ]
                }
            }
        ],
    )
    log = tmp_path / "hooks.log"
    r = _run_hook(
        {
            "hook_event_name": "SessionEnd",
            "session_id": "with-write-1",
            "cwd": str(tmp_path),
            "transcript_path": str(transcript),
            "stop_hook_active": False,
        },
        env={
            "DEVMEMORY_HOOK_LOG": str(log),
            "DEVMEMORY_HOOK_REQUIRE_EDITS": "1",
            "DEVMEMORY_HOOK_FORCE": "1",
        },
        timeout=45,
    )
    assert r.returncode == 0
    text = log.read_text(encoding="utf-8")
    assert "gate:" in text or "tool_edits" in text or "run:" in text
    assert "no tool edits" not in text


def test_hook_require_edits_off_runs_chat(tmp_path: Path) -> None:
    transcript = _write_jsonl(
        tmp_path / "t.jsonl",
        [{"message": {"content": [{"type": "text", "text": "chat"}]}}],
    )
    log = tmp_path / "hooks.log"
    r = _run_hook(
        {
            "hook_event_name": "SessionEnd",
            "session_id": "chat-allow",
            "cwd": str(tmp_path),
            "transcript_path": str(transcript),
            "stop_hook_active": False,
        },
        env={
            "DEVMEMORY_HOOK_LOG": str(log),
            "DEVMEMORY_HOOK_REQUIRE_EDITS": "0",
            "DEVMEMORY_HOOK_FORCE": "1",
        },
        timeout=45,
    )
    assert r.returncode == 0
    text = log.read_text(encoding="utf-8")
    # With require off, should not skip for no edits
    assert "no tool edits" not in text
