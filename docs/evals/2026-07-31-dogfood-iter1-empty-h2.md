# Eval · dogfood iter1 · empty H2 scrub · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T022302-8668c5` |
| model | `anthropic/claude-opus-5` |
| fix | `scrub_empty_h2_sections` + lean templates |
| hermes_rc | 0 |
| units | 6 |
| total_s | ~39.5 |
| showcase | `docs/showcase/dogfood-run-20260731T022302-8668c5/` |

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 3 | Iter1 still wrote DEV.md under tests/docs (fixed in iter2 blocklist) |
| Kind split | 5 | clean sections |
| Dedupe | 5 | no thrash |
| Privacy | 5 | secret scan clean |
| Actionability | 5 | troubleshooting + package docs |

**Composite: 4.6 / 5** (path issue closed in same loop via blocklist)
