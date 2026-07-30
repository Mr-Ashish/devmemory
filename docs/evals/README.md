# Evals

Lightweight evaluation of extraction quality. Goal: measurable dogfood, not vanity metrics.

## Automated (CI-local)

```bash
pytest -q
```

| Suite | Guards |
|-------|--------|
| `test_redaction` | secrets never survive |
| `test_normalize` | JSON contract + post-parse redaction |
| `test_apply` | dedupe, placeholders, path snap, section canonicalize |
| `test_paths_and_sections` | existing-dir resolution |
| `test_fixtures_and_offline` | offline path produces units + applies cleanly |

## Live gates

```bash
./scripts/smoke-hermes.sh          # Hermes + OpenRouter pong
./scripts/smoke-e2e.sh             # offline + live fixture extract
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase \
  --model anthropic/claude-opus-5
```

### Live rubric (human / dogfood)

Score each run 1–5:

1. **Path accuracy** — units land under real modules (`src/auth`, `src/devmemory`)
2. **Kind split** — design vs commands not mixed into one section
3. **Dedupe** — re-run does not thrash docs
4. **Privacy** — no secrets in showcase or knowledge files
5. **Actionability** — USAGE commands are copy-pasteable

Record scores in the showcase `README.md` or a dated note under this folder.

## Model policy

| Use case | Model (OpenRouter) |
|----------|--------------------|
| Dogfood / showcase | `anthropic/claude-opus-5` |
| Fast iteration | `openai/gpt-4.1-mini` |
| Offline CI | `offline` heuristic (no API) |
