```json
{
  "summary": "Nearly all of this session's architecture, module-layout, pitfall and command claims are already recorded in DEV.md / USAGE.md and the claim index. Only three items are genuinely new: the cursor-write rule (mark processed only when units > 0), the offline heuristic extract as the CI path without an OpenRouter key, and the unit-test coverage target for the merge/redaction layers.",
  "session_ids": ["dogfood-build-narrative"],
  "units": [
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Patterns",
      "content": "- A session is only recorded as processed in the state cursor when the run produced at least one unit; empty runs leave the cursor untouched so a failed or zero-unit extract can be retried without `--force`.\n- The offline heuristic extractor (path inference + command-line scraping) is the CI path when no OpenRouter key is present, so knowledge form can be exercised without live inference.\n- The unit suite is expected to cover the merge-quality surfaces specifically — redaction, normalize, apply dedupe, path snapping and offline extract — with roughly 19+ tests as the floor.",
      "evidence": [
        "Only mark sessions processed when units > 0 (do not poison cursor on empty runs)",
        "Offline heuristic extract for CI without OpenRouter (path inference + command lines)",
        "Unit tests cover redaction, normalize, apply dedupe, path snap, offline extract (target ≥19 tests)"
      ],
      "confidence": "medium"
    }
  ]
}
```
