from devmemory.normalize import normalize_extraction


def test_normalize_fenced_json():
    raw = """```json
{
  "summary": "auth notes",
  "units": [
    {
      "kind": "dev",
      "path": "src/auth",
      "action": "merge",
      "section": "Design decisions",
      "content": "- JWT HS256 for now",
      "evidence": ["session"],
      "confidence": "high"
    }
  ]
}
```"""
    result = normalize_extraction(raw, session_ids=["s1"])
    assert len(result.units) == 1
    assert result.units[0].kind == "dev"
    assert result.units[0].path == "src/auth"
    assert result.summary == "auth notes"


def test_normalize_redacts_secrets_in_content():
    raw = """{
  "summary": "x",
  "units": [{
    "kind": "usage",
    "path": ".",
    "content": "export OPENROUTER_API_KEY=sk-or-v1-abcdefghijklmnopqrstuvwxyz",
    "confidence": "medium"
  }]
}"""
    result = normalize_extraction(raw)
    assert len(result.units) == 1
    assert "sk-or-v1" not in result.units[0].content
    assert "[REDACTED]" in result.units[0].content


def test_normalize_empty_on_garbage():
    result = normalize_extraction("sorry I cannot help with that")
    assert result.units == []
