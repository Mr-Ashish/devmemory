# DEV — engineering knowledge

> How this part of the system is built.

## Architecture

- Module layout: `cli.py` (Click CLI), `assemble.py` (bounded context, no LLM), `extract.py` (Hermes orchestration + timings + showcase flag), `normalize.py` (JSON units + post-parse redaction), `apply.py` (merge into DEV.md/USAGE.md), `paths.py` (`list_repo_dirs` + `resolve_unit_path`), `sections.py` (canonicalize section titles), `trace.py` (redacted showcase packaging), `sources/` (fixtures + Claude history/project).
- `agent/` holds SOUL.md, config.yaml and extract-prompt.md used to seed the Hermes home before a live run.
- Runtime state is written under `.devmemory/` (gitignored); curated, redacted public traces are written under `docs/showcase/`.
- Control plane mirrors the Luffy PR-review agent shape: assemble → `hermes -z` → normalize → apply → human git review.
- `extract_session` records per-stage timings (assemble/extract/normalize/apply/total) into `timings.json` in the run dir and surfaces them on `ExtractOutcome`.## Design decisions

- Extraction pipeline stages: assemble → hermes extract → normalize → apply.
- Hermes is used as a CLI dependency (hermes -z), not included as vendored source.
- OpenRouter serves as the LLM provider for extraction.
- Knowledge extraction operates entirely locally with transcripts never leaving the developer's machine.
- Knowledge files (DEV.md and USAGE.md) are maintained colocated next to code modules to keep documentation context-specific and easily accessible.
- The process avoids committing raw AI session transcripts or .devmemory/ run artifacts to source control.
- Extraction pipeline inputs include Claude Code session transcripts, current repository code changes, and outputs knowledge merged into local DEV.md and USAGE.md files.
- CI workflows validate the consistency and freshness of generated knowledge files without requiring access to local transcripts.

- The apply layer is the product quality boundary: path snapping to existing dirs, canonical H2 sections, bullet near-dupe skip, placeholder scrub. The LLM proposes; merge decides.
- Default extraction model is `anthropic/claude-opus-5` (dogfood quality); `openai/gpt-4.1-mini` is acceptable for cheap iteration. Resolution order is `--model` → `DEVMEMORY_MODEL` → default.
- Hermes toolsets are empty by default for extract so the run is pure reasoning over the assembled context; set `DEVMEMORY_TOOLSETS=terminal` only when a run genuinely needs shell access.
- Showcase packaging is opt-in via `--showcase` / `--showcase-dir`; `trace.py` redacts before writing, so only sanitized traces reach `docs/showcase/`.
- `hermes-agent-self-evolution` is an idea source only (session importers, secret-redaction patterns, later skill GEPA) and is not part of the MVP runtime.
- Live runs export `HERMES_TUI_TOOL_PROGRESS=verbose` so dogfood traces capture agent tool progress.

- `DEV_TEMPLATE` / `USAGE_TEMPLATE` in `apply.py` contain only the H1 and the blockquote — canonical H2 sections are created on first real content instead of being pre-scaffolded empty.
- `sections.strip_placeholders` ends by calling `scrub_empty_h2_sections`, so placeholder removal and hollow-heading removal are a single pass on every apply.
- `scrub_empty_h2_sections` drops an `## ` heading plus its trailing blanks when every body line up to the next H2 is whitespace, keeps H1/blockquotes untouched, and collapses runs of blank lines to at most two.## Patterns

- Localized knowledge files (DEV.md for engineering details, USAGE.md for operational instructions) live next to code modules to provide context-targeted documentation.
- DEV.md captures architecture, design decisions, patterns, pitfalls, and module-specific engineering context.
- USAGE.md captures setup steps, commands, debugging, troubleshooting, and workflows essential for working with the code part.
- Extraction process keeps knowledge generation as an automatic by-product of development sessions.

- Schemas are frozen pydantic models: `KnowledgeUnit` / `ExtractionResult` in `schema.py`.
- A session is only marked processed when `units > 0`, so empty or failed runs never poison the cursor.
- An offline heuristic extract (path inference + command-line regex) keeps CI green without an OpenRouter key; it also acts as a fallback when a live run returns no parseable units.
- Dogfood loop: improve the product → run extract on this repo → update DEV/USAGE → capture a showcase package → push.## Pitfalls
- Redacting secrets before parsing breaks JSON — run redaction on string fields *after* the JSON parse in `normalize.py`.
- Without bullet near-dupe skipping, re-running extract thrashes DEV.md/USAGE.md with restated content.
- LLM-invented paths create junk doc trees — always snap a unit's path onto an existing directory (or `.`).
- Enabling terminal tools during extract slows the run and distracts the model from the JSON output contract.
- Never commit `.env` alongside `.devmemory/` and raw transcripts.

- Pre-seeding every canonical H2 leaves hollow headings and `_(none yet)_` placeholders in shipped docs; let the merge create sections lazily.

- `assemble.collect_repo_context` compacts existing DEV.md/USAGE.md before they reach the model: `_compact_knowledge` keeps each `## ` title plus at most 5 bullets, sections with no bullets are dropped entirely, and the result is capped at `DEVMEMORY_MAX_KNOWLEDGE_CHARS` (default 1600) with a `… [truncated; do not restate] …` marker — this is an anti-restate/token-thrift measure, not just truncation.
- `paths.is_knowledge_blocked` filters both the `EXISTING_DIRS` list and the collected knowledge files, so blocked trees (tests/docs-style dirs) can never be offered to the model as a knowledge home.
- The directory list handed to the prompt is `list_repo_dirs` filtered by block rules and truncated to the first 80 entries.

## Design decisions

- Bullet dedupe in `apply.py` is paraphrase-aware, not just exact: `_near_duplicate` accepts a match on substring containment (both bullets >24 chars), Jaccard ≥ 0.52, or coverage of the smaller token set ≥ 0.62.
- `_norm_bullet` strips quotes, underscores and punctuation (`_'".,;:()[]{}`) in addition to backticks/asterisks so restated bullets normalize to the same string.
- `_token_set` applies a longest-suffix-first `_stem` (ations/ation/tions/ing/ers/ies/ed/es/s) and drops tokens ≤2 chars; the stem guard requires `len(t) > len(suf) + 3` to avoid over-stemming words like "existing".
- `dedupe_section_bullets` (first bullet wins) runs on the *existing* section body before new bullets are filtered, so a file that already contains duplicates gets cleaned on the next apply; `scrub_file_near_dupes` applies it per `## ` section and finishes with `strip_placeholders`.

- Session resolution in `cli.py` prefers **real** Claude sessions over packaged fixtures at every entry point: explicit `--session-id` searches Claude first then fixtures, the default path uses `pick_latest_unprocessed` over Claude before falling back to unprocessed fixtures, and the last resort is the newest Claude session even if already processed.
- `devmemory list-sessions` lists Claude rows before fixture rows, adds a `turns` column from `meta`, and prints a `claude=<n> unprocessed_claude=<n> shown=<n>` summary line so it is obvious whether real sessions were discovered at all.

## Pitfalls

- Section-append must preserve the blank line before the next `## ` heading: when the trailing newline is consumed, the following heading is glued onto the last bullet and stops rendering as a heading (`- …maintainability issues.## Patterns`). This regression shows up across every merged DEV.md/USAGE.md at once, so check one file's diff before re-running a full apply.
- Exact-match dedupe is insufficient — the model happily re-emits the same claim in new words (e.g. "breaks JSON — redact after parse" vs "corrupts the payload — run redaction after normalize parses units"). Regression coverage for this lives in `tests/test_apply.py::test_apply_skips_paraphrase_near_dupes`, which asserts the second apply returns `changes == []`.
- Feeding whole knowledge files back into the prompt encourages restatement; send only compacted H2 + top bullets.

- Redacting secrets *before* parsing the model output corrupts the JSON payload; run redaction over string fields **after** parse (in `normalize.py`), never over the raw text.
- Giving the extract step terminal tools slows the run and pulls the model off the JSON output contract — keep toolsets empty unless a specific run needs `DEVMEMORY_TOOLSETS=terminal`.
- Units pointing at directories that do not exist create junk trees; every unit path must snap to an existing repo directory before write.
- Re-running extract without bullet near-dupe skipping thrashes the DEV/USAGE files with restated bullets.

## Patterns

- Schemas are frozen pydantic models (`KnowledgeUnit`, `ExtractionResult`) so normalize/apply operate on validated, immutable units.
- A session is only recorded as processed when it produced `units > 0`, so an empty or failed run never poisons the cursor.
- An offline heuristic extractor (path inference + command-line scraping) keeps CI green without an OpenRouter key.
- The improvement loop is: improve product → run extract on this repo itself → update the colocated DEV/USAGE files → capture a redacted showcase run → push.

- Extraction contracts are frozen pydantic models (`KnowledgeUnit` / `ExtractionResult` in `schema.py`), so malformed or extra LLM fields fail fast at normalize time instead of leaking into `apply.py`.
