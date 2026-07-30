"""R2: dry-run shows units + proposed paths; --apply writes and marks processed."""

from pathlib import Path

from click.testing import CliRunner

from devmemory.apply import apply_result, plan_result
from devmemory.cli import main
from devmemory.extract import extract_session, package_root
from devmemory.schema import ExtractionResult, KnowledgeUnit
from devmemory.sources.fixtures import FixtureSource
from devmemory.state import DevMemoryPaths


def _auth_result() -> ExtractionResult:
    return ExtractionResult(
        units=[
            KnowledgeUnit(
                kind="dev",
                path="src/auth",
                action="merge",
                section="Design decisions",
                content="- Use JWT middleware for signed sessions",
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


def test_plan_result_does_not_write(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    planned = plan_result(tmp_path, _auth_result())
    assert len(planned) == 2
    assert all(c.applied is False for c in planned)
    paths = {str(c.path.relative_to(tmp_path)) for c in planned}
    assert "src/auth/DEV.md" in paths
    assert "USAGE.md" in paths
    # no knowledge files written
    assert not (tmp_path / "src" / "auth" / "DEV.md").exists()
    assert not (tmp_path / "USAGE.md").exists()


def test_apply_result_writes_after_plan(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    assert plan_result(tmp_path, _auth_result())
    changes = apply_result(tmp_path, _auth_result())
    assert len(changes) == 2
    assert all(c.applied is True for c in changes)
    assert "JWT middleware" in (tmp_path / "src" / "auth" / "DEV.md").read_text()
    assert "pytest" in (tmp_path / "USAGE.md").read_text()


def test_extract_dry_run_offline_no_write_no_cursor(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    (tmp_path / "src" / "auth" / "__init__.py").write_text("")
    fixtures = package_root() / "fixtures" / "sessions"
    session = FixtureSource(fixtures).get("sample-auth-module")
    assert session is not None

    outcome = extract_session(
        tmp_path,
        session,
        apply=False,
        offline=True,
        force=True,
    )
    assert outcome.result.units
    assert outcome.changes  # proposed paths present
    assert all(c.applied is False for c in outcome.changes)
    # dry-run must not write knowledge files
    assert not list(tmp_path.rglob("DEV.md"))
    assert not list(tmp_path.rglob("USAGE.md"))
    # dry-run must not mark processed
    paths = DevMemoryPaths.for_repo(tmp_path)
    assert not paths.is_processed(session.session_id)
    # plan.json artifact
    assert (outcome.run_dir / "plan.json").exists()
    assert not (outcome.run_dir / "apply.json").exists()


def test_extract_apply_marks_processed(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    (tmp_path / "src" / "auth" / "__init__.py").write_text("")
    fixtures = package_root() / "fixtures" / "sessions"
    session = FixtureSource(fixtures).get("sample-auth-module")
    assert session is not None

    outcome = extract_session(
        tmp_path,
        session,
        apply=True,
        offline=True,
        force=True,
    )
    assert outcome.changes
    assert all(c.applied is True for c in outcome.changes)
    assert list(tmp_path.rglob("DEV.md")) or list(tmp_path.rglob("USAGE.md"))
    paths = DevMemoryPaths.for_repo(tmp_path)
    assert paths.is_processed(session.session_id)
    assert (outcome.run_dir / "apply.json").exists()


def test_cli_dry_run_json_includes_proposed(tmp_path: Path):
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
    assert "dry-run" in result.output or "proposed" in result.output
    # last line machine JSON
    last = result.output.strip().splitlines()[-1]
    import json

    payload = json.loads(last)
    assert payload["apply"] is False
    assert payload["units"] >= 1
    assert isinstance(payload["proposed"], list)
    assert payload["proposed"], "expected proposed knowledge paths"
    assert all(p.get("applied") is False for p in payload["proposed"])
    # still no writes under tmp repo
    assert not list(tmp_path.rglob("DEV.md"))
