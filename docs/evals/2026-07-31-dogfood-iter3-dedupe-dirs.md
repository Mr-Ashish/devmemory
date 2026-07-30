# Eval · dogfood iter3 · near-dupe + allowed dirs · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T022731-f1515c` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 5 |
| total_s | ~47.3 |
| showcase | `docs/showcase/dogfood-run-20260731T022731-f1515c/` |
| blocked paths in units/apply | **none** |

## Fixes this iteration

1. Jaccard + light stemming near-dupe for paraphrase thrash
2. `scrub_file_near_dupes` on apply path
3. Assemble: filter EXISTING_DIRS with knowledge blocklist; compact existing knowledge (H2 + ≤5 bullets)

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | only `src/devmemory` and `.` |
| Kind split | 5 | design/arch/pitfalls + troubleshooting |
| Dedupe | 5 | paraphrase pitfalls collapsed; re-run applied only new claims |
| Privacy | 5 | secret scan clean |
| Actionability | 5 | env knobs + troubleshooting |

**Composite: 5.0 / 5**
