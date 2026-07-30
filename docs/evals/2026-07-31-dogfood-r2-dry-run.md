# Eval · R2 dry-run UX · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T024229-b45cff` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 5 |
| changes applied | 4 |
| total_s | ~31.1 |
| showcase | `docs/showcase/dogfood-run-20260731T024229-b45cff/` |
| tests | **35 passed** (5 new in `test_dry_run.py`) |
| code commit | `3bb528d` |

## What shipped (R2)

1. **Default dry-run** — `devmemory extract` without `--apply` plans proposed knowledge paths only
2. **`plan_result` / `plan_unit`** — compute target `DEV.md`/`USAGE.md` without creating files
3. **CLI UX** — prints `mode=dry-run|apply`, lists proposed paths + sections + `unit_path`, machine JSON includes `apply` + `proposed[]`
4. **Artifacts** — dry-run writes `plan.json`; apply writes `apply.json`
5. **Cursor** — session marked processed **only** after successful `--apply` with units>0 (dry-run re-runnable)
6. **Default session** — still latest unprocessed real Claude session (R1), fixtures as fallback

## Live proof

```text
# offline dry-run
devmemory extract --fixture dogfood-build-narrative --offline --force
# → mode=dry-run, proposed 2 knowledge path(s), no DEV.md/USAGE.md writes

# live apply + showcase
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase \
  --model anthropic/claude-opus-5
# → hermes_rc=0 units=5 applied 4 knowledge path(s)
```

Real `~/.claude` for this cwd still has **0** Claude sessions; fixtures remain the live dogfood surface.

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | `src/devmemory/DEV.md`, root `DEV.md`, `USAGE.md` |
| Kind split | 5 | Patterns/Pitfalls vs Common commands |
| Dedupe | 4 | small restates of frozen-pydantic + redact-after-parse (R6 territory) |
| Privacy | 5 | showcase secret-scan clean |
| Actionability | 5 | dry-run → review proposed paths → `--apply` is clear |

**Composite: 4.8 / 5**

## R2 status

**DONE** — tests + offline dry-run proof + live Opus apply hermes_rc=0 + showcase.
