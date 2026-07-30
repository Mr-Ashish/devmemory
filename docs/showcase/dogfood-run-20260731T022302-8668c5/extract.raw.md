```json
{
  "summary": "Durable knowledge from the devmemory dogfood build sessions centers on a new apply-layer quality rule: DEV/USAGE templates no longer scaffold empty H2 sections, and strip_placeholders now scrubs H2 headings whose body is whitespace-only. Also captured: src/devmemory pitfalls (post-parse redaction, near-dupe skip, path snapping, empty toolsets), the showcase run-directory artifact layout, and the eval/test conventions covering the scrub behavior.",
  "session_ids": ["dogfood-build-narrative"],
  "units": [
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Design decisions",
      "content": "- `DEV_TEMPLATE` / `USAGE_TEMPLATE` in `apply.py` contain only the H1 and the blockquote — canonical H2 sections are created on first real content instead of being pre-scaffolded empty.\n- `sections.strip_placeholders` ends by calling `scrub_empty_h2_sections`, so placeholder removal and hollow-heading removal are a single pass on every apply.\n- `scrub_empty_h2_sections` drops an `## ` heading plus its trailing blanks when every body line up to the next H2 is whitespace, keeps H1/blockquotes untouched, and collapses runs of blank lines to at most two.",
      "evidence": [
        "# Sections are created on first content — avoid empty H2 scaffolding.",
        "return scrub_empty_h2_sections(\"\\n\".join(out).rstrip() + \"\\n\")",
        "Drop ## sections whose body is only whitespace (or placeholders already removed)."
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Pitfalls",
      "content": "- Redacting secrets before JSON parse corrupts the payload — run redaction over string fields *after* `normalize.py` parses the units.\n- Re-running extract without bullet near-dupe skipping thrashes DEV.md/USAGE.md with restated bullets.\n- Model-invented paths create junk directory trees; every unit path must snap to a directory that already exists.\n- Enabling terminal tools during extract slows the run and pulls the model off the JSON output contract.\n- Pre-seeding every canonical H2 leaves hollow headings and `_(none yet)_` placeholders in shipped docs; let the merge create sections lazily.",
      "evidence": [
        "Pre-parse secret redaction can break JSON — redact string fields after parse.",
        "Invented paths create junk trees — always snap to existing directories.",
        "Using terminal tools on extract slows and distracts the model from JSON contract."
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "tests",
      "action": "merge",
      "section": "Patterns",
      "content": "- Apply-layer tests drive `apply_unit(tmp_path, KnowledgeUnit(...))` against a hand-written DEV.md in `tmp_path` and assert on the re-read file text.\n- `test_apply_scrubs_empty_h2_sections` is the regression guard for hollow headings: it seeds Architecture/Design decisions/Patterns/Pitfalls, applies one Patterns bullet, then asserts the untouched empty H2s are gone while sections with content survive.\n- Suite layout mirrors the pipeline stages: `test_redaction.py`, `test_normalize.py`, `test_apply.py`, `test_paths_and_sections.py`, `test_fixtures_and_offline.py`, targeting ≥19 tests total.",
      "evidence": [
        "def test_apply_scrubs_empty_h2_sections(tmp_path: Path):",
        "assert \"## Architecture\" not in text  # stayed empty → scrubbed",
        "Unit tests cover redaction, normalize, apply dedupe, path snap, offline extract (target ≥19 tests)."
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "docs/showcase",
      "action": "merge",
      "section": "Architecture",
      "content": "- Each showcase run is a self-contained directory named `dogfood-run-<UTC timestamp>-<short hash>` written by `trace.py` after redaction.\n- A run dir carries the full pipeline audit trail: `prompt.md`, `repo-context.md`, `session.md`, `extract.raw.md`, `units.json`, `apply.json`, `timings.json`, `hermes-usage.json`, `meta.env`, plus `README.md`/`summary.md` and an `agent-loop/` subdir with the redacted Hermes agent log.\n- Only sanitized traces land here; `.devmemory/` holds the unredacted runtime state and stays gitignored.",
      "evidence": [
        "docs/showcase/dogfood-run-20260731T021737-6f9c71/apply.json",
        "docs/showcase/dogfood-run-20260731T021737-6f9c71/agent-loop",
        "Include redacted Hermes agent.log in dogfood showcase"
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "docs/evals",
      "action": "merge",
      "section": "Patterns",
      "content": "- Three eval tiers are kept distinct: unit tests (redaction, normalize, apply dedupe, path snap, offline extract), live eval (`smoke-hermes` pong plus a fixture extract that must yield a `src/auth` DEV/USAGE split at high confidence), and dogfood eval (self-extract must improve root and package DEV.md).\n- Dogfood eval pass criterion is negative as well as positive: the run must not reintroduce `_(none yet)_` placeholders or empty H2 headings into the committed docs.\n- Eval runs are dated and written up per session, e.g. `docs/evals/2026-07-31-dogfood-opus5.md`.",
      "evidence": [
        "Live eval: smoke-hermes pong + fixture extract produces src/auth DEV/USAGE split with high confidence.",
        "Dogfood eval: self-extract improves root and package DEV.md without reintroducing _(none yet)_ placeholders.",
        "docs/evals/2026-07-31-dogfood-opus5.md"
      ],
      "confidence": "medium"
    },
    {
      "kind": "usage",
      "path": ".",
      "action": "merge",
      "section": "Troubleshooting",
      "content": "- Hollow `## Architecture` / `## Troubleshooting` headings left in a DEV.md or USAGE.md mean the file predates the empty-section scrub; re-running any apply against that file removes them automatically.\n- After a dogfood run, `devmemory review` then plain `git diff` is the intended human gate — expect the diff to include deletions of previously empty H2 sections, not just added bullets.\n- Full local loop before pushing: `source .venv/bin/activate`, `./scripts/ensure-hermes.sh`, `./scripts/smoke-e2e.sh`, `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase`, `pytest -q`.",
      "evidence": [
        "-## Architecture\n-\n-## Design decisions\n-\n-## Patterns",
        "devmemory review",
        "./scripts/smoke-e2e.sh"
      ],
      "confidence": "high"
    }
  ]
}
```
