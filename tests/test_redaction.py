from devmemory.redaction import contains_secret, redact


def test_redacts_openrouter_key():
    text = "key is sk-or-v1-abcdefghijklmnopqrstuvwxyz0123456789"
    assert contains_secret(text)
    assert "[REDACTED]" in redact(text)
    assert "sk-or-v1" not in redact(text)


def test_redacts_github_pat():
    text = "token ghp_abcdefghijklmnopqrstuv"
    assert contains_secret(text)
    assert "ghp_" not in redact(text)


def test_clean_text_passthrough():
    text = "run pytest tests/auth -q"
    assert not contains_secret(text)
    assert redact(text) == text
