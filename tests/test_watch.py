"""R8: devmemory watch — poll Claude sessions for new work."""

from __future__ import annotations

import json
import os
from pathlib import Path

from click.testing import CliRunner

from devmemory.cli import main
from devmemory.schema import ExtractionResult, KnowledgeUnit
from devmemory.sources.base import SessionRecord
from devmemory.state import DevMemoryPaths
from devmemory.watch import (
    find_watch_candidates,
    mark_seen,
    read_watch_state,
    run_watch_cycle,
    session_fingerprint,
)


def _hist_line(sid: str, display: str, project: str, ts_ms: int) -> dict:
    return {
        "display": display,
        "project": project,
        "sessionId": sid,
        "timestamp": ts_ms,
    }


def test_session_fingerprint_stable() -> None:
    s = SessionRecord(
        session_id="a",
        source="claude",
        project="/x",
        text="hello",
        timestamp="1",
    )
    assert session_fingerprint(s) == session_fingerprint(s)


def test_find_candidates_new_and_seen(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    proj = str(repo.resolve())
    hist.write_text(
        json.dumps(_hist_line("s1", "First session about modules", proj, 1_700_000_000_000))
        + "\n"
        + json.dumps(_hist_line("s2", "Second session about hooks", proj, 1_700_000_100_000))
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DEVMEMORY_CLAUDE_HISTORY", str(hist))
    monkeypatch.setenv("DEVMEMORY_CLAUDE_PROJECTS", str(tmp_path / "no-projects"))

    paths = DevMemoryPaths.for_repo(repo)
    paths.ensure()
    # no transcript → require_edits still allows (no_transcript_allow)
    cands = find_watch_candidates(repo, paths=paths, require_edits=True)
    ids = {s.session_id for s, _ in cands}
    assert "s1" in ids and "s2" in ids

    # mark s1 seen → only s2
    s1 = next(s for s, _ in cands if s.session_id == "s1")
    mark_seen(paths, s1)
    cands2 = find_watch_candidates(repo, paths=paths, require_edits=True)
    assert {s.session_id for s, _ in cands2} == {"s2"}


def test_find_skips_processed(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    proj = str(repo.resolve())
    hist.write_text(
        json.dumps(_hist_line("done-sess", "Already processed session text", proj, 1_700_000_000_000))
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DEVMEMORY_CLAUDE_HISTORY", str(hist))
    monkeypatch.setenv("DEVMEMORY_CLAUDE_PROJECTS", str(tmp_path / "np"))
    paths = DevMemoryPaths.for_repo(repo)
    paths.ensure()
    paths.mark_processed("done-sess", run_id="r1", units=1)
    cands = find_watch_candidates(repo, paths=paths, require_edits=False)
    assert cands == []


def test_run_watch_cycle_calls_extract(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    proj = str(repo.resolve())
    hist.write_text(
        json.dumps(_hist_line("watch-1", "Extract me please with enough text", proj, 1_700_000_000_000))
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DEVMEMORY_CLAUDE_HISTORY", str(hist))
    monkeypatch.setenv("DEVMEMORY_CLAUDE_PROJECTS", str(tmp_path / "np"))

    calls: list[str] = []

    class FakeOutcome:
        run_id = "run-fake"
        result = ExtractionResult(
            units=[
                KnowledgeUnit(
                    kind="dev",
                    path=".",
                    content="- from watch",
                    confidence="high",
                )
            ],
            summary="ok",
        )

    def fake_extract(root, session, **kwargs):
        calls.append(session.session_id)
        return FakeOutcome()

    cycle = run_watch_cycle(
        repo,
        offline=True,
        require_edits=False,
        extract_fn=fake_extract,
    )
    assert cycle.extracted == 1
    assert calls == ["watch-1"]
    # second cycle: seen → no extract
    cycle2 = run_watch_cycle(
        repo,
        offline=True,
        require_edits=False,
        extract_fn=fake_extract,
    )
    assert cycle2.extracted == 0
    assert len(calls) == 1
    st = read_watch_state(DevMemoryPaths.for_repo(repo))
    assert "watch-1" in (st.get("seen") or {})


def test_cli_watch_once_json(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    hist = tmp_path / "history.jsonl"
    hist.write_text("", encoding="utf-8")
    monkeypatch.setenv("DEVMEMORY_CLAUDE_HISTORY", str(hist))
    monkeypatch.setenv("DEVMEMORY_CLAUDE_PROJECTS", str(tmp_path / "np"))
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["watch", "--repo", str(repo), "--once", "--json", "--offline", "--allow-chat"],
    )
    assert result.exit_code == 0, result.output
    # last line machine summary
    lines = [ln for ln in result.output.strip().splitlines() if ln.startswith("{")]
    assert lines
    summary = json.loads(lines[-1])
    assert summary["polls"] == 1
    assert summary["extracted"] == 0
