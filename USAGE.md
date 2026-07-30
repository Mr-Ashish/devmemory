# USAGE — operational knowledge

> How to work with this part of the system.

## Setup

- Create and activate Python virtual environment.
- Set `OPENROUTER_API_KEY` environment variable for live extraction.
- Optionally set `DEVMEMORY_ENV_FILE` for loading env vars.
- Run `./scripts/ensure-hermes.sh` to install Hermes CLI and verify setup.

## Common commands

- pip install -e '.[dev]' to set up development environment.
- Use `devmemory extract --fixture sample-auth-module --apply` to run the extraction and apply knowledge updates.
- Run tests via `pytest -q`.
- Hermes CLI can be installed and ensured via `./scripts/ensure-hermes.sh`.
- Various devmemory CLI commands available: `init`, `list-sessions`, `extract`, `apply --run <id>`, `status`, and `review`.
- Example extract commands: `devmemory extract --fixture sample-auth-module --apply`, `devmemory extract --session <id> --apply`, `devmemory extract --offline --apply` for offline mode.

## Debugging

## Troubleshooting
