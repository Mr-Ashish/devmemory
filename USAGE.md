# USAGE — operational knowledge

> How to work with this part of the system.

## Setup

- Create and activate Python virtual environment: `python3 -m venv .venv && source .venv/bin/activate`.
- `pip install -e '.[dev]'`.
- Set `OPENROUTER_API_KEY` (or `DEVMEMORY_ENV_FILE`) for live extraction.
- Run `./scripts/ensure-hermes.sh` once to install Hermes CLI.

## Common commands

- Dry-run extract (units + proposed paths + unified `preview.diff`): `devmemory extract --fixture sample-auth-module`
- Review knowledge diff: open `.devmemory/out/<run>/preview.diff` or read the colorized CLI print
- Write knowledge: `devmemory extract --fixture sample-auth-module --apply`
- Real Claude session: `devmemory extract --session <id> --apply` (default without flags prefers latest unprocessed Claude session for cwd)
- Offline heuristic: `devmemory extract --offline --apply --force`
- List sessions: `devmemory list-sessions`
- Review knowledge diffs: `devmemory review`
- Tests: `pytest -q`
- Full smoke: `./scripts/smoke-e2e.sh`

## Claude Code hook (SessionEnd)

Install once per project (or use `--user` for all repos):

```bash
./scripts/install-claude-hook.sh
# → merges SessionEnd hook into .claude/settings.json
```

- Default: **background dry-run** of the ending session (or latest unprocessed); log at `.devmemory/hooks.log`.
- Auto-write: `export DEVMEMORY_HOOK_APPLY=1` before Claude Code.
- Prefer **SessionEnd** over **Stop** (Stop fires every turn; thrashy). Opt-in: `./scripts/install-claude-hook.sh --with-stop`.
- Print fragment only: `./scripts/install-claude-hook.sh --print`.
- Hook never blocks Claude (always exit 0); never commits `.env` / `.devmemory/`.

## Troubleshooting

- Hollow `## Architecture` / `## Troubleshooting` headings mean the file predates the empty-section scrub; re-run apply to scrub them.
- After a dogfood run: `devmemory review` then `git diff` as the human gate.
- Hook silent? Check `.devmemory/hooks.log`; ensure `devmemory` is on PATH or `.venv/bin/devmemory` exists; set `DEVMEMORY_HOOK_VERBOSE=1` for stderr.
- Hook skipped on Stop: expected unless `DEVMEMORY_HOOK_ON_STOP=1`.
- Full local loop: `source .venv/bin/activate`, `./scripts/ensure-hermes.sh`, `./scripts/smoke-e2e.sh`, `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase`, `pytest -q`.
