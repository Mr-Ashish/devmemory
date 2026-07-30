# Eval · R3 Claude Code SessionEnd hook · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T025126-b52ea6` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 4 |
| changes applied | 2 |
| total_s | ~31.8 |
| showcase | `docs/showcase/dogfood-run-20260731T025126-b52ea6/` |
| tests | **44 passed** (9 new in `test_claude_hook.py`) |
| code commit | `ee8074e` |

## What shipped (R3)

1. **`scripts/claude-code-hook.sh`** — Claude Code stdin JSON → SessionEnd extract (Stop opt-in)
2. **Always exit 0** — never blocks Claude; `stop_hook_active` short-circuits
3. **Background default** — SessionEnd budget is short; Hermes must not block
4. **Dry-run default** — `DEVMEMORY_HOOK_APPLY=1` to write; offline fallback without key
5. **Debounce 120s** per session under `.devmemory/hook-stamps/`
6. **`scripts/install-claude-hook.sh`** — one-liner merge into `.claude/settings.json` (`--user`, `--with-stop`, `--print`)
7. Docs in README + USAGE

## Live proof

```text
# hook unit surface
pytest -q tests/test_claude_hook.py   # 9 passed

# install fragment (no machine-absolute settings committed)
./scripts/install-claude-hook.sh --print

# live dogfood (same pipeline hook will call)
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase \
  --model anthropic/claude-opus-5
# → hermes_rc=0 units=4 applied 2 knowledge path(s)
```

Real `~/.claude` for this cwd still has **0** Claude sessions; fixtures remain the live dogfood surface. Hook is proven via scripted SessionEnd payloads in tests.

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | `src/devmemory/DEV.md`, root `DEV.md` |
| Kind split | 5 | Pitfalls + Patterns |
| Dedupe | 4 | dogfood-loop restates slightly; R6 still open |
| Privacy | 5 | showcase secret-scan clean; hook logs gitignored |
| Actionability | 5 | one-liner install; SessionEnd > Stop design clear |

**Composite: 4.8 / 5**

## R3 status

**DONE** — tests + install print + live Opus apply hermes_rc=0 + showcase.
