# Eval · R8 watch · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T033900-ad9f76` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 5 |
| changes | 5 → `src/devmemory/{DEV,USAGE}.md` |
| preview | +17 / −0 |
| total_s | ~25 |
| showcase | `docs/showcase/dogfood-run-20260731T033900-ad9f76/` |
| tests | **92 passed** (`test_watch.py` + suite) |
| code commit | `d2a610b` |

## What shipped (R8)

1. **`watch.py`** — poll Claude sessions; `.devmemory/watch.json` fingerprints
2. **`devmemory watch`** — `--once` / `--interval` / `--apply` / `--offline` / `--require-edits` / `--json`
3. Tool-edit gate only on per-session project JSONL (not shared history.jsonl)
4. `mark_seen` after extract or error (no poison loops); max 3 extracts/cycle

## Live proof

```text
devmemory watch --once --json --offline
# → polls=1, discovered/extracted depend on local Claude sessions

devmemory extract --text-file r8-watch.txt --session r8-watch-ship \
  --apply --force --showcase --model anthropic/claude-opus-5
# → hermes_rc=0 units=5
```

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | package knowledge |
| Kind split | 5 | Arch / Design / Patterns / Pitfalls + commands |
| Dedupe | 5 | net-new R8 only |
| Privacy | 5 | no secrets |
| Actionability | 5 | watch --once / interval / pytest path |

**Composite: 5.0 / 5**

## Milestone

**R1–R8 complete** (discovery → dry-run → hook → preview → doctor → anti-restate → validate → tool-edit gate → watch). Remaining ideas are P2+ polish.
