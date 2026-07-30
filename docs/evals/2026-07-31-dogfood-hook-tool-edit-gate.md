# Eval · Hook tool-edit gate · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T033504-281af8` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 4 |
| changes | 4 → `src/devmemory/{DEV,USAGE}.md` |
| preview | +14 / −0 |
| total_s | ~27 |
| showcase | `docs/showcase/dogfood-run-20260731T033504-281af8/` |
| tests | **87 passed** (`test_hook_gate.py` + existing hooks) |
| code commit | `48a957f` |

## What shipped

1. **`hook_gate.py`** — `should_run_extract_for_session` / transcript Write·Edit detection
2. **`claude-code-hook.sh`** — default `DEVMEMORY_HOOK_REQUIRE_EDITS=1`; skip chat-only; FORCE bypass
3. Fail-open: missing transcript / import errors still allow extract; hook exit 0 always
4. Docs: USAGE + README env table

## Live proof

```text
# chat-only transcript → skip (unit-tested)
# write tool in transcript → run (unit-tested)

devmemory extract --text-file r75-hook-gate.txt --session r75-hook-tool-edit-gate \
  --apply --force --showcase --model anthropic/claude-opus-5
# → hermes_rc=0 units=4
```

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | package knowledge only |
| Kind split | 5 | Arch / Patterns / Pitfalls + Debugging |
| Dedupe | 5 | net-new gate details only |
| Privacy | 5 | showcase clean |
| Actionability | 5 | hooks.log markers + FORCE + pytest path |

**Composite: 5.0 / 5**

## Next

R8 `watch` (mtime poll) remains optional until real Claude sessions land on this repo. Remaining backlog is mostly P2.
