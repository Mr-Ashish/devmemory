# Showcases

Curated, **redacted** live runs of devmemory dogfooding itself.

| Run | Model | Notes |
|-----|-------|-------|
| [dogfood-run-20260731T033504-281af8](./dogfood-run-20260731T033504-281af8/) | Opus 5 | **hook tool-edit gate** · ~27s · 4 units · +14/−0 · hermes_rc=0 |
| [dogfood-run-20260731T032614-a2aa70](./dogfood-run-20260731T032614-a2aa70/) | Opus 5 | **R7** validate ship · ~23s · 4 units · +12/−0 · hermes_rc=0 |
| [dogfood-run-20260731T032535-73934d](./dogfood-run-20260731T032535-73934d/) | Opus 5 | dogfood narrative re-run after R7 · 1 unit · hermes_rc=0 |
| [dogfood-run-20260731T031810-c66390](./dogfood-run-20260731T031810-c66390/) | Opus 5 | **R6** anti-restate · ~19s · 2 units · +4/−0 · hermes_rc=0 |
| [dogfood-run-20260731T030327-011c11](./dogfood-run-20260731T030327-011c11/) | Opus 5 | **R5** doctor ship · ~27s · 4 units · hermes_rc=0 |
| [dogfood-run-20260731T025840-bf64f4](./dogfood-run-20260731T025840-bf64f4/) | Opus 5 | **R4** unified preview.diff · ~32s · 4 units · +3/−0 |
| [dogfood-run-20260731T025126-b52ea6](./dogfood-run-20260731T025126-b52ea6/) | Opus 5 | **R3** SessionEnd hook ship · ~32s · 4 units · hermes_rc=0 |
| [dogfood-run-20260731T024229-b45cff](./dogfood-run-20260731T024229-b45cff/) | Opus 5 | **R2** dry-run UX · ~31s · 5 units |
| [dogfood-run-20260731T023342-e5e026](./dogfood-run-20260731T023342-e5e026/) | Opus 5 | **R1** Claude discovery · ~47s · 6 units · `sources/DEV.md` |
| [dogfood-run-20260731T022731-f1515c](./dogfood-run-20260731T022731-f1515c/) | Opus 5 | Iter3 near-dupe + allowed dirs · ~47s · 5 units · no blocked paths |
| [dogfood-run-20260731T022302-8668c5](./dogfood-run-20260731T022302-8668c5/) | Opus 5 | Iter1 empty-H2 scrub · ~40s · 6 units |
| [dogfood-run-20260731T021737-6f9c71](./dogfood-run-20260731T021737-6f9c71/) | Opus 5 | First package dogfood · ~35s · 6 units |

```bash
export DEVMEMORY_MODEL=anthropic/claude-opus-5
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase
```
