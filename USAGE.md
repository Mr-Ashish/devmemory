# USAGE — operational knowledge

> How to work with this part of the system.

## Setup

- Create and activate Python virtual environment: `python3 -m venv .venv && source .venv/bin/activate`.
- `pip install -e '.[dev]'`.
- Set `OPENROUTER_API_KEY` (or `DEVMEMORY_ENV_FILE`) for live extraction.
- Run `./scripts/ensure-hermes.sh` once to install Hermes CLI.

## Common commands

- Readiness: `devmemory doctor` (table + JSON); `devmemory doctor --strict` fails unless live-ready; `devmemory doctor --json` for CI
- Dry-run extract (units + proposed paths + unified `preview.diff`): `devmemory extract --fixture sample-auth-module`
- Review knowledge diff: open `.devmemory/out/<run>/preview.diff` or read the colorized CLI print
- Real Claude session: `devmemory extract --session <id> --apply` (default without flags prefers latest unprocessed Claude session for cwd)
- Offline heuristic: `devmemory extract --offline --apply --force`
- List sessions: `devmemory list-sessions`
- Tests: `pytest -q`
- Full smoke: `./scripts/smoke-e2e.sh`
- Poll Claude sessions (backup when hook missing): `devmemory watch --once --json` (or `--interval 120 --apply`)

## Claude Code hook (SessionEnd)

Install once per project (or use `--user` for all repos):

```bash
./scripts/install-claude-hook.sh
# → merges SessionEnd hook into .claude/settings.json
```

- Auto-write: `export DEVMEMORY_HOOK_APPLY=1` before Claude Code.
- Prefer **SessionEnd** over **Stop** (Stop fires every turn; thrashy). Opt-in: `./scripts/install-claude-hook.sh --with-stop`.
- **Tool-edit gate (default on):** skips extract when the session transcript has no Write/Edit-class tools (chat-only). Opt out: `export DEVMEMORY_HOOK_REQUIRE_EDITS=0`. Missing transcript still allows a run.
- Print fragment only: `./scripts/install-claude-hook.sh --print`.
- Hook never blocks Claude (always exit 0); never commits `.env` / `.devmemory/`.

## Troubleshooting

- Hollow `## Architecture` / `## Troubleshooting` headings mean the file predates the empty-section scrub; re-run apply to scrub them.
- After a dogfood run: `devmemory review` then `git diff` as the human gate.
- Hook silent? Check `.devmemory/hooks.log`; ensure `devmemory` is on PATH or `.venv/bin/devmemory` exists; set `DEVMEMORY_HOOK_VERBOSE=1` for stderr.
- Hook skipped on Stop: expected unless `DEVMEMORY_HOOK_ON_STOP=1`.
- Hook skipped with `no tool edits`: session was chat-only; write code in the session or set `DEVMEMORY_HOOK_REQUIRE_EDITS=0` / `DEVMEMORY_HOOK_FORCE=1`.
- Live extract fails? Run `devmemory doctor --strict` — fix hermes (`./scripts/ensure-hermes.sh`) or `OPENROUTER_API_KEY` / `DEVMEMORY_ENV_FILE`.
