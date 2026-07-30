"""R7: knowledge form validator (no transcripts)."""

from pathlib import Path

from click.testing import CliRunner

from devmemory.cli import main
from devmemory.validate import discover_knowledge_files, run_validate, validate_file


def test_validate_ok_file(tmp_path: Path):
    p = tmp_path / "DEV.md"
    p.write_text(
        "# DEV — engineering knowledge\n\n"
        "> how\n\n"
        "## Architecture\n\n"
        "- Module layout is clear.\n",
        encoding="utf-8",
    )
    fr = validate_file(p, repo_root=tmp_path)
    assert fr.ok
    assert not any(i.status == "fail" for i in fr.issues)


def test_validate_fails_placeholder(tmp_path: Path):
    p = tmp_path / "DEV.md"
    p.write_text(
        "# DEV — engineering knowledge\n\n## Patterns\n\n_(none yet)_\n",
        encoding="utf-8",
    )
    fr = validate_file(p, repo_root=tmp_path)
    assert not fr.ok
    assert any(i.check == "placeholder" for i in fr.issues)


def test_validate_fails_empty_h2(tmp_path: Path):
    p = tmp_path / "USAGE.md"
    p.write_text(
        "# USAGE — operational knowledge\n\n## Setup\n\n## Common commands\n\n- `pytest -q`\n",
        encoding="utf-8",
    )
    fr = validate_file(p, repo_root=tmp_path)
    assert not fr.ok
    assert any(i.check == "empty_h2" for i in fr.issues)


def test_validate_fails_glued_h2(tmp_path: Path):
    p = tmp_path / "DEV.md"
    p.write_text(
        "# DEV — engineering knowledge\n\n"
        "## Patterns\n\n"
        "- some bullet about maintainability issues.## Pitfalls\n"
        "- Never commit secrets.\n",
        encoding="utf-8",
    )
    fr = validate_file(p, repo_root=tmp_path)
    assert not fr.ok
    assert any(i.check == "glued_h2" for i in fr.issues)


def test_validate_ignores_inline_hash_hash_in_prose(tmp_path: Path):
    """Inline `## Architecture` mentions must not trip glued_h2."""
    p = tmp_path / "USAGE.md"
    p.write_text(
        "# USAGE — operational knowledge\n\n"
        "## Troubleshooting\n\n"
        "- Hollow `## Architecture` headings mean the file predates the scrub.\n",
        encoding="utf-8",
    )
    fr = validate_file(p, repo_root=tmp_path)
    assert fr.ok
    assert not any(i.check == "glued_h2" for i in fr.issues)


def test_validate_fails_blocked_path(tmp_path: Path):
    d = tmp_path / "tests" / "unit"
    d.mkdir(parents=True)
    p = d / "DEV.md"
    p.write_text(
        "# DEV — engineering knowledge\n\n## Patterns\n\n- should not live here\n",
        encoding="utf-8",
    )
    fr = validate_file(p, repo_root=tmp_path)
    assert not fr.ok
    assert any(i.check == "blocked_path" for i in fr.issues)


def test_validate_fails_secret(tmp_path: Path):
    p = tmp_path / "USAGE.md"
    p.write_text(
        "# USAGE — operational knowledge\n\n"
        "## Setup\n\n"
        "- OPENROUTER_API_KEY=sk-or-v1-abcdefghijklmnopqrstuvwxyz012345\n",
        encoding="utf-8",
    )
    fr = validate_file(p, repo_root=tmp_path)
    assert not fr.ok
    assert any(i.check == "secret" for i in fr.issues)


def test_validate_warns_unknown_section(tmp_path: Path):
    p = tmp_path / "DEV.md"
    p.write_text(
        "# DEV — engineering knowledge\n\n## Random thoughts\n\n- A claim.\n",
        encoding="utf-8",
    )
    fr = validate_file(p, repo_root=tmp_path)
    assert fr.ok  # warns only
    assert any(i.check == "unknown_section" and i.status == "warn" for i in fr.issues)


def test_discover_skips_venv(tmp_path: Path):
    (tmp_path / "DEV.md").write_text("# DEV\n\n## A\n\n- x\n", encoding="utf-8")
    bad = tmp_path / ".venv" / "lib"
    bad.mkdir(parents=True)
    (bad / "DEV.md").write_text("# DEV\n\n## A\n\n- x\n", encoding="utf-8")
    found = discover_knowledge_files(tmp_path)
    assert len(found) == 1
    assert found[0].name == "DEV.md"


def test_run_validate_repo(tmp_path: Path):
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "DEV.md").write_text(
        "# DEV — engineering knowledge\n\n## Architecture\n\n- Layers.\n",
        encoding="utf-8",
    )
    (tmp_path / "USAGE.md").write_text(
        "# USAGE — operational knowledge\n\n## Common commands\n\n- `make test`\n",
        encoding="utf-8",
    )
    report = run_validate(tmp_path)
    assert report.ok
    assert report.file_count == 2


def test_cli_validate_json_and_exit(tmp_path: Path):
    (tmp_path / "DEV.md").write_text(
        "# DEV — engineering knowledge\n\n## Patterns\n\n_(none yet)_\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--repo", str(tmp_path), "--json"])
    assert result.exit_code == 1
    assert '"ok": false' in result.output or '"ok": false' in result.output.replace(" ", "")
    assert "placeholder" in result.output


def test_cli_validate_strict_warns(tmp_path: Path):
    (tmp_path / "DEV.md").write_text(
        "# DEV — engineering knowledge\n\n## Random thoughts\n\n- A claim.\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    soft = runner.invoke(main, ["validate", "--repo", str(tmp_path)])
    assert soft.exit_code == 0
    hard = runner.invoke(main, ["validate", "--repo", str(tmp_path), "--strict"])
    assert hard.exit_code == 1
