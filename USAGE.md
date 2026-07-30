# USAGE — operational knowledge

> How to work with this part of the system.

## Setup

- Create and activate Python virtual environment.
- Set `OPENROUTER_API_KEY` environment variable for live extraction.
- Optionally set `DEVMEMORY_ENV_FILE` for loading env vars.
- Run `./scripts/ensure-hermes.sh` to install Hermes CLI and verify setup.## Common commands

- pip install -e '.[dev]' to set up development environment.
- Use `devmemory extract --fixture sample-auth-module` for a dry-run (units + proposed paths); add `--apply` to write DEV.md/USAGE.md.
- Run tests via `pytest -q`.
- Hermes CLI can be installed and ensured via `./scripts/ensure-hermes.sh`.
- Various devmemory CLI commands available: `init`, `list-sessions`, `extract`, `apply --run <id>`, `status`, and `review`.
- Example extract commands: `devmemory extract --fixture sample-auth-module` (dry-run), `devmemory extract --fixture sample-auth-module --apply`, `devmemory extract --session <id> --apply`, `devmemory extract --offline --apply` for offline mode.

## Troubleshooting


- Hollow `## Architecture` / `## Troubleshooting` headings left in a DEV.md or USAGE.md mean the file predates the empty-section scrub; re-running any apply against that file removes them automatically.
- After a dogfood run, `devmemory review` then plain `git diff` is the intended human gate — expect the diff to include deletions of previously empty H2 sections, not just added bullets.
- Full local loop before pushing: `source .venv/bin/activate`, `./scripts/ensure-hermes.sh`, `./scripts/smoke-e2e.sh`, `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase`, `pytest -q`.

## Common commands

- Create the environment once per shell: `python3 -m venv .venv && source .venv/bin/activate`.
- Run the test suite with `pytest -q` before pushing any apply-layer change.
- Review pending doc changes as a human gate with `devmemory review`, then use normal `git` review before committing.
