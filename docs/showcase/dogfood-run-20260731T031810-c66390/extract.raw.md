```json
{
  "summary": "Nearly all of the narrative (architecture, module layout, patterns, pitfalls, commands, debug tips) restates the existing claim index and is dropped. The only new durable knowledge is the R6 change in extract.py: the offline heuristic fallback is now gated on hermes hard-failure or JSON parse failure, so an intentionally empty unit list from the anti-restate model is preserved instead of being replaced by heuristics.",
  "session_ids": ["dogfood-build-narrative"],
  "units": [
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Design decisions",
      "content": "- The offline heuristic fallback in `extract_session` is gated: it runs only when `hermes_rc != 0` or the normalized summary starts with `Failed to parse`. A live run that legitimately returns `units: []` (anti-restate \"nothing new\") is kept as-is.\n- When the fallback does fire, the result is re-stamped via `result.model_copy(update={\"model\": model})` so the recorded model carries the `+offline-fallback` suffix instead of the original model id.",
      "evidence": [
        "parse_failed = (result.summary or \"\").startswith(\"Failed to parse\")",
        "if not result.units and (hermes_rc != 0 or parse_failed):",
        "result = result.model_copy(update={\"model\": model})"
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Pitfalls",
      "content": "- Falling back to the offline extractor on *any* empty unit list defeats anti-restate: heuristic units thrash the DEV/USAGE files and can leak inferred paths. Only a hard Hermes failure or unparseable output justifies the fallback.\n- Regression coverage lives in `tests/test_fixtures_and_offline.py`: `test_intentional_empty_units_skips_offline_fallback` monkeypatches `devmemory.extract.offline_extract` to raise if called, and `test_parse_failure_still_uses_offline_fallback` asserts non-JSON output does yield heuristic units with `offline-fallback` in the model name.",
      "evidence": [
        "Intentional empty units (R6 anti-restate: model says \"nothing new\") must NOT be replaced by offline heuristics (they thrash docs / leak paths).",
        "raise AssertionError(\"offline_extract should not run on intentional empty units\")",
        "assert \"offline-fallback\" in (outcome.result.model or \"\")"
      ],
      "confidence": "high"
    }
  ]
}
```
