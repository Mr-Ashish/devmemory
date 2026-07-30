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


def test_intentional_empty_units_skips_offline_fallback(tmp_path: Path, monkeypatch):
    """R6: live model returning units:[] (nothing new) must not run offline heuristic."""
    (tmp_path / "src").mkdir()
    session = FixtureSource(package_root() / "fixtures" / "sessions").get(
        "sample-auth-module"
    )
    assert session is not None

    empty_json = (
        '{"summary": "Already fully represented in claim index.", '
        '"session_ids": ["sample-auth-module"], "units": []}'
    )

    def fake_hermes(**kwargs):
        kwargs["out_raw"].write_text(empty_json, encoding="utf-8")
        return 0

    monkeypatch.setattr("devmemory.extract.run_hermes_extract", fake_hermes)
    monkeypatch.setattr("devmemory.extract.seed_hermes_home", lambda *a, **k: None)
    monkeypatch.setattr("devmemory.extract.find_hermes", lambda: "/usr/bin/true")

    calls = {"n": 0}

    def boom(*a, **k):
        calls["n"] += 1
        raise AssertionError("offline_extract should not run on intentional empty units")

    monkeypatch.setattr("devmemory.extract.offline_extract", boom)

    outcome = extract_session(
        tmp_path,
        session,
        apply=False,
        offline=False,
        force=True,
        model="anthropic/claude-opus-5",
    )
    assert outcome.result.units == []
    assert "offline-fallback" not in (outcome.result.model or "")
    assert calls["n"] == 0
    assert "claim index" in outcome.result.summary.lower() or "represented" in (
        outcome.result.summary or ""
    ).lower()


def test_parse_failure_still_uses_offline_fallback(tmp_path: Path, monkeypatch):
    (tmp_path / "src").mkdir()
    session = FixtureSource(package_root() / "fixtures" / "sessions").get(
        "sample-auth-module"
    )
    assert session is not None

    def fake_hermes(**kwargs):
        kwargs["out_raw"].write_text("not json at all {{{", encoding="utf-8")
        return 0

    monkeypatch.setattr("devmemory.extract.run_hermes_extract", fake_hermes)
    monkeypatch.setattr("devmemory.extract.seed_hermes_home", lambda *a, **k: None)

    outcome = extract_session(
        tmp_path,
        session,
        apply=False,
        offline=False,
        force=True,
        model="test-model",
    )
    assert outcome.result.units  # offline heuristic produced units
    assert "offline-fallback" in (outcome.result.model or "")
