from pathlib import Path

from devmemory.paths import infer_paths_from_text, list_repo_dirs, resolve_unit_path
from devmemory.sections import canonicalize_section


def test_resolve_snaps_to_existing(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    dirs = list_repo_dirs(tmp_path)
    assert "src/auth" in dirs
    assert resolve_unit_path(tmp_path, "src/auth/foo/bar", existing_dirs=dirs) == "src/auth"
    assert resolve_unit_path(tmp_path, "does/not/exist", existing_dirs=dirs) == "."


def test_resolve_blocks_tests_and_docs(tmp_path: Path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs" / "showcase").mkdir(parents=True)
    (tmp_path / "src" / "devmemory").mkdir(parents=True)
    dirs = list_repo_dirs(tmp_path)
    assert resolve_unit_path(tmp_path, "tests", existing_dirs=dirs) == "."
    assert resolve_unit_path(tmp_path, "docs/showcase", existing_dirs=dirs) == "."
    assert resolve_unit_path(tmp_path, "docs/evals", existing_dirs=dirs) == "."
    assert resolve_unit_path(tmp_path, "src/devmemory", existing_dirs=dirs) == "src/devmemory"


def test_infer_paths_from_session_text(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    dirs = list_repo_dirs(tmp_path)
    text = "put middleware in `src/auth/` and keep tokens separate"
    assert "src/auth" in infer_paths_from_text(text, dirs)


def test_canonicalize_sections():
    assert canonicalize_section("usage", "Usage and CLI") == "Common commands"
    assert canonicalize_section("dev", "gotchas") == "Pitfalls"
    assert canonicalize_section("usage", "Local Development and Debugging") == "Debugging"
