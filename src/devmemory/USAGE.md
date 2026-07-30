# USAGE — operational knowledge

> How to work with this part of the system.

## Setup

## Common commands

- Live dogfood extract with showcase: `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase` (add `--showcase-dir <path>` for a custom output dir).
- `--force` re-processes a session that is already recorded in the cursor.
- Point env loading at an external file and pin the model before a live run: `export DEVMEMORY_ENV_FILE=<path to .env>` and `export DEVMEMORY_MODEL=anthropic/claude-opus-5`.
- End-to-end smoke: `./scripts/smoke-e2e.sh`; Hermes-only connectivity check: `./scripts/smoke-hermes.sh`.
- `devmemory review` shows the pending doc changes for human git review.
- The last line of `devmemory extract` stdout is machine-readable JSON including `units`, `changes`, `model`, `hermes_rc`, `timings` and `showcase`.

## Debugging

- `hermes_rc != 0`: inspect `extract.raw.stderr` in the run dir, and confirm the seeded `HERMES_HOME/.env` is mode 0600 and contains `OPENROUTER_API_KEY`.
- Zero units: read `extract.raw.md` for non-JSON output; the offline heuristic fallback should still produce units.
- Wrong unit path: confirm the directory appears in `EXISTING_DIRS` of the assembled prompt and that the tree sample includes the module dir.
- Per-stage `timings.json` in the run dir shows which phase is slow (assemble vs extract vs normalize vs apply).
- Showcase privacy check: `trace.py` strips `sk-or` keys, `Bearer` tokens and env assignments before anything lands in `docs/showcase/`.
- Test coverage targets ≥19 unit tests spanning redaction, normalize, apply dedupe, path snap and offline extract.

## Troubleshooting
