```json
{
  "summary": "Durable knowledge from the devmemory self-dogfood build sessions: pydantic frozen schemas and cursor-safety in the extract pipeline, an offline heuristic extract path for CI, redaction ordering and toolset pitfalls, live/dogfood eval acceptance criteria, and the empty-units debugging routine.",
  "session_ids": ["dogfood-build-narrative"],
  "units": [
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Patterns",
      "content": "- Extraction contracts are frozen pydantic models (`KnowledgeUnit` / `ExtractionResult` in `schema.py`); normalize validates the model's JSON against them instead of hand-rolling dict checks.\n- A session is only recorded as processed when the run produced `units > 0`, so an empty or failed extract never poisons the cursor and the session stays eligible for a retry.\n- An offline heuristic extract path (path inference from mentioned modules + command-line scraping) lets CI exercise the full assemble → normalize → apply pipeline with no OpenRouter key.",
      "evidence": [
        "Frozen schemas via pydantic KnowledgeUnit / ExtractionResult.",
        "Only mark sessions processed when units > 0 (do not poison cursor on empty runs).",
        "Offline heuristic extract for CI without OpenRouter (path inference + command lines)."
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Pitfalls",
      "content": "- Do not redact secrets before JSON parsing: rewriting the raw model output breaks the JSON payload. Redaction runs on string fields *after* parse in `normalize.py`.\n- Giving the extract step terminal/filesystem tools makes runs slower and pulls the model off the JSON output contract into exploration; keep toolsets empty unless a run genuinely needs them.\n- Inventing target paths grows junk directory trees — every unit path must snap to a directory that already exists in the repo.",
      "evidence": [
        "Pre-parse secret redaction can break JSON — redact string fields after parse.",
        "Using terminal tools on extract slows and distracts the model from JSON contract.",
        "Invented paths create junk trees — always snap to existing directories."
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": ".",
      "action": "merge",
      "section": "Patterns",
      "content": "- Live eval acceptance: `./scripts/smoke-hermes.sh` returns a pong, then a fixture extract must split knowledge into `src/auth` DEV.md + USAGE.md units at high confidence.\n- Dogfood eval acceptance: a self-extract must improve both the root and package DEV.md without reintroducing `_(none yet)_` placeholders or hollow H2 sections.",
      "evidence": [
        "Live eval: smoke-hermes pong + fixture extract produces src/auth DEV/USAGE split with high confidence.",
        "Dogfood eval: self-extract improves root and package DEV.md without reintroducing _(none yet)_ placeholders."
      ],
      "confidence": "medium"
    },
    {
      "kind": "usage",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Debugging",
      "content": "- Zero units returned: open `extract.raw.md` in the run dir and look for non-JSON prose or a truncated fence; the offline heuristic fallback should still yield units, so a truly empty result points at the assembled prompt rather than the model.\n- `hermes_rc != 0`: read `extract.raw.stderr`, then verify the Hermes home `.env` is mode 0600 and actually carries `OPENROUTER_API_KEY`.",
      "evidence": [
        "If units empty: inspect extract.raw.md for non-JSON; offline fallback should still produce units.",
        "If hermes_rc != 0: check extract.raw.stderr and HERMES_HOME/.env mode 0600 + OPENROUTER_API_KEY."
      ],
      "confidence": "high"
    }
  ]
}
```
