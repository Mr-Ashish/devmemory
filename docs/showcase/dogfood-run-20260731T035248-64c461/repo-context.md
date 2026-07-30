# Repository context

- **root:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **assembled_at:** 2026-07-30T22:22:48Z

## git status

```
M docs/experiments/README.md
```

## recent log

```
928881c Stability fire 2/3: no P0/P1; Opus units=0 anti-restate hold
3204347 Stability fire 1/3: no P0/P1; dogfood anti-restate holds at 0 writes
ef2ad0f Dogfood R8: Opus watch ship, eval 5.0, showcase, knowledge
d2a610b R8: devmemory watch polls Claude sessions for new extracts
4e3f723 Dogfood hook tool-edit gate: Opus showcase, eval 5.0, knowledge
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
tests/test_doctor.py
tests/test_dry_run.py
tests/test_fixtures_and_offline.py
tests/test_hook_gate.py
tests/test_normalize.py
tests/test_paths_and_sections.py
tests/test_preview_diff.py
tests/test_redaction.py
tests/test_validate.py
tests/test_watch.py
agent/MEMORY.seed.md
agent/SOUL.md
agent/config.yaml
agent/extract-prompt.md
docs/ARCHITECTURE.md
docs/BUILD-LOG.md
docs/evals/2026-07-31-dogfood-hook-tool-edit-gate.md
docs/evals/2026-07-31-dogfood-iter1-empty-h2.md
docs/evals/2026-07-31-dogfood-iter3-dedupe-dirs.md
docs/evals/2026-07-31-dogfood-opus5.md
docs/evals/2026-07-31-dogfood-r1-claude-discovery.md
docs/evals/2026-07-31-dogfood-r2-dry-run.md
docs/evals/2026-07-31-dogfood-r3-claude-hook.md
docs/evals/2026-07-31-dogfood-r4-preview-diff.md
docs/evals/2026-07-31-dogfood-r5-doctor.md
docs/evals/2026-07-31-dogfood-r6-anti-restate.md
docs/evals/2026-07-31-dogfood-r7-validate.md
docs/evals/2026-07-31-dogfood-r8-watch.md
docs/evals/2026-07-31-dogfood-stability-1.md
docs/evals/2026-07-31-dogfood-stability-2.md
docs/evals/README.md
docs/experiments/README.md
docs/showcase/README.md
docs/showcase/dogfood-run-20260731T033504-281af8/README.md
docs/showcase/dogfood-run-20260731T033504-281af8/apply.json
docs/showcase/dogfood-run-20260731T033504-281af8/extract.raw.md
docs/showcase/dogfood-run-20260731T033504-281af8/hermes-usage.json
docs/showcase/dogfood-run-20260731T033504-281af8/meta.env
docs/showcase/dogfood-run-20260731T033504-281af8/preview.diff
docs/showcase/dogfood-run-20260731T033504-281af8/preview.json
docs/showcase/dogfood-run-20260731T033504-281af8/prompt.md
docs/showcase/dogfood-run-20260731T033504-281af8/repo-context.md
docs/showcase/dogfood-run-20260731T033504-281af8/session.md
docs/showcase/dogfood-run-20260731T033504-281af8/summary.md
docs/showcase/dogfood-run-20260731T033504-281af8/timings.json
docs/showcase/dogfood-run-20260731T033504-281af8/units.json
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
docs/showcase/dogfood-run-20260731T031810-c66390/README.md
docs/showcase/dogfood-run-20260731T031810-c66390/apply.json
docs/showcase/dogfood-run-20260731T031810-c66390/extract.raw.md
docs/showcase/dogfood-run-20260731T031810-c66390/hermes-usage.json
docs/showcase/dogfood-run-20260731T031810-c66390/meta.env
docs/showcase/dogfood-run-20260731T031810-c66390/preview.diff
docs/showcase/dogfood-run-20260731T031810-c66390/preview.json
docs/showcase/dogfood-run-20260731T031810-c66390/prompt.md
docs/showcase/dogfood-run-20260731T031810-c66390/repo-context.md
docs/showcase/dogfood-run-20260731T031810-c66390/session.md
docs/showcase/dogfood-run-20260731T031810-c66390/summary.md
docs/showcase/dogfood-run-20260731T031810-c66390/timings.json
docs/showcase/dogfood-run-20260731T031810-c66390/units.json
docs/showcase/dogfood-run-20260731T025126-b52ea6/README.md
docs/showcase/dogfood-run-20260731T025126-b52ea6/apply.json
docs/showcase/dogfood-run-20260731T025126-b52ea6/extract.raw.md
docs/showcase/dogfood-run-20260731T025126-b52ea6/hermes-usage.json
docs/showcase/dogfood-run-20260731T025126-b52ea6/meta.env
docs/showcase/dogfood-run-20260731T025126-b52ea6/prompt.md
docs/showcase/dogfood-run-20260731T025126-b52ea6/repo-context.md
docs/showcase/dogfood-run-20260731T025126-b52ea6/session.md
docs/showcase/dogfood-run-20260731T025126-b52ea6/summary.md
docs/showcase/dogfood-run-20260731T025126-b52ea6/units.json
docs/showcase/dogfood-run-20260731T034257-9c4ca1/README.md
docs/showcase/dogfood-run-20260731T034257-9c4ca1/apply.json
docs/showcase/dogfood-run-20260731T034257-9c4ca1/extract.raw.md
docs/showcase/dogfood-run-20260731T034257-9c4ca1/hermes-usage.json
docs/showcase/dogfood-run-20260731T034257-9c4ca1/meta.env
docs/showcase/dogfood-run-20260731T034257-9c4ca1/preview.diff
docs/showcase/dogfood-run-20260731T034257-9c4ca1/preview.json
docs/showcase/dogfood-run-20260731T034257-9c4ca1/prompt.md
docs/showcase/dogfood-run-20260731T034257-9c4ca1/repo-context.md
docs/showcase/dogfood-run-20260731T034257-9c4ca1/session.md
docs/showcase/dogfood-run-20260731T034257-9c4ca1/summary.md
docs/showcase/dogfood-run-20260731T034257-9c4ca1/timings.json
docs/showcase/dogfood-run-20260731T034257-9c4ca1/units.json
docs/showcase/dogfood-run-20260731T025840-bf64f4/README.md
docs/showcase/dogfood-run-20260731T025840-bf64f4/apply.json
docs/showcase/dogfood-run-20260731T025840-bf64f4/extract.raw.md
docs/showcase/dogfood-run-20260731T025840-bf64f4/hermes-usage.json
docs/showcase/dogfood-run-20260731T025840-bf64f4/meta.env
docs/showcase/dogfood-run-20260731T025840-bf64f4/preview.diff
docs/showcase/dogfood-run-20260731T025840-bf64f4/preview.json
docs/showcase/dogfood-run-20260731T025840-bf64f4/prompt.md
docs/showcase/dogfood-run-20260731T025840-bf64f4/repo-context.md
docs/showcase/dogfood-run-20260731T025840-bf64f4/session.md
docs/showcase/dogfood-run-20260731T025840-bf64f4/summary.md
docs/showcase/dogfood-run-20260731T025840-bf64f4/timings.json
docs/showcase/dogfood-run-20260731T025840-bf64f4/units.json
docs/showcase/dogfood-run-20260731T032535-73934d/README.md
docs/showcase/dogfood-run-20260731T032535-73934d/apply.json
docs/showcase/dogfood-run-20260731T032535-73934d/extract.raw.md
docs/showcase/dogfood-run-20260731T032535-73934d/hermes-usage.json
docs/showcase/dogfood-run-20260731T032535-73934d/meta.env
docs/showcase/dogfood-run-20260731T032535-73934d/preview.diff
docs/showcase/dogfood-run-20260731T032535-73934d/preview.json
docs/showcase/dogfood-run-20260731T032535-73934d/prompt.md
docs/showcase/dogfood-run-20260731T032535-73934d/repo-context.md
docs/showcase/dogfood-run-20260731T032535-73934d/session.md
docs/showcase/dogfood-run-20260731T032535-73934d/summary.md
docs/showcase/dogfood-run-20260731T032535-73934d/timings.json
docs/showcase/dogfood-run-20260731T032535-73934d/units.json
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
docs/showcase/dogfood-run-20260731T032614-a2aa70/README.md
docs/showcase/dogfood-run-20260731T032614-a2aa70/apply.json
docs/showcase/dogfood-run-20260731T032614-a2aa70/extract.raw.md
docs/showcase/dogfood-run-20260731T032614-a2aa70/hermes-usage.json
docs/showcase/dogfood-run-20260731T032614-a2aa70/meta.env
docs/showcase/dogfood-run-20260731T032614-a2aa70/preview.diff
docs/showcase/dogfood-run-20260731T032614-a2aa70/preview.json
docs/showcase/dogfood-run-20260731T032614-a2aa70/prompt.md
docs/showcase/dogfood-run-20260731T032614-a2aa70/repo-context.md
docs/showcase/dogfood-run-20260731T032614-a2aa70/session.md
docs/showcase/dogfood-run-20260731T032614-a2aa70/summary.md
docs/showcase/dogfood-run-20260731T032614-a2aa70/timings.json
docs/showcase/dogfood-run-20260731T032614-a2aa70/units.json
docs/showcase/dogfood-run-20260731T030327-011c11/README.md
docs/showcase/dogfood-run-20260731T030327-011c11/apply.json
docs/showcase/dogfood-run-20260731T030327-011c11/extract.raw.md
docs/showcase/dogfood-run-20260731T030327-011c11/hermes-usage.json
docs/showcase/dogfood-run-20260731T030327-011c11/meta.env
docs/showcase/dogfood-run-20260731T030327-011c11/preview.diff
docs/showcase/dogfood-run-20260731T030327-011c11/preview.json
docs/showcase/dogfood-run-20260731T030327-011c11/prompt.md
docs/showcase/dogfood-run-20260731T030327-011c11/repo-context.md
docs/showcase/dogfood-run-20260731T030327-011c11/session.md
docs/showcase/dogfood-run-20260731T030327-011c11/summary.md
docs/showcase/dogfood-run-20260731T030327-011c11/timings.json
docs/showcase/dogfood-run-20260731T030327-011c11/units.json
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
docs/showcase/dogfood-run-20260731T033900-ad9f76/README.md
docs/showcase/dogfood-run-20260731T033900-ad9f76/apply.json
docs/showcase/dogfood-run-20260731T033900-ad9f76/extract.raw.md
docs/showcase/dogfood-run-20260731T033900-ad9f76/hermes-usage.json
docs/showcase/dogfood-run-20260731T033900-ad9f76/meta.env
docs/showcase/dogfood-run-20260731T033900-ad9f76/preview.diff
docs/showcase/dogfood-run-20260731T033900-ad9f76/preview.json
docs/showcase/dogfood-run-20260731T033900-ad9f76/prompt.md
docs/showcase/dogfood-run-20260731T033900-ad9f76/repo-context.md
docs/showcase/dogfood-run-20260731T033900-ad9f76/session.md
docs/showcase/dogfood-run-20260731T033900-ad9f76/summary.md
docs/showcase/dogfood-run-20260731T033900-ad9f76/timings.json
docs/showcase/dogfood-run-20260731T033900-ad9f76/units.json
docs/showcase/dogfood-run-20260731T022302-8668c5/README.md
docs/showcase/dogfood-run-20260731T022302-8668c5/apply.json
docs/showcase/dogfood-run-20260731T022302-8668c5/extract.raw.md
```

## git diff

```
diff --git a/docs/experiments/README.md b/docs/experiments/README.md
index 7563299..2049515 100644
--- a/docs/experiments/README.md
+++ b/docs/experiments/README.md
@@ -239,3 +239,18 @@ Running notes from dogfood experiments. Prefer short entries with command + outc
 ### Decision
 
 **No build.** Reconfirmed R1–R8 solid; doctor ready_live; validate ok (1 P2 warn). Health dogfood only. Consecutive no-P0/P1 fires: **2/3**.
+
+## 2026-07-31 · fire · stability (no P0/P1) · 3/3 · DONE
+
+**Persona jobs:** fully covered by R1–R8 + tool-edit gate.
+
+### ROI rank (this fire)
+
+| Rank | Idea | Priority |
+|------|------|----------|
+| — | *(none)* | **no P0/P1** |
+| 1–4 | P2 polish only (USAGE H2, embeddings, init-hook, GEPA) | skip |
+
+### Decision
+
+**No build.** Third consecutive no-P0/P1 fire with eval ≥4.5 and clean push → **scheduler DONE**.
```

## existing knowledge files

### claim index (do not restate these claims)
- [DEV.md#Pitfalls] artifact clutter commit control devmemory never privacy protect
- [DEV.md#Pitfalls] acces freshnes generat knowledge requir session validate
- [DEV.md#Pitfalls] avoid context knowledge large localiz maintainability monolithic preferable
- [DEV.md#Patterns] docseval knowledge
- [DEV.md#Design decisions] built dependency entirely external inside monorepo product repository
- [DEV.md#Design decisions] agent anthropicclaude-opus-5 cheap consum dogfood-quality gpt-41-mini inference install
- [DEV.md#Design decisions] hermes-agent-self-evolution import later pattern runtime secret-redaction session skill
- [DEV.md#Design decisions] apply boundary bullet canonical decid exist layer merge
- [DEV.md#Design decisions] assembl context devmemorytoolsets=terminal empty explicit extract opt-in override
- [DEV.md#Design decisions] apply-dedupe confidence devmd devusage dogfood extract fixture improve
- [src/auth/DEV.md#Design decisions] authentic locat middleware srcauth
- [src/auth/DEV.md#Design decisions] lookup separat token verific
- [src/auth/DEV.md#Design decisions] currently hs256 later migrate rs256 token
- [src/auth/DEV.md#Patterns] decorator protect requireauth
- [src/auth/DEV.md#Patterns] authoriz [REDACTED] header obtain token
- [src/auth/DEV.md#Pitfalls] authoriz avoid contain header secret
- [src/devmemory/DEV.md#Architecture] applypy assemblepy bound canonicalize claude click clipy context
- [src/devmemory/DEV.md#Architecture] agent configyaml extract-promptmd soulmd
- [src/devmemory/DEV.md#Architecture] curat devmemory docsshowcase gitignor public redact runtime state
- [src/devmemory/DEV.md#Architecture] agent apply assemble control human luffy mirror normalize
- [src/devmemory/DEV.md#Architecture] assembleextractnormalizeapplytotal extractoutcome extractsession per-stage record surfac timing timingsjson
- [src/devmemory/DEV.md#Architecture] asset block checker colocat devmdusagemd empty failur fixtur
- [src/devmemory/DEV.md#Architecture] --strict break devmemory error githubworkflowsciyml non---strict pytest scriptsvalidate-knowledgesh
- [src/devmemory/DEV.md#Architecture] decision extract hermescli hookgatepy proces runskip scriptsclaude-code-hooksh session
- [src/devmemory/DEV.md#Architecture] alway always-run behavior devmemoryhookforce=1 devmemoryhookrequireedits=0 entirely extract pre-gate
- [src/devmemory/DEV.md#Architectur
… [claim index truncated; do not restate] …

### knowledge excerpts
### DEV.md

## Pitfalls
- Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
- Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.

## Patterns
- Eval notes live under docs/evals but knowledge should root

## Design decisions
- The product was built and validated entirely inside this repository (self-dogfooding); there is no external monorepo dependency.
- Hermes Agent is consumed as an installed CLI (`hermes -z`) with OpenRouter inference — `anthropic/claude-opus-5` is the model pinned for dogfood-quality runs, `gpt-4.1-mini` for cheap iteration.
- `hermes-agent-self-evolution` is treated as an idea source only (session importers, secret-redaction patterns, later skill GEPA); it is not part of the MVP runtime.
- The apply layer — not the prompt — is the quality boundary: path snapping to existing dirs, canonical H2 titles, bullet near-dupe skipping and placeholder scrubbing. The LLM proposes; merge decides.

### src/auth/DEV.md

## Design decisions
- Authentication middleware is located in `src/auth/`.
- Token verification is separated from user lookup.
- Tokens are currently signed with HS256; plan to migrate to RS256 later.

## Patterns
- Use a `require_auth` decorator on all protected routes.
- The decorator reads the `Authorization: Bearer` header to obtain the token.

## Pitfalls
- Avoid logging the raw `Authorization` header as it contains secrets.

### src/devmemory/DEV.md

## Architecture
- Module layout: `cli.py` (Click CLI), `assemble.py` (bounded context, no LLM), `extract.py` (Hermes orchestration + timings + showcase flag), `normalize.py` (JSON units + post-parse redaction), `apply.py` (merge into DEV.md/USAGE.md), `paths.py` (`list_repo_dirs` + `resolve_unit_path`), `sections.py` (canonicalize section titles), `trace.py` (redacted showcase packaging), `sources/` (fixtures + Claude history/project).
- `agent/` holds SOUL.md, config.yaml and extract-prompt.md used to seed the Hermes home before a live run.
- Runtime state is written under `.devmemory/` (gitignored); curated, redacted public traces are written under `docs/showcase/`.
- Control plane mirrors the Luffy PR-review agent shape: assemble → `hermes -z` → normalize → apply → human git review.

## Design decisions
- Extraction pipeline stages: assemble → hermes extract → normalize → apply.
- Hermes is used as a CLI dependency (hermes -z), not included as vendored source.
- OpenRouter serves as the LLM provider for extraction.
- Knowledge extraction operates entirely locally with transcripts never leaving the developer's machine.

## Patterns
- DEV.md captures architecture, design decisions, patterns, pitfalls, and module-specific engineering context.
- USAGE.md captures setup steps, commands, debugging, troubleshooting, and workflows essential for working with the code part.
- Extraction process keeps knowledge generation as an automatic by-product of development sessions.
- Schemas are frozen pydantic models: `KnowledgeUnit` / `ExtractionResult` in `schema.py`.

## Pitfalls
- Reda
… [truncated; do not restate] …

### src/devmemory/sources/DEV.md

## Architecture
- Two Claude importers feed one discovery API: `ClaudeHistorySource` reads the flat `~/.claude/history.jsonl` prompt log, `ClaudeProjectSource` reads full transcripts from `~/.claude/projects/<encoded-path>/*.jsonl`.
- `ClaudeHistorySource.list_sessions` buckets history lines by `sessionId` and joins their texts chronologically, so a multi-turn history log yields one `SessionRecord` per session instead of one per prompt.
- `discover_claude_sessions` merges both sources newest-first and prefers the project record when the same session id appears in both (project JSONL carries richer multi-role transcripts).
- Records carry `meta["turns"]` (and `meta["project_dir"]` for project sessions) so callers/CLI can show session size without re-reading the files.

## Design decisions
- Discovery scopes to the repo by *project path*, not by name: `project_matches_repo` accepts the repo's resolved absolute path and any path under it, so sessions started in a subdirectory of the repo still count.
- The earlier soft "repo name appears in project string" fallback was removed from history filtering because it pulled in unrelated repos; `repo_root=` filtering replaces `project_filter=` for that call path.
- History/project roots are overridable via `DEVMEMORY_CLAUDE_HISTORY` and `DEVMEMORY_CLAUDE_PROJECTS` specifically so tests can point at fixtures instead of the real `~/.claude`.
- `encode_project_path` (public; `_encode_project_path` kept as a back-compat alias) implements Claude's `/Users/foo/bar -> -Users-foo-bar` encoding, and project-dir matching layers exact match, enc
… [truncated; do not restate] …

### USAGE.md

## Setup
- Create and activate Python virtual environment: `python3 -m venv .venv && source .venv/bin/activate`.
- `pip install -e '.[dev]'`.
- Set `OPENROUTER_API_KEY` (or `DEVMEMORY_ENV_FILE`) for live extraction.
- Run `./scripts/ensure-hermes.sh` once to install Hermes CLI.

## Common commands
- Readiness: `devmemory doctor` (table + JSON); `devmemory doctor --strict` fails unless live-ready; `devmemory doctor --json` for CI
- Dry-run extract (units + proposed paths + unified `preview.diff`): `devmemory extract --fixture sample-auth-module`
- Review knowledge diff: open `.devmemory/out/<run>/preview.diff` or read the colorized CLI print
- Real Claude session: `devmemory extract --session <id> --apply` (default without flags prefers latest unprocessed Claude session for cwd)

## Claude Code hook (SessionEnd)
- Auto-write: `export DEVMEMORY_HOOK_APPLY=1` before Claude Code.
- Prefer **SessionEnd** over **Stop** (Stop fires every turn; thrashy). Opt-in: `./scripts/install-claude-hook.sh --with-stop`.
- **Tool-edit gate (default on):** skips extract when the session transcript has no Write/Edit-class tools (chat-only). Opt out: `export DEVMEMORY_HOOK_REQUIRE_EDITS=0`. Missing transcript still allows a run.
- Print fragment only: `./scripts/install-claude-hook.sh --print`.

## Troubleshooting
- Hollow `## Architecture` / `## Troubleshooting` headings mean the file predates the empty-section scrub; re-run apply to scrub them.
- After a dogfood run: `devmemory review` then `git diff` as the human gate.
- Hook silent? Check `.devmemory/hooks.log`; ensure `devmemory` is on PATH 
… [truncated; do not restate] …

### src/auth/USAGE.md

## Setup
- For local development, set environment variable `AUTH_SECRET=dev-only` before running the server with uvicorn.

## Common commands
- Run tests with `pytest tests/auth -q`.
- Start the development server with `uvicorn app.main:app --reload --port 8000`.

## Debugging
- If receiving a 401 on a valid token, check for clock skew and verify that the `AUTH_SECRET` matches the issuer.

### src/devmemory/USAGE.md

## Common commands
- Live dogfood extract with showcase: `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase` (add `--showcase-dir <path>` for a custom output dir).
- `--force` re-processes a session that is already recorded in the cursor.
- Point env loading at an external file and pin the model before a live run: `export DEVMEMORY_ENV_FILE=<path to .env>` and `export DEVMEMORY_MODEL=anthropic/claude-opus-5`.
- End-to-end smoke: `./scripts/smoke-e2e.sh`; Hermes-only connectivity check: `./scripts/smoke-hermes.sh`.

## Debugging
- `hermes_rc != 0`: inspect `extract.raw.stderr` in the run dir, and confirm the seeded `HERMES_HOME/.env` is mode 0600 and contains `OPENROUTER_API_KEY`.
- Zero units: read `extract.raw.md` for non-JSON output; the offline heuristic fallback should still produce units.
- Wrong unit path: confirm the directory appears in `EXISTING_DIRS` of the assembled prompt and that the tree sample includes the module dir.
- Per-stage `timings.json` in the run dir shows which phase is slow (assemble vs extract vs normalize vs apply).

## Troubleshooting
- Context size is tunable via env: `DEVMEMORY_MAX_SESSION_CHARS` (24000), `DEVMEMORY_MAX_DIFF_CHARS` (40000), `DEVMEMORY_MAX_TREE_LINES` (200), `DEVMEMORY_MAX_KNOWLEDGE_CHARS` (1600). Raise these only when the model is clearly missing evidence — larger prompts increase restatement.
- Docs growing on every run: verify near-dupe skipping is active (`apply.dedupe_section_bullets` / `scrub_file_near_dupes`) rather than editing the docs by hand.

## Debugging
- No real sessions being picked 
… [truncated; do not restate] …

