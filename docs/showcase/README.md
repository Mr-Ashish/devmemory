# Showcases

Curated, **redacted** live runs of devmemory dogfooding itself.

| Run | Model | Notes |
|-----|-------|-------|
| [dogfood-run-20260731T021737-6f9c71](./dogfood-run-20260731T021737-6f9c71/) | `anthropic/claude-opus-5` | Build narrative → `src/devmemory` DEV/USAGE · ~35s · 6 units |

## Generate a new showcase

```bash
export DEVMEMORY_MODEL=anthropic/claude-opus-5
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase
```

Never put secrets in this tree; packaging always goes through `trace.py` redaction.
