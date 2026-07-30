# Eval · R7 CI form-validator · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T032614-a2aa70` (R7 ship narrative) |
| companion | `run-20260731T032535-73934d` (dogfood-build-narrative re-run) |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 4 (R7) · 1 (narrative re-run) |
| preview | +12/−0 (R7) |
| total_s | ~23 |
| showcase | `docs/showcase/dogfood-run-20260731T032614-a2aa70/` |
| tests | **75 passed** (12 in `test_validate.py`) |
| code commit | `715a38c` |
| validate | `ok=yes` fail=0 warn=1 (custom USAGE H2 for Claude hook) |

## What shipped (R7)

1. **`devmemory validate`** — pure Python form gate, no transcripts / Hermes / keys
2. Checks: H1, placeholders, empty H2, glued section H2 (ignore inline `` `## X` ``), blocked path, secrets, unknown section warn
3. **`--json` / `--strict`** — machine CI; strict fails on warns
4. **`scripts/validate-knowledge.sh`** + **`.github/workflows/ci.yml`** (pytest + soft validate)
5. Repaired historical glued-H2 thrash in knowledge files

## Live proof

```text
devmemory validate
# → ok=yes fail=0 warn=1

devmemory extract --text-file r7-session.txt --session r7-validate-ship \
  --apply --force --showcase --model anthropic/claude-opus-5
# → hermes_rc=0 units=4 applied to src/devmemory/{DEV,USAGE}.md
```

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | `src/devmemory/{DEV,USAGE}.md` |
| Kind split | 5 | Architecture / Design / Pitfalls + Common commands |
| Dedupe | 5 | only net-new R7 claims; claim index held narrative thrash |
| Privacy | 5 | no keys; validate itself scans secrets |
| Actionability | 5 | `devmemory validate --json` + script landed in USAGE |

**Composite: 5.0 / 5**

## Milestone

R1–R7 proven (tests + live). Next: **hook apply gate** (tool-edit only) or **R8 watch** when real Claude sessions land.
