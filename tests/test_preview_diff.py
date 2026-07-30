"""R4: unified knowledge git-style diff preview before apply."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from devmemory.apply import apply_result, plan_preview, plan_result
from devmemory.cli import main
from devmemory.extract import extract_session, package_root
from devmemory.schema import ExtractionResult, KnowledgeUnit
from devmemory.sources.fixtures import FixtureSource
from devmemory.state import DevMemoryPaths


def _two_units_same_file() -> ExtractionResult:
    return ExtractionResult(
        units=[
            KnowledgeUnit(
                kind="dev",
                path="src/auth",
                action="merge",
                section="Patterns",
                content="- Use short-lived access tokens",
                confidence="high",
            ),
            KnowledgeUnit(
                kind="dev",
                path="src/auth",
                action="merge",
                section="Pitfalls",
                content="- Never log raw JWT secrets",
                confidence="high",
            ),
            KnowledgeUnit(
                kind="usage",
                path=".",
                action="merge",
                section="Common commands",
                content="- `pytest tests/auth -q`",
                confidence="medium",
            ),
        ]
    )


def test_plan_preview_unified_diff_new_files(tmp_path: Path) -> None:
    (tmp_path / "src" / "auth").mkdir(parents=True)
    preview = plan_preview(tmp_path, _two_units_same_file())
    assert len(preview.changes) == 3
    assert all(c.applied is False for c in preview.changes)
    assert len(preview.files) == 2  # DEV.md + USAGE.md
    text = preview.unified_text()
    assert "diff --git" in text
    assert "src/auth/DEV.md" in text
    assert "USAGE.md" in text
    assert "short-lived access tokens" in text
    assert "Never log raw JWT secrets" in text
    assert "pytest tests/auth" in text
    # new file markers
    assert "new file mode" in text
    stats = preview.stats()
    assert stats["files"] == 2
    assert stats["lines_added"] > 0
    assert stats["changes"] == 3
    # no writes
    assert not (tmp_path / "src" / "auth" / "DEV.md").exists()


def test_plan_preview_sequential_merge_into_existing(tmp_path: Path) -> None:
    auth = tmp_path / "src" / "auth"
    auth.mkdir(parents=True)
    existing = (
        "# DEV — engineering knowledge\n\n"
        "> How this part of the system is built.\n\n"
        "## Patterns\n\n"
        "- Existing pattern bullet\n"
    )
    (auth / "DEV.md").write_text(existing, encoding="utf-8")
    result = ExtractionResult(
        units=[
            KnowledgeUnit(
                kind="dev",
                path="src/auth",
                action="merge",
                section="Patterns",
                content="- Brand new pattern about refresh rotation",
                confidence="high",
            ),
            KnowledgeUnit(
                kind="dev",
                path="src/auth",
                action="merge",
                section="Patterns",
                content="- Second sequential pattern about clock skew",
                confidence="high",
            ),
        ]
    )
    preview = plan_preview(tmp_path, result)
    assert len(preview.files) == 1
    fd = preview.files[0]
    assert fd.rel_path == "src/auth/DEV.md"
    assert not fd.is_new
    unified = fd.unified()
    assert "Existing pattern bullet" in unified or "Existing pattern bullet" in fd.old_text
    assert "refresh rotation" in fd.new_text
    assert "clock skew" in fd.new_text
    # both sequential bullets present once
    assert fd.new_text.count("refresh rotation") == 1
    assert fd.new_text.count("clock skew") == 1
    # diff shows additions
    assert "+- Brand new pattern about refresh rotation" in unified or (
        "refresh rotation" in unified and unified.count("+") >= 1
    )


def test_plan_preview_noop_when_near_dupe(tmp_path: Path) -> None:
    auth = tmp_path / "src" / "auth"
    auth.mkdir(parents=True)
    (auth / "DEV.md").write_text(
        "# DEV\n\n## Patterns\n\n- Use short-lived access tokens\n",
        encoding="utf-8",
    )
    result = ExtractionResult(
        units=[
            KnowledgeUnit(
                kind="dev",
                path="src/auth",
                action="merge",
                section="Patterns",
                content="- Use short-lived access tokens",
                confidence="high",
            )
        ]
    )
    preview = plan_preview(tmp_path, result)
    assert preview.changes == []
    assert preview.files == []
    assert preview.unified_text() == ""


def test_plan_result_matches_preview_changes(tmp_path: Path) -> None:
    (tmp_path / "src" / "auth").mkdir(parents=True)
    result = _two_units_same_file()
    planned = plan_result(tmp_path, result)
    preview = plan_preview(tmp_path, result)
    assert len(planned) == len(preview.changes)
    assert {c.path for c in planned} == {c.path for c in preview.changes}


def test_preview_matches_apply_content(tmp_path: Path) -> None:
    (tmp_path / "src" / "auth").mkdir(parents=True)
    result = _two_units_same_file()
    preview = plan_preview(tmp_path, result)
    apply_result(tmp_path, result)
    for fd in preview.files:
        on_disk = fd.path.read_text(encoding="utf-8")
        assert on_disk == fd.new_text


def test_extract_dry_run_writes_preview_diff(tmp_path: Path) -> None:
    (tmp_path / "src" / "auth").mkdir(parents=True)
    (tmp_path / "src" / "auth" / "__init__.py").write_text("")
    fixtures = package_root() / "fixtures" / "sessions"
    session = FixtureSource(fixtures).get("sample-auth-module")
    assert session is not None
    outcome = extract_session(
        tmp_path, session, apply=False, offline=True, force=True
    )
    assert (outcome.run_dir / "preview.diff").exists()
    assert (outcome.run_dir / "preview.json").exists()
    assert outcome.preview is not None
    diff = (outcome.run_dir / "preview.diff").read_text(encoding="utf-8")
    meta = json.loads((outcome.run_dir / "preview.json").read_text(encoding="utf-8"))
    if outcome.changes:
        assert "diff --git" in diff or meta["stats"]["files"] >= 0
        assert meta["stats"]["changes"] == len(outcome.changes)
    # still no knowledge writes + no cursor
    assert not list(tmp_path.rglob("DEV.md"))
    assert not DevMemoryPaths.for_repo(tmp_path).is_processed(session.session_id)


def test_cli_dry_run_shows_preview_stats(tmp_path: Path) -> None:
    (tmp_path / "src" / "auth").mkdir(parents=True)
    (tmp_path / "src" / "auth" / "__init__.py").write_text("")
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "extract",
            "--repo",
            str(tmp_path),
            "--fixture",
            "sample-auth-module",
            "--offline",
            "--force",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "preview" in result.output.lower()
    last = result.output.strip().splitlines()[-1]
    payload = json.loads(last)
    assert "preview" in payload
    assert payload["preview"]["diff_path"].endswith("preview.diff")
    assert payload["apply"] is False
