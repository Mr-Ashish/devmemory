# Showcases

Curated, **redacted** live runs of devmemory dogfooding itself.

| Run | Model | Notes |
|-----|-------|-------|
| [dogfood-run-20260731T022302-8668c5](./dogfood-run-20260731T022302-8668c5/) | Opus 5 | Iter1 empty-H2 + build narrative · ~40s · 6 units |
| [dogfood-run-20260731T021737-6f9c71](./dogfood-run-20260731T021737-6f9c71/) | Opus 5 | First package DEV/USAGE dogfood · ~35s · 6 units |

## Generate a new showcase

```bash
export DEVMEMORY_MODEL=anthropic/claude-opus-5
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase
```
