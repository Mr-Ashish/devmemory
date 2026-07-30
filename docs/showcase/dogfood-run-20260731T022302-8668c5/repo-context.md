# Repository context

- **root:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **assembled_at:** 2026-07-30T20:53:02Z

## git status

```
M DEV.md
 M USAGE.md
 M src/auth/DEV.md
 M src/auth/USAGE.md
 M src/devmemory/USAGE.md
 M src/devmemory/apply.py
 M src/devmemory/sections.py
 M tests/test_apply.py
```

## recent log

```
a3dfefc Include redacted Hermes agent.log in dogfood showcase
2016aee Dogfood Opus 5 self-extract with traces, showcase, brand, and docs
d5f78f4 Implement devmemory MVP with high-ROI knowledge quality fixes
c379765 Initial commit: copy README from archit15singh/devmemory
```

## tree (sample)

```
DEV.md
PLAN.md
README.md
USAGE.md
pyproject.toml
tests/test_apply.py
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
docs/evals/2026-07-31-dogfood-opus5.md
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
scripts/ensure-hermes.sh
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
src/devmemory/sources/__init__.py
src/devmemory/sources/base.py
src/devmemory/sources/claude.py
src/devmemory/sources/fixtures.py
```

## git diff

```
diff --git a/DEV.md b/DEV.md
index 9d3f54b..7f40833 100644
--- a/DEV.md
+++ b/DEV.md
@@ -2,12 +2,6 @@
 
 > How this part of the system is built.
 
-## Architecture
-
-## Design decisions
-
-## Patterns
-
 ## Pitfalls
 - Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
 - Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
diff --git a/USAGE.md b/USAGE.md
index 5c3257b..a110e53 100644
--- a/USAGE.md
+++ b/USAGE.md
@@ -17,7 +17,3 @@
 - Hermes CLI can be installed and ensured via `./scripts/ensure-hermes.sh`.
 - Various devmemory CLI commands available: `init`, `list-sessions`, `extract`, `apply --run <id>`, `status`, and `review`.
 - Example extract commands: `devmemory extract --fixture sample-auth-module --apply`, `devmemory extract --session <id> --apply`, `devmemory extract --offline --apply` for offline mode.
-
-## Debugging
-
-## Troubleshooting
diff --git a/src/auth/DEV.md b/src/auth/DEV.md
index a38affa..a645e2a 100644
--- a/src/auth/DEV.md
+++ b/src/auth/DEV.md
@@ -2,8 +2,6 @@
 
 > How this part of the system is built.
 
-## Architecture
-
 ## Design decisions
 
 - Authentication middleware is located in `src/auth/`.
diff --git a/src/auth/USAGE.md b/src/auth/USAGE.md
index 5432a83..599ca65 100644
--- a/src/auth/USAGE.md
+++ b/src/auth/USAGE.md
@@ -14,5 +14,3 @@
 ## Debugging
 
 - If receiving a 401 on a valid token, check for clock skew and verify that the `AUTH_SECRET` matches the issuer.
-
-## Troubleshooting
diff --git a/src/devmemory/USAGE.md b/src/devmemory/USAGE.md
index cb6e27c..aed1e56 100644
--- a/src/devmemory/USAGE.md
+++ b/src/devmemory/USAGE.md
@@ -2,8 +2,6 @@
 
 > How to work with this part of the system.
 
-## Setup
-
 ## Common commands
 
 - Live dogfood extract with showcase: `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase` (add `--showcase-dir <path>` for a custom output dir).
@@ -21,5 +19,3 @@
 - Per-stage `timings.json` in the run dir shows which phase is slow (assemble vs extract vs normalize vs apply).
 - Showcase privacy check: `trace.py` strips `sk-or` keys, `Bearer` tokens and env assignments before anything lands in `docs/showcase/`.
 - Test coverage targets ≥19 unit tests spanning redaction, normalize, apply dedupe, path snap and offline extract.
-
-## Troubleshooting
diff --git a/src/devmemory/apply.py b/src/devmemory/apply.py
index e4e211b..0979ee1 100644
--- a/src/devmemory/apply.py
+++ b/src/devmemory/apply.py
@@ -15,30 +15,17 @@ from devmemory.sections import (
     strip_placeholders,
 )
 
+# Sections are created on first content — avoid empty H2 scaffolding.
 DEV_TEMPLATE = """# DEV — engineering knowledge
 
 > How this part of the system is built.
 
-## Architecture
-
-## Design decisions
-
-## Patterns
-
-## Pitfalls
 """
 
 USAGE_TEMPLATE = """# USAGE — operational knowledge
 
 > How to work with this part of the system.
 
-## Setup
-
-## Common commands
-
-## Debugging
-
-## Troubleshooting
 """
 
 
diff --git a/src/devmemory/sections.py b/src/devmemory/sections.py
index 4674486..546d3e1 100644
--- a/src/devmemory/sections.py
+++ b/src/devmemory/sections.py
@@ -100,4 +100,44 @@ def strip_placeholders(text: str) -> str:
         else:
             blank = 0
             out.append(ln)
-    return "\n".join(out).rstrip() + "\n"
+    return scrub_empty_h2_sections("\n".join(out).rstrip() + "\n")
+
+
+def scrub_empty_h2_sections(text: str) -> str:
+    """Drop ## sections whose body is only whitespace (or placeholders already removed).
+
+    Keeps H1, blockquotes, and any H2 that has at least one non-empty body line.
+    """
+    if not text.strip():
+        return text if text.endswith("\n") else text + "\n"
+
+    lines = text.splitlines()
+    # Find H2 indices
+    h2_idx = [i for i, ln in enumerate(lines) if re.match(r"^##\s+\S", ln)]
+    if not h2_idx:
+        return text if text.endswith("\n") else text + "\n"
+
+    drop: set[int] = set()
+    for n, start in enumerate(h2_idx):
+        end = h2_idx[n + 1] if n + 1 < len(h2_idx) else len(lines)
+        body = lines[start + 1 : end]
+        if any(ln.strip() for ln in body):
+            continue
+        # empty body → drop heading and blank lines until next H2
+        for j in range(start, end):
+            drop.add(j)
+
+    kept = [ln for i, ln in enumerate(lines) if i not in drop]
+    # collapse excess blanks
+    out: list[str] = []
+    blank = 0
+    for ln in kept:
+        if not ln.strip():
+            blank += 1
+            if blank <= 2:
+                out.append(ln)
+        else:
+            blank = 0
+            out.append(ln)
+    result = "\n".join(out).rstrip() + "\n"
+    return result
diff --git a/tests/test_apply.py b/tests/test_apply.py
index ca2ed9c..446cc74 100644
--- a/tests/test_apply.py
+++ b/tests/test_apply.py
@@ -108,6 +108,33 @@ def test_apply_strips_placeholders(tmp_path: Path):
     assert "_(none yet)_" not in text
 
 
+def test_apply_scrubs_empty_h2_sections(tmp_path: Path):
+    p = tmp_path / "DEV.md"
+    p.write_text(
+        "# DEV\n\n## Architecture\n\n## Design decisions\n\n## Patterns\n\n"
+        "## Pitfalls\n- Never commit secrets.\n",
+        encoding="utf-8",
+    )
+    ch = apply_unit(
+        tmp_path,
+        KnowledgeUnit(
+            kind="dev",
+            path=".",
+            section="Patterns",
+            content="- Colocate knowledge with code",
+            confidence="high",
+        ),
+    )
+    assert ch is not None
+    text = p.read_text()
+    assert "## Architecture" not in text  # stayed empty → scrubbed
+    assert "## Design decisions" not in text
+    assert "## Patterns" in text
+    assert "Colocate knowledge" in text
+    assert "## Pitfalls" in text
+    assert "Never commit secrets" in text
+
+
 def test_apply_snaps_invented_path_to_existing(tmp_path: Path):
     (tmp_path / "src" / "auth").mkdir(parents=True)
     ch = apply_unit(
```

## existing knowledge files

### DEV.md

# DEV — engineering knowledge

> How this part of the system is built.

## Pitfalls
- Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
- Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.


### src/auth/DEV.md

# DEV — engineering knowledge

> How this part of the system is built.

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

# DEV — engineering knowledge

> How this part of the system is built.

## Architecture

- Module layout: `cli.py` (Click CLI), `assemble.py` (bounded context, no LLM), `extract.py` (Hermes orchestration + timings + showcase flag), `normalize.py` (JSON units + post-parse redaction), `apply.py` (merge into DEV.md/USAGE.md), `paths.py` (`list_repo_dirs` + `resolve_unit_path`), `sections.py` (canonicalize section titles), `trace.py` (redacted showcase packaging), `sources/` (fixtures + Claude history/project).
- `agent/` holds SOUL.md, config.yaml and extract-prompt.md used to seed the Hermes home before a live run.
- Runtime state is written under `.devmemory/` (gitignored); curated, redacted public traces are written under `docs/showcase/`.
- Control plane mirrors the Luffy PR-review agent shape: assemble → `hermes -z` → normalize → apply → human git review.
- `extract_session` records per-stage timings (assemble/extract/normalize/apply/total) into `timings.json` in the run dir and surfaces them on `ExtractOutcome`.

## Design decisions

- Extraction pipeline stages: assemble → hermes extract → normalize → apply.
- Hermes is used as a CLI dependency (hermes -z), not included as vendored source.
- OpenRouter serves as the LLM provider for extraction.
- Knowledge extraction operates entirely locally with transcripts never leaving the developer's machine.
- Knowledge files (DEV.md and USAGE.md) are maintained colocated next to code modules to keep documentation context-specific and easily accessible.
- The process avoids committing raw AI session transcripts or .devmemory/ run artifacts to source control.
- Extraction pipeline inputs include Claude Code session transcripts, current repository code changes, and outputs knowledge merged into local DEV.md and USAGE.md files.
- CI workflows validate the consistency and freshness of generated knowledge files without requiring access to local transcripts.

- The apply layer is the product quality boundary: path snapping to existing dirs, canonical H2 sections, bullet near-dupe skip, placeholder scrub. The LLM proposes; merge decides.
- Default extraction model is `anthropic/claude-opus-5` (dogfood quality); `openai/gpt-4.1-mini` is acceptable for cheap iteration. Resolution order is `--model` → `DEVMEMORY_MODEL` → default.
- Hermes toolsets are empty by default for extract so the run is pure reasoning over the assembled context; set `DEVMEMORY_TOOLSETS=terminal` only when a run genuinely needs shell access.
- Showcase packaging is opt-in via `--showcase` / `--showcase-dir`; `trace.py` redacts before writing, so only sanitized traces reach `docs/showcase/`.
- `hermes-agent-self-evolution` is an idea source only (session importers, secret-redaction patterns, later skill GEPA) and is not part of the MVP runtime.
- Live runs export `HERMES_TUI_TOOL_PROGRESS=verbose` so dogfood traces capture agent tool progress.

## Patterns

- Knowledge extraction pipeline runs as 4 separate phases: assemble context, extract knowledge using Hermes CLI call, normalize JSON output, then apply merged changes.
- Localized knowledge files (DEV.md for engineering details, USAGE.md for operational instructions) live next to code modules to provide context-targeted documentation.
- DEV.md captures architecture, design decisions, patterns, pitfalls, and module-specific engineering context.
- USAGE.md captures setup steps, commands, debugging, troubleshooting, and workflows essential for working with the code part.
- Extraction process keeps knowledge generation as an automatic by-product of development sessions.

- Schemas are frozen pydantic models: `KnowledgeUnit` / `ExtractionResult` in `schema.py`.
- A session is only marked processed when `units > 0`, so empty or failed runs never poison the cursor.
- An offline heuristic extract (path inference + command-line regex) keeps CI green without an OpenRouter key; it also acts as a fallback when a live run returns no parseable units.
- Dogfood loop: improve the prod

### USAGE.md

# USAGE — operational knowledge

> How to work with this part of the system.

## Setup

- Create and activate Python virtual environment.
- Set `OPENROUTER_API_KEY` environment variable for live extraction.
- Optionally set `DEVMEMORY_ENV_FILE` for loading env vars.
- Run `./scripts/ensure-hermes.sh` to install Hermes CLI and verify setup.

## Common commands

- pip install -e '.[dev]' to set up development environment.
- Use `devmemory extract --fixture sample-auth-module --apply` to run the extraction and apply knowledge updates.
- Run tests via `pytest -q`.
- Hermes CLI can be installed and ensured via `./scripts/ensure-hermes.sh`.
- Various devmemory CLI commands available: `init`, `list-sessions`, `extract`, `apply --run <id>`, `status`, and `review`.
- Example extract commands: `devmemory extract --fixture sample-auth-module --apply`, `devmemory extract --session <id> --apply`, `devmemory extract --offline --apply` for offline mode.


### src/auth/USAGE.md

# USAGE — operational knowledge

> How to work with this part of the system.

## Setup

- For local development, set environment variable `AUTH_SECRET=dev-only` before running the server with uvicorn.

## Common commands

- Run tests with `pytest tests/auth -q`.
- Start the development server with `uvicorn app.main:app --reload --port 8000`.

## Debugging

- If receiving a 401 on a valid token, check for clock skew and verify that the `AUTH_SECRET` matches the issuer.


### src/devmemory/USAGE.md

# USAGE — operational knowledge

> How to work with this part of the system.

## Common commands

- Live dogfood extract with showcase: `devmemory extract --fixture dogfood-build-narrative --apply --force --showcase` (add `--showcase-dir <path>` for a custom output dir).
- `--force` re-processes a session that is already recorded in the cursor.
- Point env loading at an external file and pin the model before a live run: `export DEVMEMORY_ENV_FILE=<path to .env>` and `export DEVMEMORY_MODEL=anthropic/claude-opus-5`.
- End-to-end smoke: `./scripts/smoke-e2e.sh`; Hermes-only connectivity check: `./scripts/smoke-hermes.sh`.
- `devmemory review` shows the pending doc changes for human git review.
- The last line of `devmemory extract` stdout is machine-readable JSON including `units`, `changes`, `model`, `hermes_rc`, `timings` and `showcase`.

## Debugging

- `hermes_rc != 0`: inspect `extract.raw.stderr` in the run dir, and confirm the seeded `HERMES_HOME/.env` is mode 0600 and contains `OPENROUTER_API_KEY`.
- Zero units: read `extract.raw.md` for non-JSON output; the offline heuristic fallback should still produce units.
- Wrong unit path: confirm the directory appears in `EXISTING_DIRS` of the assembled prompt and that the tree sample includes the module dir.
- Per-stage `timings.json` in the run dir shows which phase is slow (assemble vs extract vs normalize vs apply).
- Showcase privacy check: `trace.py` strips `sk-or` keys, `Bearer` tokens and env assignments before anything lands in `docs/showcase/`.
- Test coverage targets ≥19 unit tests spanning redaction, normalize, apply dedupe, path snap and offline extract.


