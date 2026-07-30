"""R1: Claude session discovery for cwd (history + project JSONL)."""

from __future__ import annotations

import json
from pathlib import Path

from devmemory.sources.claude import (
    ClaudeHistorySource,
    ClaudeProjectSource,
    discover_claude_sessions,
    encode_project_path,
    pick_latest_unprocessed,
    project_matches_repo,
)


def _write_history(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _write_project_session(projects_dir: Path, repo: Path, session_id: str, lines: list[dict]) -> Path:
    encoded = encode_project_path(repo)
    d = projects_dir / encoded
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{session_id}.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")
    return p


def test_project_matches_repo_exact_and_subdir(tmp_path: Path):
    repo = tmp_path / "devmemory"
    repo.mkdir()
    assert project_matches_repo(str(repo), repo)
    assert project_matches_repo(str(repo / "src" / "devmemory"), repo)
    assert not project_matches_repo(str(tmp_path / "other"), repo)
    assert not project_matches_repo(str(tmp_path), repo)  # parent only — no match
    assert not project_matches_repo("", repo)


def test_history_groups_by_session_id(tmp_path: Path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    sid = "sess-abc-111"
    _write_history(
        hist,
        [
            {
                "display": "First turn: design the auth module carefully.",
                "timestamp": 1000,
                "project": str(repo),
                "sessionId": sid,
            },
            {
                "display": "Second turn: add JWT with HS256 and document pitfalls.",
                "timestamp": 2000,
                "project": str(repo),
                "sessionId": sid,
            },
            {
                "display": "Unrelated other project session prompt here.",
                "timestamp": 3000,
                "project": str(tmp_path / "other"),
                "sessionId": "other-sess",
            },
        ],
    )
    src = ClaudeHistorySource(hist)
    sessions = src.list_sessions(repo_root=repo)
    assert len(sessions) == 1
    s = sessions[0]
    assert s.session_id == sid
    assert s.source == "claude-history"
    assert s.meta.get("turns") == 2
    assert "auth module" in s.text
    assert "HS256" in s.text
    assert s.timestamp == 2000  # last turn


def test_project_jsonl_discovery(tmp_path: Path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    projects = tmp_path / "projects"
    _write_project_session(
        projects,
        repo,
        "proj-session-99",
        [
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "We chose path snap over free-form paths."}],
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "Agreed: resolve to existing dirs; block tests/docs trees.",
                        }
                    ],
                },
            },
        ],
    )
    found = ClaudeProjectSource(projects).list_for_repo(repo)
    assert len(found) == 1
    assert found[0].session_id == "proj-session-99"
    assert found[0].source == "claude-project"
    assert "path snap" in found[0].text
    assert "block tests" in found[0].text


def test_discover_prefers_project_over_history_same_id(tmp_path: Path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    projects = tmp_path / "projects"
    sid = "shared-id-42"
    _write_history(
        hist,
        [
            {
                "display": "History-only short user prompt about modules.",
                "timestamp": 5000,
                "project": str(repo),
                "sessionId": sid,
            }
        ],
    )
    _write_project_session(
        projects,
        repo,
        sid,
        [
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": "Full project transcript with assistant turns included here.",
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": "Here is the durable design decision for extract defaults.",
                },
            },
        ],
    )
    merged = discover_claude_sessions(
        repo, history_path=hist, projects_dir=projects, limit=10
    )
    assert len(merged) == 1
    assert merged[0].source == "claude-project"
    assert "assistant" in merged[0].text.lower() or "durable design" in merged[0].text


def test_discover_newest_first_and_unprocessed_pick(tmp_path: Path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    _write_history(
        hist,
        [
            {
                "display": "Older session talking about extract pipeline setup.",
                "timestamp": 100,
                "project": str(repo),
                "sessionId": "old-sess",
            },
            {
                "display": "Newer session talking about stop hooks and doctor.",
                "timestamp": 9000,
                "project": str(repo),
                "sessionId": "new-sess",
            },
        ],
    )
    sessions = discover_claude_sessions(
        repo, history_path=hist, projects_dir=tmp_path / "no-projects", limit=10
    )
    assert [s.session_id for s in sessions] == ["new-sess", "old-sess"]

    processed = {"new-sess"}
    picked = pick_latest_unprocessed(
        sessions, is_processed=lambda sid: sid in processed
    )
    assert picked is not None
    assert picked.session_id == "old-sess"

    all_done = pick_latest_unprocessed(
        sessions, is_processed=lambda sid: True
    )
    assert all_done is None


def test_list_sessions_cli_sees_unprocessed_claude(tmp_path: Path, monkeypatch):
    """Live-shaped: env overrides + list-sessions includes real unprocessed rows."""
    from click.testing import CliRunner

    from devmemory.cli import main

    repo = tmp_path / "cwd-repo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    projects = tmp_path / "projects"
    _write_history(
        hist,
        [
            {
                "display": "Implement Claude discovery for cwd and group multi-turn history.",
                "timestamp": 1700000000000,
                "project": str(repo),
                "sessionId": "cli-live-sess-1",
            }
        ],
    )
    monkeypatch.setenv("DEVMEMORY_CLAUDE_HISTORY", str(hist))
    monkeypatch.setenv("DEVMEMORY_CLAUDE_PROJECTS", str(projects))

    runner = CliRunner()
    result = runner.invoke(main, ["list-sessions", "--repo", str(repo), "--no-fixtures"])
    assert result.exit_code == 0, result.output
    assert "cli-live-sess-1" in result.output
    assert "claude-history" in result.output
    assert "unprocessed_claude=1" in result.output


def test_extract_default_picks_unprocessed_claude(tmp_path: Path, monkeypatch):
    """Default extract resolution prefers latest unprocessed Claude over fixtures."""
    from devmemory.cli import _resolve_session

    repo = tmp_path / "cwd-repo"
    (repo / "src").mkdir(parents=True)
    hist = tmp_path / "history.jsonl"
    projects = tmp_path / "projects"
    _write_history(
        hist,
        [
            {
                "display": "Default UX should pick this real Claude session first always.",
                "timestamp": 1800000000000,
                "project": str(repo),
                "sessionId": "default-pick-me",
            }
        ],
    )
    monkeypatch.setenv("DEVMEMORY_CLAUDE_HISTORY", str(hist))
    monkeypatch.setenv("DEVMEMORY_CLAUDE_PROJECTS", str(projects))

    session = _resolve_session(repo, session_id=None, fixture=None, text_file=None)
    assert session.session_id == "default-pick-me"
    assert session.source == "claude-history"


def test_history_redacts_secrets(tmp_path: Path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    _write_history(
        hist,
        [
            {
                "display": "Set OPENROUTER_API_KEY=sk-or-v1-abcdefghijklmnopqrstuvwxyz012345",
                "timestamp": 1,
                "project": str(repo),
                "sessionId": "sec-1",
            }
        ],
    )
    sessions = ClaudeHistorySource(hist).list_sessions(repo_root=repo)
    assert sessions
    assert "sk-or-v1-" not in sessions[0].text
