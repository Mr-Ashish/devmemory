# Repository context

- **root:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **assembled_at:** 2026-07-30T21:21:26Z

## git status

```
(clean)
```

## recent log

```
ee8074e R3: Claude Code SessionEnd hook + install one-liner
2ca7371 Dogfood R2: live Opus showcase, dry-run eval, knowledge apply
3bb528d R2: dry-run units+proposed paths; --apply writes + marks processed
842748c R1: Claude session discovery for cwd (history + project JSONL)
3e0ebb3 Dogfood iter3: paraphrase near-dupe and assemble allowed-dir filter
```

## tree (sample)

```
DEV.md
PLAN.md
README.md
USAGE.md
pyproject.toml
tests/test_apply.py
tests/test_claude_discovery.py
tests/test_claude_hook.py
tests/test_dry_run.py
tests/test_fixtures_and_offline.py
tests/test_normalize.py
tests/test_paths_and_sections.py
tests/test_redaction.py
agent/MEMORY.seed.md
agent/SOUL.md
agent/config.yaml
agent/extract-prompt.md
docs/ARCHITECTURE.md
docs/BUILD-LOG.md
docs/evals/2026-07-31-dogfood-iter1-empty-h2.md
docs/evals/2026-07-31-dogfood-iter3-dedupe-dirs.md
docs/evals/2026-07-31-dogfood-opus5.md
docs/evals/2026-07-31-dogfood-r1-claude-discovery.md
docs/evals/2026-07-31-dogfood-r2-dry-run.md
docs/evals/README.md
docs/experiments/README.md
docs/showcase/README.md
docs/showcase/dogfood-run-20260731T021737-6f9c71/README.md
docs/showcase/dogfood-run-20260731T021737-6f9c71/apply.json
docs/showcase/dogfood-run-20260731T021737-6f9c71/extract.raw.md
docs/showcase/dogfood-run-20260731T021737-6f9c71/hermes-usage.json
docs/showcase/dogfood-run-20260731T021737-6f9c71/meta.env
docs/showcase/dogfood-run-20260731T021737-6f9c71/prompt.md
docs/showcase/dogfood-run-20260731T021737-6f9c71/repo-context.md
docs/showcase/dogfood-run-20260731T021737-6f9c71/session.md
docs/showcase/dogfood-run-20260731T021737-6f9c71/summary.md
docs/showcase/dogfood-run-20260731T021737-6f9c71/timings.json
docs/showcase/dogfood-run-20260731T021737-6f9c71/units.json
docs/showcase/dogfood-run-20260731T023342-e5e026/README.md
docs/showcase/dogfood-run-20260731T023342-e5e026/apply.json
docs/showcase/dogfood-run-20260731T023342-e5e026/extract.raw.md
docs/showcase/dogfood-run-20260731T023342-e5e026/hermes-usage.json
docs/showcase/dogfood-run-20260731T023342-e5e026/meta.env
docs/showcase/dogfood-run-20260731T023342-e5e026/prompt.md
docs/showcase/dogfood-run-20260731T023342-e5e026/repo-context.md
docs/showcase/dogfood-run-20260731T023342-e5e026/session.md
docs/showcase/dogfood-run-20260731T023342-e5e026/summary.md
docs/showcase/dogfood-run-20260731T023342-e5e026/units.json
docs/showcase/dogfood-run-20260731T024229-b45cff/README.md
docs/showcase/dogfood-run-20260731T024229-b45cff/apply.json
docs/showcase/dogfood-run-20260731T024229-b45cff/extract.raw.md
docs/showcase/dogfood-run-20260731T024229-b45cff/hermes-usage.json
docs/showcase/dogfood-run-20260731T024229-b45cff/meta.env
docs/showcase/dogfood-run-20260731T024229-b45cff/prompt.md
docs/showcase/dogfood-run-20260731T024229-b45cff/repo-context.md
docs/showcase/dogfood-run-20260731T024229-b45cff/session.md
docs/showcase/dogfood-run-20260731T024229-b45cff/summary.md
docs/showcase/dogfood-run-20260731T024229-b45cff/units.json
docs/showcase/dogfood-run-20260731T022731-f1515c/README.md
docs/showcase/dogfood-run-20260731T022731-f1515c/apply.json
docs/showcase/dogfood-run-20260731T022731-f1515c/extract.raw.md
docs/showcase/dogfood-run-20260731T022731-f1515c/hermes-usage.json
docs/showcase/dogfood-run-20260731T022731-f1515c/meta.env
docs/showcase/dogfood-run-20260731T022731-f1515c/prompt.md
docs/showcase/dogfood-run-20260731T022731-f1515c/repo-context.md
docs/showcase/dogfood-run-20260731T022731-f1515c/session.md
docs/showcase/dogfood-run-20260731T022731-f1515c/summary.md
docs/showcase/dogfood-run-20260731T022731-f1515c/timings.json
docs/showcase/dogfood-run-20260731T022731-f1515c/units.json
docs/showcase/dogfood-run-20260731T022302-8668c5/README.md
docs/showcase/dogfood-run-20260731T022302-8668c5/apply.json
docs/showcase/dogfood-run-20260731T022302-8668c5/extract.raw.md
docs/showcase/dogfood-run-20260731T022302-8668c5/hermes-usage.json
docs/showcase/dogfood-run-20260731T022302-8668c5/meta.env
docs/showcase/dogfood-run-20260731T022302-8668c5/prompt.md
docs/showcase/dogfood-run-20260731T022302-8668c5/repo-context.md
docs/showcase/dogfood-run-20260731T022302-8668c5/session.md
docs/showcase/dogfood-run-20260731T022302-8668c5/summary.md
docs/showcase/dogfood-run-20260731T022302-8668c5/timings.json
docs/showcase/dogfood-run-20260731T022302-8668c5/units.json
scripts/claude-code-hook.sh
scripts/ensure-hermes.sh
scripts/install-claude-hook.sh
scripts/load-env.sh
scripts/smoke-e2e.sh
scripts/smoke-hermes.sh
fixtures/sessions/dogfood-build-narrative.json
fixtures/sessions/sample-auth-module.json
fixtures/sessions/sample-cli-pipeline.json
assets/devmemory-core.html
src/auth/DEV.md
src/auth/USAGE.md
src/devmemory/DEV.md
src/devmemory/USAGE.md
src/devmemory/__init__.py
src/devmemory/apply.py
src/devmemory/assemble.py
src/devmemory/cli.py
src/devmemory/extract.py
src/devmemory/normalize.py
src/devmemory/paths.py
src/devmemory/redaction.py
src/devmemory/schema.py
src/devmemory/sections.py
src/devmemory/state.py
src/devmemory/trace.py
src/devmemory/sources/DEV.md
src/devmemory/sources/__init__.py
src/devmemory/sources/base.py
src/devmemory/sources/claude.py
src/devmemory/sources/fixtures.py
```

## git diff

```
(no unstaged/uncommitted diff)
```

## existing knowledge files

### DEV.md

## Pitfalls
- Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
- Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.## Patterns
- Eval notes live under docs/evals but knowledge should root

## Design decisions
- The product was built and validated entirely inside this repository (self-dogfooding); there is no external monorepo dependency.
- Hermes Agent is consumed as an installed CLI (`hermes -z`) with OpenRouter inference — `anthropic/claude-opus-5` is the model pinned for dogfood-quality runs, `gpt-4.1-mini` for cheap iteration.
- `hermes-agent-self-evolution` is treated as an idea source only (session importers, secret-redaction patterns, later skill GEPA); it is not part of the MVP runtime.
- The apply layer — not the prompt — is the quality boundary: path snapping to existing dirs, canonical H2 titles, bullet near-dupe skipping and placeholder scrubbing. The LLM proposes; merge decides.
- Hermes runs extract with empty toolsets (pure reasoning over assembled context); `DEVMEMORY_TOOLSETS=terminal` is an explicit opt-in override.

### src/auth/DEV.md

## Design decisions
- Authentication middleware is located in `src/auth/`.
- Token verification is separated from user lookup.
- Tokens are currently signed with HS256; plan to migrate to RS256 later.## Patterns
- Use a `require_auth` decorator on all protected routes.
- The decorator reads the `Authorization: Bearer` header to obtain the token.## Pitfalls

### src/devmemory/DEV.md

## Architecture
- Module layout: `cli.py` (Click CLI), `assemble.py` (bounded context, no LLM), `extract.py` (Hermes orchestration + timings + showcase flag), `normalize.py` (JSON units + post-parse redaction), `apply.py` (merge into DEV.md/USAGE.md), `paths.py` (`list_repo_dirs` + `resolve_unit_path`), `sections.py` (canonicalize section titles), `trace.py` (redacted showcase packaging), `sources/` (fixtures + Claude history/project).
- `agent/` holds SOUL.md, config.yaml and extract-prompt.md used to seed the Hermes home before a live run.
- Runtime state is written under `.devmemory/` (gitignored); curated, redacted public traces are written under `docs/showcase/`.
- Control plane mirrors the Luffy PR-review agent shape: assemble → `hermes -z` → normalize → apply → human git review.
- `extract_session` records per-stage timings (assemble/extract/normalize/apply/total) into `timings.json` in the run dir and surfaces them on `ExtractOutcome`.## Design decisions

## Design decisions
- Bullet dedupe in `apply.py` is paraphrase-aware, not just exact: `_near_duplicate` accepts a match on substring containment (both bullets >24 chars), Jaccard ≥ 0.52, or coverage of the smaller token set ≥ 0.62.
- `_norm_bullet` strips quotes, underscores and punctuation (`_'".,;:()[]{}`) in addition to backticks/asterisks so restated bullets normalize to the same string.
- `_token_set` applies a longest-suffix-first `_stem` (ations/ation/tions/ing/ers/ies/ed/es/s) and drops tokens ≤2 chars; the stem guard requires `len(t) > len(suf) + 3` to avoid over-stemming words like "existing".
- `dedupe_
… [truncated; do not restate] …

### src/devmemory/sources/DEV.md

## Architecture
- Two Claude importers feed one discovery API: `ClaudeHistorySource` reads the flat `~/.claude/history.jsonl` prompt log, `ClaudeProjectSource` reads full transcripts from `~/.claude/projects/<encoded-path>/*.jsonl`.
- `ClaudeHistorySource.list_sessions` buckets history lines by `sessionId` and joins their texts chronologically, so a multi-turn history log yields one `SessionRecord` per session instead of one per prompt.
- `discover_claude_sessions` merges both sources newest-first and prefers the project record when the same session id appears in both (project JSONL carries richer multi-role transcripts).
- Records carry `meta["turns"]` (and `meta["project_dir"]` for project sessions) so callers/CLI can show session size without re-reading the files.
- `pick_latest_unprocessed(sessions, is_processed=...)` is the selection primitive: it scans the newest-first list and returns the first session not in the cursor.

## Design decisions
- Discovery scopes to the repo by *project path*, not by name: `project_matches_repo` accepts the repo's resolved absolute path and any path under it, so sessions started in a subdirectory of the repo still count.
- The earlier soft "repo name appears in project string" fallback was removed from history filtering because it pulled in unrelated repos; `repo_root=` filtering replaces `project_filter=` for that call path.
- History/project roots are overridable via `DEVMEMORY_CLAUDE_HISTORY` and `DEVMEMORY_CLAUDE_PROJECTS` specifically so tests can point at fixtures instead of the real `~/.claude`.
- `encode_project_path` (public; `
… [truncated; do not restate] …

### USAGE.md

## Setup
- Create and activate Python virtual environment: `python3 -m venv .venv && source .venv/bin/activate`.
- `pip install -e '.[dev]'`.
- Set `OPENROUTER_API_KEY` (or `DEVMEMORY_ENV_FILE`) for live extraction.
- Run `./scripts/ensure-hermes.sh` once to install Hermes CLI.

## Common commands
- Dry-run extract (units + proposed paths): `devmemory extract --fixture sample-auth-module`
- Write knowledge: `devmemory extract --fixture sample-auth-module --apply`
- Real Claude session: `devmemory extract --session <id> --apply` (default without flags prefers latest unprocessed Claude session for cwd)
- Offline heuristic: `devmemory extract --offline --apply --force`
- List sessions: `devmemory list-sessions`

## Claude Code hook (SessionEnd)
- Default: **background dry-run** of the ending session (or latest unprocessed); log at `.devmemory/hooks.log`.
- Auto-write: `export DEVMEMORY_HOOK_APPLY=1` before Claude Code.
- Prefer **SessionEnd** over **Stop** (Stop fires every turn; thrashy). Opt-in: `./scripts/install-claude-hook.sh --with-stop`.
- Print fragment only: `./scripts/install-claude-hook.sh --print`.
- Hook never blocks Claude (always exit 0); never commits `.env` / `.devmemory/`.

## Troubleshooting
- Hollow `## Architecture` / `## Troubleshooting` headings mean the file predates the empty-section scrub; re-run apply to scrub them.
- After a dogfood run: `devmemory review` then `git diff` as the human gate.
- Hook silent? Check `.devmemory/hooks.log`; ensure `devmemory` is on PATH or `.venv/bin/devmemory` exists; set `DEVMEMORY_HOOK_VERBOSE=1` for stderr.
- Hook ski
… [truncated; do not restate] …

### src/auth/USAGE.md

## Setup
- For local development, set environment variable `AUTH_SECRET=dev-only` before running the server with uvicorn.## Common commands
- Run tests with `pytest tests/auth -q`.
- Start the development server with `uvicorn app.main:app --reload --port 8000`.## Debugging
- If receiving a 401 on a valid token, check for clock skew and verify that the `AUTH_SECRET` matches the issuer.

### src/devmemory/USAGE.md

## Common commands
- Live dogfood extract with showcase: `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase` (add `--showcase-dir <path>` for a custom output dir).
- `--force` re-processes a session that is already recorded in the cursor.
- Point env loading at an external file and pin the model before a live run: `export DEVMEMORY_ENV_FILE=<path to .env>` and `export DEVMEMORY_MODEL=anthropic/claude-opus-5`.
- End-to-end smoke: `./scripts/smoke-e2e.sh`; Hermes-only connectivity check: `./scripts/smoke-hermes.sh`.
- `devmemory review` shows the pending doc changes for human git review.

## Troubleshooting
- Context size is tunable via env: `DEVMEMORY_MAX_SESSION_CHARS` (24000), `DEVMEMORY_MAX_DIFF_CHARS` (40000), `DEVMEMORY_MAX_TREE_LINES` (200), `DEVMEMORY_MAX_KNOWLEDGE_CHARS` (1600). Raise these only when the model is clearly missing evidence — larger prompts increase restatement.
- Unit landed under the wrong directory: confirm the target appears in the `EXISTING_DIRS` block of the assembled prompt and that the module dir shows up in the tree sample; blocked trees are filtered out on purpose and will never be accepted.
- Docs growing on every run: verify near-dupe skipping is active (`apply.dedupe_section_bullets` / `scrub_file_near_dupes`) rather than editing the docs by hand.
- Before publishing a run, remember `trace.py` redacts `sk-or` / `Bearer` tokens and env assignments on the way into `docs/showcase/` — never copy files there manually.

## Debugging
- Non-zero `hermes_rc`: read `extract.raw.stderr` in the run dir, then confirm `HERMES
… [truncated; do not restate] …

