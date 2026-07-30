from pathlib import Path

from devmemory.extract import extract_session, offline_extract, package_root
from devmemory.sources.fixtures import FixtureSource
from devmemory.state import DevMemoryPaths


def test_fixture_load():
    fixtures = package_root() / "fixtures" / "sessions"
    sessions = FixtureSource(fixtures).list_sessions()
    assert any(s.session_id == "sample-auth-module" for s in sessions)


def test_offline_extract_maps_auth_path(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    (tmp_path / "src" / "auth" / "__init__.py").write_text("")
    fixtures = package_root() / "fixtures" / "sessions"
    session = FixtureSource(fixtures).get("sample-auth-module")
    assert session is not None
    result = offline_extract(session, tmp_path)
    assert result.units
    kinds = {u.kind for u in result.units}
    # should capture both design and commands from the rich fixture
    assert "dev" in kinds or "usage" in kinds
    paths = {u.path for u in result.units}
    assert "src/auth" in paths or "." in paths


def test_offline_extract_apply(tmp_path: Path):
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
    assert outcome.result.units
    text = ""
    for p in tmp_path.rglob("DEV.md"):
        text += p.read_text()
    for p in tmp_path.rglob("USAGE.md"):
        text += p.read_text()
    assert text
    assert "_(none yet)_" not in text
    paths = DevMemoryPaths.for_repo(tmp_path)
    assert paths.is_processed("sample-auth-module")
