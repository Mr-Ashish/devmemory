# Eval · dogfood Opus 5 · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T021737-6f9c71` |
| model | `anthropic/claude-opus-5` via OpenRouter |
| session | `dogfood-build-narrative` (fixture) |
| hermes_rc | 0 |
| units | 6 |
| total_s | ~35s |
| showcase | `docs/showcase/dogfood-run-20260731T021737-6f9c71/` |

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | All units under `src/devmemory` |
| Kind split | 5 | DEV architecture/decisions/patterns/pitfalls + USAGE commands/debug |
| Dedupe | 5 | Applied as first rich package write; no placeholder pollution |
| Privacy | 5 | Showcase via `trace.py` redaction; no `.env` |
| Actionability | 5 | Concrete venv/install/extract/showcase commands |

**Composite: 5.0 / 5**

## Commands

```bash
export DEVMEMORY_MODEL=anthropic/claude-opus-5
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase
```
