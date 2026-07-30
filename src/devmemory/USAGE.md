# USAGE — operational knowledge

> How to work with this part of the system.

## Common commands

- Live dogfood extract with showcase: `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase` (add `--showcase-dir <path>` for a custom output dir).
- `--force` re-processes a session that is already recorded in the cursor.
- Point env loading at an external file and pin the model before a live run: `export DEVMEMORY_ENV_FILE=<path to .env>` and `export DEVMEMORY_MODEL=anthropic/claude-opus-5`.
- End-to-end smoke: `./scripts/smoke-e2e.sh`; Hermes-only connectivity check: `./scripts/smoke-hermes.sh`.
- `devmemory review` shows the pending doc changes for human git review.
- The last line of `devmemory extract` stdout is machine-readable JSON including `units`, `changes`, `model`, `hermes_rc`, `timings` and `showcase`.## Debugging

- `hermes_rc != 0`: inspect `extract.raw.stderr` in the run dir, and confirm the seeded `HERMES_HOME/.env` is mode 0600 and contains `OPENROUTER_API_KEY`.
- Zero units: read `extract.raw.md` for non-JSON output; the offline heuristic fallback should still produce units.
- Wrong unit path: confirm the directory appears in `EXISTING_DIRS` of the assembled prompt and that the tree sample includes the module dir.
- Per-stage `timings.json` in the run dir shows which phase is slow (assemble vs extract vs normalize vs apply).
- Showcase privacy check: `trace.py` strips `sk-or` keys, `Bearer` tokens and env assignments before anything lands in `docs/showcase/`.
- Test coverage targets ≥19 unit tests spanning redaction, normalize, apply dedupe, path snap and offline extract.

## Troubleshooting

- Context size is tunable via env: `DEVMEMORY_MAX_SESSION_CHARS` (24000), `DEVMEMORY_MAX_DIFF_CHARS` (40000), `DEVMEMORY_MAX_TREE_LINES` (200), `DEVMEMORY_MAX_KNOWLEDGE_CHARS` (1600). Raise these only when the model is clearly missing evidence — larger prompts increase restatement.
- Unit landed under the wrong directory: confirm the target appears in the `EXISTING_DIRS` block of the assembled prompt and that the module dir shows up in the tree sample; blocked trees are filtered out on purpose and will never be accepted.
- Docs growing on every run: verify near-dupe skipping is active (`apply.dedupe_section_bullets` / `scrub_file_near_dupes`) rather than editing the docs by hand.
- Before publishing a run, remember `trace.py` redacts `sk-or` / `Bearer` tokens and env assignments on the way into `docs/showcase/` — never copy files there manually.

## Debugging

- Non-zero `hermes_rc`: read `extract.raw.stderr` in the run dir, then confirm `HERMES_HOME/.env` is mode 0600 and that `OPENROUTER_API_KEY` is set.
- Zero units returned: open `extract.raw.md` and look for non-JSON preamble; the offline heuristic path should still yield units, so an empty result there points at the assembled prompt rather than the model.
- No real sessions being picked up: run `devmemory list-sessions` and read the trailing `claude=… unprocessed_claude=…` counters; if they are 0, point `DEVMEMORY_CLAUDE_HISTORY` / `DEVMEMORY_CLAUDE_PROJECTS` at the right locations (they also exist so tests can use fixtures).
- Sessions appearing in the wrong order usually means a timestamp was compared as a string — history entries are epoch milliseconds and must go through the seconds normalizer.

- `hermes_rc != 0`: read `extract.raw.stderr`, then verify the Hermes home `.env` is mode 0600 and actually carries `OPENROUTER_API_KEY`.
