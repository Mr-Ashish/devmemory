# Session

- **session_id:** `dogfood-build-narrative`
- **source:** `fixture`
- **project:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **timestamp:** `2026-07-31T02:30:00Z`

## Transcript / notes

We built and dogfooded the entire devmemory product in this repository itself — no external monorepo (no Odoo). Everything below is durable engineering knowledge from the build sessions.

## Architecture decisions

- Control plane mirrors Luffy (luffy-pr-review-agent): assemble → hermes -z → normalize → apply → human git review.
- Hermes Agent is a CLI dependency (not vendored). Inference is OpenRouter. Default model for dogfood quality: anthropic/claude-opus-5; iteration can use gpt-4.1-mini.
- hermes-agent-self-evolution is used for ideas (session importers, secret redaction patterns, later skill GEPA) — not required for the MVP runtime.
- Product knowledge lives as colocated DEV.md (how built) and USAGE.md (how to operate), not a single root brain dump.
- Runtime state lives under .devmemory/ (gitignored). Curated public traces live under docs/showcase/ after redaction.
- Apply layer is the product quality boundary: path snap to existing dirs, canonical H2 sections, bullet near-dupe skip, placeholder scrub. LLM proposes; merge decides.
- Default Hermes toolsets are empty for extract (pure reasoning over assembled context). Override DEVMEMORY_TOOLSETS=terminal only when needed.

## Module layout

- src/devmemory/cli.py — Click CLI
- src/devmemory/assemble.py — bounded context (no LLM)
- src/devmemory/extract.py — Hermes orchestration + timings + showcase flag
- src/devmemory/normalize.py — JSON units + redaction after parse
- src/devmemory/apply.py — merge into DEV.md/USAGE.md
- src/devmemory/paths.py — list_repo_dirs + resolve_unit_path
- src/devmemory/sections.py — canonicalize section titles
- src/devmemory/trace.py — redacted showcase packaging
- src/devmemory/sources/ — fixtures + Claude history/project
- agent/ — SOUL.md, config.yaml, extract-prompt.md for Hermes home seeding

## Patterns

- Frozen schemas via pydantic KnowledgeUnit / ExtractionResult.
- Only mark sessions processed when units > 0 (do not poison cursor on empty runs).
- Offline heuristic extract for CI without OpenRouter (path inference + command lines).
- Dogfood loop: improve product → run extract on self → update DEV/USAGE → capture showcase → push.

## Pitfalls

- Never commit .devmemory/ or raw transcripts or .env.
- Pre-parse secret redaction can break JSON — redact string fields after parse.
- Re-running without bullet dedupe thrashs docs — always near-dupe skip.
- Invented paths create junk trees — always snap to existing directories.
- Using terminal tools on extract slows and distracts the model from JSON contract.

## Commands that worked

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
export DEVMEMORY_ENV_FILE=/Users/ashishmishra/Documents/experiments/pr-review-agent/.env
export DEVMEMORY_MODEL=anthropic/claude-opus-5
./scripts/ensure-hermes.sh
./scripts/smoke-e2e.sh
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase
pytest -q
devmemory review
```

## Debug tips

- If hermes_rc != 0: check extract.raw.stderr and HERMES_HOME/.env mode 0600 + OPENROUTER_API_KEY.
- If units empty: inspect extract.raw.md for non-JSON; offline fallback should still produce units.
- If wrong path: ensure path appears in EXISTING_DIRS in assembled prompt and tree contains the module dir.
- Showcase privacy: trace.py redacts sk-or / Bearer / env assignments before writing docs/showcase/.

## Eval notes

- Unit tests cover redaction, normalize, apply dedupe, path snap, offline extract (target ≥19 tests).
- Live eval: smoke-hermes pong + fixture extract produces src/auth DEV/USAGE split with high confidence.
- Dogfood eval: self-extract improves root and package DEV.md without reintroducing _(none yet)_ placeholders.
