# Architecture

## One sentence

devmemory is a local control plane that assembles session + repo context, runs Hermes Agent via OpenRouter to extract durable knowledge units, normalizes them, and merges into colocated `DEV.md` / `USAGE.md` for human git review.

## Flow

```text
session (fixture | Claude | file)
  → assemble (no LLM)
  → hermes -z + OpenRouter
  → normalize JSON units
  → apply merge → DEV.md / USAGE.md
  → developer git review
```

## Stages

| Stage | Module / script | Responsibility |
|-------|-----------------|----------------|
| Discover | `sources/*` | Fixtures, Claude history/project JSONL |
| Assemble | `assemble.py` | Bounded prompt + repo snapshot |
| Extract | `extract.py` + Hermes CLI | LLM → raw markdown/JSON |
| Normalize | `normalize.py` | Parse schema, redact secrets |
| Apply | `apply.py` | Section-aware merge into knowledge files |
| State | `state.py` | `.devmemory/` processed session cursor |
| CLI | `cli.py` | User-facing commands |

## Borrowed patterns

- **Luffy** (`pr-review-agent`): Hermes bootstrap, `hermes -z`, HERMES_HOME seeding, OpenRouter env, normalize/repair, trace under run dir
- **Hermes Agent**: runtime only (not forked)
- **hermes-agent-self-evolution**: secret redaction + session import ideas

## Privacy

- `.devmemory/` is gitignored (run artifacts, state, hermes home)
- Knowledge files are intentional product artifacts for commit after review
- Transcripts never leave the machine
