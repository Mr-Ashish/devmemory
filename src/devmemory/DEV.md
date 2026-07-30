# DEV — engineering knowledge

> How this part of the system is built.

## Architecture

- Module layout: `cli.py` (Click CLI), `assemble.py` (bounded context, no LLM), `extract.py` (Hermes orchestration + timings + showcase flag), `normalize.py` (JSON units + post-parse redaction), `apply.py` (merge into DEV.md/USAGE.md), `paths.py` (`list_repo_dirs` + `resolve_unit_path`), `sections.py` (canonicalize section titles), `trace.py` (redacted showcase packaging), `sources/` (fixtures + Claude history/project).
- `agent/` holds SOUL.md, config.yaml and extract-prompt.md used to seed the Hermes home before a live run.
- Runtime state is written under `.devmemory/` (gitignored); curated, redacted public traces are written under `docs/showcase/`.
- Control plane mirrors the Luffy PR-review agent shape: assemble → `hermes -z` → normalize → apply → human git review.
- `extract_session` records per-stage timings (assemble/extract/normalize/apply/total) into `timings.json` in the run dir and surfaces them on `ExtractOutcome`.

- `validate.py` is the form checker for colocated DEV.md/USAGE.md: H1 present, no `_(none yet)_` placeholders, no empty H2 sections, no glued mid-line `##` headings, knowledge not under blocked trees (`tests/`, `docs/`, `fixtures/`, `assets/`, `scripts/`), and a secret-pattern scan; non-canonical H2 titles are warnings, not failures.
- `scripts/validate-knowledge.sh` wraps `devmemory validate --strict`; `.github/workflows/ci.yml` runs pytest plus a soft (non-`--strict`) `devmemory validate`, so warnings do not break CI while hard form errors do.

- `hook_gate.py` owns the SessionEnd run/skip decision: `should_run_extract_for_session` is called by `scripts/claude-code-hook.sh` *before* it spawns the extract process, so a skipped session costs no Hermes/CLI startup.
- `DEVMEMORY_HOOK_FORCE=1` short-circuits the gate entirely (always extract); `DEVMEMORY_HOOK_REQUIRE_EDITS=0` restores the pre-gate always-run behavior.

- `watch.py` is a polling watcher that discovers new Claude sessions for the repo cwd and drives the normal extract pipeline for each candidate.
- Watcher state lives in `.devmemory/watch.json` and records seen-session fingerprints of the form `id|timestamp|textlen`, so a session that grows after being seen is re-detected while unchanged sessions are skipped.
- CLI surface: `devmemory watch` with `--once` / `--interval` / `--apply` / `--offline` / `--require-edits` / `--allow-chat` / `--json`.

## Design decisions

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
- `hermes-agent-self-evolution` is an idea source only (session importers, secret-redaction patterns, later skill GEPA) and is not part of the MVP runtime.
- Live runs export `HERMES_TUI_TOOL_PROGRESS=verbose` so dogfood traces capture agent tool progress.

- `DEV_TEMPLATE` / `USAGE_TEMPLATE` in `apply.py` contain only the H1 and the blockquote — canonical H2 sections are created on first real content instead of being pre-scaffolded empty.
- `sections.strip_placeholders` ends by calling `scrub_empty_h2_sections`, so placeholder removal and hollow-heading removal are a single pass on every apply.
- `scrub_empty_h2_sections` drops an `## ` heading plus its trailing blanks when every body line up to the next H2 is whitespace, keeps H1/blockquotes untouched, and collapses runs of blank lines to at most two.

- Form validation is deliberately a separate, dependency-free stage from extraction: `validate.py` is pure Python with no Hermes subprocess, no OpenRouter call and no session/transcript access, so CI can gate knowledge shape on any runner without an API key.
- `--strict` (fail on warnings) is reserved for the local/script path; CI stays soft so canonical-H2 drift reports without blocking merges.

- `watch` exists as a backup path for repos where the Claude Code SessionEnd hook is not installed; like the hook, its default extract is dry-run and writing requires `--apply`.
- The tool-edit gate is applied only to per-session project JSONL transcripts, never to the shared `history.jsonl`: history is multi-session, so gating it as one transcript would false-skip every row.
- `max_extracts` per poll cycle defaults to 3 to avoid stampeding Hermes with concurrent/backlogged extractions.

## Patterns

- DEV.md captures architecture, design decisions, patterns, pitfalls, and module-specific engineering context.
- USAGE.md captures setup steps, commands, debugging, troubleshooting, and workflows essential for working with the code part.
- Extraction process keeps knowledge generation as an automatic by-product of development sessions.

- Schemas are frozen pydantic models: `KnowledgeUnit` / `ExtractionResult` in `schema.py`.
- A session is only marked processed when `units > 0`, so empty or failed runs never poison the cursor.
- An offline heuristic extract (path inference + command-line regex) keeps CI green without an OpenRouter key; it also acts as a fallback when a live run returns no parseable units.
- Dogfood loop: improve the product → run extract on this repo → update DEV/USAGE → capture a showcase package → push.

- The unit suite is expected to cover the merge-quality surfaces specifically — redaction, normalize, apply dedupe, path snapping and offline extract — with roughly 19+ tests as the floor.

- Edit-class tool allowlist for the hook gate: `Write`, `Edit`, `MultiEdit`, `NotebookEdit`, `Create`, `str_replace`, `apply_patch`, `Delete`.
- Detection reads Claude `tool_use` content blocks or `tool_complete` traces, fronted by a fast regex pre-scan over JSONL lines so large transcripts are not fully parsed.
- Bash-only sessions count as non-edits: shell activity is not treated as a durable code-write signal.

- `find_watch_candidates` filters out both cursor-processed sessions and already-seen fingerprints before proposing work.
- `mark_seen` is called after an extract *and* after an extract error, so a session that reliably fails cannot become a poison loop that blocks every later cycle.
- `watch --once` is the entry point for cron jobs and tests; each cycle prints a machine-readable JSON summary line on stdout.

## Pitfalls
- Redacting secrets before parsing breaks JSON — run redaction on string fields *after* the JSON parse in `normalize.py`.
- Without bullet near-dupe skipping, re-running extract thrashes DEV.md/USAGE.md with restated content.
- LLM-invented paths create junk doc trees — always snap a unit's path onto an existing directory (or `.`).
- Enabling terminal tools during extract slows the run and distracts the model from the JSON output contract.
- Never commit `.env` alongside `.devmemory/` and raw transcripts.

- Pre-seeding every canonical H2 leaves hollow headings and `_(none yet)_` placeholders in shipped docs; let the merge create sections lazily.

- `assemble.collect_repo_context` compacts existing DEV.md/USAGE.md before they reach the model: `_compact_knowledge` keeps each `## ` title plus at most 5 bullets, sections with no bullets are dropped entirely, and the result is capped at `DEVMEMORY_MAX_KNOWLEDGE_CHARS` (default 1600) with a `… [truncated; do not restate] …` marker — this is an anti-restate/token-thrift measure, not just truncation.
- `paths.is_knowledge_blocked` filters both the `EXISTING_DIRS` list and the collected knowledge files, so blocked trees (tests/docs-style dirs) can never be offered to the model as a knowledge home.
- The directory list handed to the prompt is `list_repo_dirs` filtered by block rules and truncated to the first 80 entries.

- The glued-heading check must ignore inline code mentions: a backticked `## Architecture` inside prose is documentation, not a mid-line heading, and flagging it produces false failures on the project's own DEV.md files.

- Do not treat every JSON `name` field in a transcript as a tool invocation — require a `tool_use` type or surrounding tool-event context, or unrelated payload keys produce false edit signals.
- The gate must never block Claude: gate exceptions and import errors fall through to *allow* extract, and the hook script always exits 0.

- `watch` enters a forever loop only when neither `--once` nor `--max-polls` is given; tests must always pass `--once` or they will hang.

## Design decisions

- Bullet dedupe in `apply.py` is paraphrase-aware, not just exact: `_near_duplicate` accepts a match on substring containment (both bullets >24 chars), Jaccard ≥ 0.52, or coverage of the smaller token set ≥ 0.62.
- `_norm_bullet` strips quotes, underscores and punctuation (`_'".,;:()[]{}`) in addition to backticks/asterisks so restated bullets normalize to the same string.
- `_token_set` applies a longest-suffix-first `_stem` (ations/ation/tions/ing/ers/ies/ed/es/s) and drops tokens ≤2 chars; the stem guard requires `len(t) > len(suf) + 3` to avoid over-stemming words like "existing".

- `devmemory list-sessions` lists Claude rows before fixture rows, adds a `turns` column from `meta`, and prints a `claude=<n> unprocessed_claude=<n> shown=<n>` summary line so it is obvious whether real sessions were discovered at all.

- When the fallback does fire, the result is re-stamped via `result.model_copy(update={"model": model})` so the recorded model carries the `+offline-fallback` suffix instead of the original model id.

## Pitfalls

- Feeding whole knowledge files back into the prompt encourages restatement; send only compacted H2 + top bullets.

- Falling back to the offline extractor on *any* empty unit list defeats anti-restate: heuristic units thrash the DEV/USAGE files and can leak inferred paths. Only a hard Hermes failure or unparseable output justifies the fallback.
- Regression coverage lives in `tests/test_fixtures_and_offline.py`: `test_intentional_empty_units_skips_offline_fallback` monkeypatches `devmemory.extract.offline_extract` to raise if called, and `test_parse_failure_still_uses_offline_fallback` asserts non-JSON output does yield heuristic units with `offline-fallback` in the model name.

## Patterns

- The processed-session cursor is only advanced when a run yields `units > 0`; empty runs leave the session unprocessed so it can be retried instead of being silently burned.
