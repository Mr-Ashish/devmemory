# Eval · R5 devmemory doctor · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T030327-011c11` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 4 |
| changes applied | 2 |
| total_s | ~27.4 |
| showcase | `docs/showcase/dogfood-run-20260731T030327-011c11/` |
| tests | **58 passed** (7 new in `test_doctor.py`) |
| code commit | `2526196` |
| doctor | `ready_live=yes` `ready_offline=yes` (sessions warn: fixtures only) |
| smoke-e2e | **E2E_OK** (gpt-4.1-mini live sample-auth-module) |

## What shipped (R5)

1. **`devmemory doctor`** — hermes, OPENROUTER key (masked), sessions, model, git, gitignore, hook, state
2. **`--json` / `--strict`** — machine report; exit 1 unless live-ready
3. **Never prints raw keys** — fingerprint + sha256 only
4. **ready_live / ready_offline** gates for scripts and hooks

## Live proof

```text
devmemory doctor --strict
# → ready_live=yes ready_offline=yes fail=[] warn=[sessions]

devmemory extract --fixture dogfood-build-narrative --apply --force --showcase \
  --model anthropic/claude-opus-5
# → hermes_rc=0 units=4 applied 2 · preview.diff present

./scripts/smoke-e2e.sh
# → E2E_OK
```

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | `src/devmemory/{DEV,USAGE}.md` |
| Kind split | 5 | Patterns + Debugging |
| Dedupe | 3.5 | frozen-pydantic restates again (R6) |
| Privacy | 5 | showcase clean; doctor masks key |
| Actionability | 5 | doctor → fix path is clear |

**Composite: 4.7 / 5**

## R1–R5 milestone

| Item | Evidence |
|------|----------|
| R1 Claude discovery | tests + showcase e5e026 |
| R2 dry-run UX | tests + showcase b45cff |
| R3 SessionEnd hook | tests + scripts + showcase b52ea6 |
| R4 preview.diff | tests + showcase bf64f4 |
| R5 doctor | tests + live ready_live + this eval |

**R5 DONE.** R1–R5 proven with tests + live + smoke-e2e + dogfood ≥4.5/5.
