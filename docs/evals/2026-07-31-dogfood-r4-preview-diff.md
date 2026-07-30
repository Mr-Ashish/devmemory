# Eval · R4 unified knowledge preview diff · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T025840-bf64f4` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 4 |
| changes applied | 1 |
| preview stats | 1 file · +3/−0 |
| total_s | ~32.5 |
| showcase | `docs/showcase/dogfood-run-20260731T025840-bf64f4/` (includes `preview.diff`) |
| tests | **51 passed** (7 new in `test_preview_diff.py`) |
| code commit | `b9c4276` (+ trace showcase pack for preview artifacts) |

## What shipped (R4)

1. **`plan_preview` / `FileDiff` / `PreviewPlan`** — sequential in-memory multi-unit merge
2. **Git-style unified diff** — `diff --git`, `a/`/`b/` labels, `new file mode` for creates
3. **Artifacts** — `preview.diff` + `preview.json` on every extract (dry-run and apply)
4. **CLI** — colorized unified knowledge diff + `preview` block in machine JSON
5. **`plan_result`** — now sequential (matches what `--apply` writes)
6. **Showcase** — packages `preview.diff` / `preview.json` / `plan.json` / `timings.json`

## Live proof

```text
# offline dry-run → colorized diff + stats
devmemory extract --fixture dogfood-build-narrative --offline --force
# → preview 2 file(s) +11/-1 → …/preview.diff

# live apply + showcase
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase \
  --model anthropic/claude-opus-5
# → hermes_rc=0 units=4 applied 1 · preview 1 file +3/-0
```

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | `src/devmemory/DEV.md` only |
| Kind split | 5 | Patterns/Pitfalls/Debugging units |
| Dedupe | 4 | slight restate of frozen pydantic schemas (R6) |
| Privacy | 5 | showcase secret-scan clean |
| Actionability | 5 | unified diff is the human gate before `--apply` |

**Composite: 4.8 / 5**

## R4 status

**DONE** — tests + offline dry-run preview + live Opus hermes_rc=0 + showcase with `preview.diff`.
