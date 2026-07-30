# Eval · R1 Claude session discovery · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T023342-e5e026` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 6 |
| total_s | ~46.9 |
| showcase | `docs/showcase/dogfood-run-20260731T023342-e5e026/` |
| tests | **30 passed** (8 new in `test_claude_discovery.py`) |

## What shipped (R1)

1. **History grouping** — multi-turn `history.jsonl` lines → one `SessionRecord` per `sessionId`
2. **Project JSONL** — `~/.claude/projects/<encoded-path>/*.jsonl` discovery for cwd
3. **cwd filter** — `project_matches_repo` (exact path + subdirs only; no soft name match)
4. **epoch-ms timestamps** — `_ts_sort_key` normalizes ms → seconds for newest-first
5. **Default pick** — extract prefers latest unprocessed Claude session over fixtures
6. **list-sessions** — Claude first; shows `turns` + `unprocessed_claude=N`
7. **Env overrides** — `DEVMEMORY_CLAUDE_HISTORY` / `DEVMEMORY_CLAUDE_PROJECTS` for tests/dogfood

## Live proof

```text
DEVMEMORY_CLAUDE_HISTORY=/tmp/.../history.jsonl \
DEVMEMORY_CLAUDE_PROJECTS=/tmp/.../projects \
devmemory list-sessions --no-fixtures
# → claude=2 unprocessed_claude=2 (history multi-turn + project JSONL)
# default _resolve_session → r1-dogfood-live-sess (claude-history)
```

Real `~/.claude` for this cwd currently has **0** Claude sessions (never opened Claude Code here); fixtures still list correctly as fallback.

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | units → `src/devmemory/sources` + `src/devmemory` |
| Kind split | 5 | architecture / decisions / pitfalls / patterns / debugging |
| Dedupe | 5 | merge into new `sources/DEV.md` without thrash |
| Privacy | 5 | showcase secret-scan clean; import-time redaction tested |
| Actionability | 5 | env overrides + hermes_rc/empty-units debugging steps |

**Composite: 5.0 / 5**

## R1 status

**DONE** — tests + live discovery proof + dogfood extract hermes_rc=0 + knowledge under `src/devmemory/sources/DEV.md`.
