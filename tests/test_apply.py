from pathlib import Path

from devmemory.apply import apply_result, apply_unit
from devmemory.schema import ExtractionResult, KnowledgeUnit


def test_apply_creates_dev_and_usage(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    result = ExtractionResult(
        units=[
            KnowledgeUnit(
                kind="dev",
                path="src/auth",
                action="merge",
                section="Design decisions",
                content="- Use JWT middleware",
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
    changes = apply_result(tmp_path, result)
    assert len(changes) == 2
    dev = tmp_path / "src" / "auth" / "DEV.md"
    usage = tmp_path / "USAGE.md"
    assert dev.exists()
    assert usage.exists()
    assert "JWT middleware" in dev.read_text()
    assert "pytest" in usage.read_text()
    assert "_(none yet)_" not in dev.read_text()


def test_apply_skips_duplicate(tmp_path: Path):
    result = ExtractionResult(
        units=[
            KnowledgeUnit(
                kind="dev",
                path=".",
                section="Architecture",
                content="- Idempotent note about the system",
                confidence="high",
            )
        ]
    )
    assert len(apply_result(tmp_path, result)) == 1
    assert len(apply_result(tmp_path, result)) == 0


def test_apply_skips_near_duplicate_bullets(tmp_path: Path):
    apply_result(
        tmp_path,
        ExtractionResult(
            units=[
                KnowledgeUnit(
                    kind="dev",
                    path=".",
                    section="Design decisions",
                    content="- Tokens are signed with HS256 for now",
                    confidence="high",
                )
            ]
        ),
    )
    changes = apply_result(
        tmp_path,
        ExtractionResult(
            units=[
                KnowledgeUnit(
                    kind="dev",
                    path=".",
                    section="Design decisions",
                    content="- Tokens are signed with HS256 for now; migrate later",
                    confidence="high",
                )
            ]
        ),
    )
    # near-duplicate should be skipped
    assert changes == []


def test_apply_skips_paraphrase_near_dupes(tmp_path: Path):
    apply_result(
        tmp_path,
        ExtractionResult(
            units=[
                KnowledgeUnit(
                    kind="dev",
                    path=".",
                    section="Pitfalls",
                    content="- Redacting secrets before parsing breaks JSON — redact after parse",
                    confidence="high",
                )
            ]
        ),
    )
    changes = apply_result(
        tmp_path,
        ExtractionResult(
            units=[
                KnowledgeUnit(
                    kind="dev",
                    path=".",
                    section="Pitfalls",
                    content="- Redacting secrets before JSON parse corrupts the payload — run redaction after normalize parses units",
                    confidence="high",
                )
            ]
        ),
    )
    assert changes == []


def test_apply_strips_placeholders(tmp_path: Path):
    p = tmp_path / "DEV.md"
    p.write_text(
        "# DEV\n\n## Design decisions\n\n_(none yet)_\n\n",
        encoding="utf-8",
    )
    ch = apply_unit(
        tmp_path,
        KnowledgeUnit(
            kind="dev",
            path=".",
            section="Design decisions",
            content="- Real decision",
            confidence="high",
        ),
    )
    assert ch is not None
    text = p.read_text()
    assert "Real decision" in text
    assert "_(none yet)_" not in text


def test_apply_scrubs_empty_h2_sections(tmp_path: Path):
    p = tmp_path / "DEV.md"
    p.write_text(
        "# DEV\n\n## Architecture\n\n## Design decisions\n\n## Patterns\n\n"
        "## Pitfalls\n- Never commit secrets.\n",
        encoding="utf-8",
    )
    ch = apply_unit(
        tmp_path,
        KnowledgeUnit(
            kind="dev",
            path=".",
            section="Patterns",
            content="- Colocate knowledge with code",
            confidence="high",
        ),
    )
    assert ch is not None
    text = p.read_text()
    assert "## Architecture" not in text  # stayed empty → scrubbed
    assert "## Design decisions" not in text
    assert "## Patterns" in text
    assert "Colocate knowledge" in text
    assert "## Pitfalls" in text
    assert "Never commit secrets" in text


def test_apply_snaps_invented_path_to_existing(tmp_path: Path):
    (tmp_path / "src" / "auth").mkdir(parents=True)
    ch = apply_unit(
        tmp_path,
        KnowledgeUnit(
            kind="dev",
            path="src/auth/middleware/deep/invented",
            section="Patterns",
            content="- require_auth decorator",
            confidence="high",
        ),
    )
    assert ch is not None
    assert ch.path == (tmp_path / "src" / "auth" / "DEV.md").resolve()


def test_apply_canonicalizes_usage_section(tmp_path: Path):
    ch = apply_unit(
        tmp_path,
        KnowledgeUnit(
            kind="usage",
            path=".",
            section="Usage and CLI",
            content="- `devmemory extract --apply`",
            confidence="high",
        ),
    )
    assert ch is not None
    text = (tmp_path / "USAGE.md").read_text()
    assert "## Common commands" in text
    assert "devmemory extract" in text


def test_apply_skips_low_confidence(tmp_path: Path):
    result = ExtractionResult(
        units=[
            KnowledgeUnit(
                kind="dev",
                path=".",
                content="- maybe",
                confidence="low",
            )
        ]
    )
    assert apply_result(tmp_path, result) == []
