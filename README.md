# devmemory

Continuous knowledge extraction for AI-native software development.

Treat documentation as a continuously generated artifact of development: extract durable engineering knowledge from local AI coding sessions into colocated **`DEV.md`** and **`USAGE.md`** files that live next to the code they describe.

Built on the **Hermes Agent** runtime + **OpenRouter** (same control-plane pattern as [luffy-pr-review-agent](https://github.com/Mr-Ashish/luffy-pr-review-agent)).

## Why

AI coding sessions produce architecture decisions, trade-offs, commands, and pitfalls — then that knowledge evaporates. Git keeps the code; it does not keep the reasoning. devmemory extracts the durable bits **locally** (transcripts never leave the machine) and writes reviewable knowledge files into the repo.

## Quick start

```bash
# install
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'

# OpenRouter key (or copy from luffy .env)
export OPENROUTER_API_KEY=...
# optional convenience:
# export DEVMEMORY_ENV_FILE=/path/to/pr-review-agent/.env

# Hermes CLI (one-time)
./scripts/ensure-hermes.sh

# offline path (no LLM) — deterministic e2e
devmemory extract --fixture sample-auth-module --offline --apply --force

# live path (Hermes + OpenRouter)
devmemory extract --fixture sample-auth-module --apply --force

# inspect knowledge diffs
devmemory review
```

## CLI

| Command | Purpose |
|---------|---------|
| `devmemory init` | Create `.devmemory/`, seed root templates |
| `devmemory list-sessions` | Fixtures + Claude history for this repo |
| `devmemory extract` | Assemble → extract → normalize → optional apply |
| `devmemory apply --run <id>` | Apply a prior run’s `units.json` |
| `devmemory status` | Processed sessions / recent runs |
| `devmemory review` | git status/diff for knowledge files |

### Extract options

```bash
devmemory extract --fixture sample-auth-module --apply
devmemory extract --session <id> --apply
devmemory extract --text-file ./notes.md --apply --force
devmemory extract --offline --apply   # heuristic, no Hermes
```

## Pipeline

```text
session (fixture | Claude history | file)
  → assemble bounded context
  → hermes -z (OpenRouter)  OR  offline heuristic
  → normalize JSON units
  → apply merge into DEV.md / USAGE.md
  → developer reviews via git
```

## Knowledge files

| File | Answers |
|------|---------|
| `DEV.md` | How is this part built? (architecture, decisions, patterns, pitfalls) |
| `USAGE.md` | How do I work with it? (commands, workflows, debugging) |

Place them at module roots, not only at the repo root.

## Privacy

- Runs entirely on the developer machine.
- State and run artifacts under `.devmemory/` (gitignored).
- Raw transcripts are never committed.
- Secret patterns are redacted from session text and extraction output.

## Layout

```text
agent/           Hermes SOUL, config, extract prompt
src/devmemory/   CLI + pipeline
scripts/         ensure-hermes, smoke, e2e
fixtures/        sample sessions + sample_repo
tests/
```

## Vision (original)

See git history for the full product vision essay: colocated knowledge, continuous extraction, CI validating form (not transcripts). This repo implements the local MVP of that vision.

## License

MIT
