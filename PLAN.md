# devmemory implementation plan

## Status (verified 2026-07-31)

| Phase | Goal | Status |
|-------|------|--------|
| 0 | Scaffold + Hermes/OpenRouter smoke | **done** — `SMOKE_OK` (pong via OpenRouter) |
| 1 | Session discovery + redaction | **done** — fixtures + Claude history + secret filters |
| 2 | Context assembly | **done** — `assemble.py` writes prompt/session/repo-context |
| 3 | Hermes extract + normalize | **done** — live `hermes -z` (no tools by default) + JSON units |
| 4 | Apply DEV.md / USAGE.md | **done** — path snap, section canonicalize, bullet dedupe, no placeholders |
| 5 | CLI + state machine | **done** — init/list/extract/apply/status/review |
| E2E | Live extract+apply | **done** — `scripts/smoke-e2e.sh` → `E2E_OK` |
| ROI pass | Quality fixes | **done** — see below |
| R3 | Claude Code SessionEnd hook + install one-liner | **done** — scripts/claude-code-hook.sh + install-claude-hook.sh |
| R4 | Unified knowledge git-style preview diff | **done** — plan_preview + preview.diff on every extract |
| R5 | devmemory doctor (hermes/key/sessions/model) | **done** — doctor.py + CLI --json/--strict |
| 6 | Watch + CI validation | later (after R1–R5) |
| 7 | Multi-source + skill evolution | later |

## Highest-ROI fixes (quality pass)

1. **Apply quality** — strip `_(none yet)_`, bullet-level near-dupe skip, canonical sections
2. **Path snap** — never invent dirs; map to existing repo paths (`src/auth`, `src/devmemory`)
3. **No toolsets by default** — pure extract over assembled context (faster, less wander)
4. **Prompt** — allowlist dirs + fixed H2 set; forbid exploration
5. **Offline heuristics** — real bullets + path inference for CI
6. **Processed cursor** — only mark sessions that produced units

## Verified live run

- Hermes Agent v0.19.0
- Model: `openai/gpt-4.1-mini` via OpenRouter
- Fixture → `src/auth/{DEV,USAGE}.md` with Architecture/Patterns/Pitfalls split
- **19** pytest tests passing

## Commands

```bash
source .venv/bin/activate
export DEVMEMORY_ENV_FILE=/Users/ashishmishra/Documents/experiments/pr-review-agent/.env
./scripts/ensure-hermes.sh
./scripts/smoke-e2e.sh
devmemory extract --fixture sample-auth-module --apply --force
```
