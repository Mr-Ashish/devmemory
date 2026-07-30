# Repository context

- **root:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **assembled_at:** 2026-07-30T20:57:31Z

## git status

```
M DEV.md
 M USAGE.md
 M src/auth/DEV.md
 M src/auth/USAGE.md
 M src/devmemory/DEV.md
 M src/devmemory/USAGE.md
 M src/devmemory/apply.py
 M src/devmemory/assemble.py
 M tests/test_apply.py
```

## recent log

```
3e2b3dd Dogfood loop: scrub empty H2s and block knowledge under tests/docs
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
docs/evals/2026-07-31-dogfood-iter1-empty-h2.md
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
index cab673c..927890b 100644
--- a/DEV.md
+++ b/DEV.md
@@ -5,8 +5,6 @@
 ## Pitfalls
 - Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
 - Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
-- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.
-
-## Patterns
+- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.## Patterns
 
 - Eval notes live under docs/evals but knowledge should root
diff --git a/USAGE.md b/USAGE.md
index d9da0dc..fddbfad 100644
--- a/USAGE.md
+++ b/USAGE.md
@@ -7,18 +7,14 @@
 - Create and activate Python virtual environment.
 - Set `OPENROUTER_API_KEY` environment variable for live extraction.
 - Optionally set `DEVMEMORY_ENV_FILE` for loading env vars.
-- Run `./scripts/ensure-hermes.sh` to install Hermes CLI and verify setup.
-
-## Common commands
+- Run `./scripts/ensure-hermes.sh` to install Hermes CLI and verify setup.## Common commands
 
 - pip install -e '.[dev]' to set up development environment.
 - Use `devmemory extract --fixture sample-auth-module --apply` to run the extraction and apply knowledge updates.
 - Run tests via `pytest -q`.
 - Hermes CLI can be installed and ensured via `./scripts/ensure-hermes.sh`.
 - Various devmemory CLI commands available: `init`, `list-sessions`, `extract`, `apply --run <id>`, `status`, and `review`.
-- Example extract commands: `devmemory extract --fixture sample-auth-module --apply`, `devmemory extract --session <id> --apply`, `devmemory extract --offline --apply` for offline mode.
-
-## Troubleshooting
+- Example extract commands: `devmemory extract --fixture sample-auth-module --apply`, `devmemory extract --session <id> --apply`, `devmemory extract --offline --apply` for offline mode.## Troubleshooting
 
 - Hollow `## Architecture` / `## Troubleshooting` headings left in a DEV.md or USAGE.md mean the file predates the empty-section scrub; re-running any apply against that file removes them automatically.
 - After a dogfood run, `devmemory review` then plain `git diff` is the intended human gate — expect the diff to include deletions of previously empty H2 sections, not just added bullets.
diff --git a/src/auth/DEV.md b/src/auth/DEV.md
index a645e2a..81c51e6 100644
--- a/src/auth/DEV.md
+++ b/src/auth/DEV.md
@@ -6,12 +6,8 @@
 
 - Authentication middleware is located in `src/auth/`.
 - Token verification is separated from user lookup.
-- Tokens are currently signed with HS256; plan to migrate to RS256 later.
-
-## Patterns
+- Tokens are currently signed with HS256; plan to migrate to RS256 later.## Patterns
 
 - Use a `require_auth` decorator on all protected routes.
-- The decorator reads the `Authorization: Bearer` header to obtain the token.
-
-## Pitfalls
+- The decorator reads the `Authorization: Bearer` header to obtain the token.## Pitfalls
 - Avoid logging the raw `Authorization` header as it contains secrets.
diff --git a/src/auth/USAGE.md b/src/auth/USAGE.md
index 599ca65..2239289 100644
--- a/src/auth/USAGE.md
+++ b/src/auth/USAGE.md
@@ -4,13 +4,9 @@
 
 ## Setup
 
-- For local development, set environment variable `AUTH_SECRET=dev-only` before running the server with uvicorn.
-
-## Common commands
+- For local development, set environment variable `AUTH_SECRET=dev-only` before running the server with uvicorn.## Common commands
 
 - Run tests with `pytest tests/auth -q`.
-- Start the development server with `uvicorn app.main:app --reload --port 8000`.
-
-## Debugging
+- Start the development server with `uvicorn app.main:app --reload --port 8000`.## Debugging
 
 - If receiving a 401 on a valid token, check for clock skew and verify that the `AUTH_SECRET` matches the issuer.
diff --git a/src/devmemory/DEV.md b/src/devmemory/DEV.md
index c65fdb4..87bbb87 100644
--- a/src/devmemory/DEV.md
+++ b/src/devmemory/DEV.md
@@ -8,9 +8,7 @@
 - `agent/` holds SOUL.md, config.yaml and extract-prompt.md used to seed the Hermes home before a live run.
 - Runtime state is written under `.devmemory/` (gitignored); curated, redacted public traces are written under `docs/showcase/`.
 - Control plane mirrors the Luffy PR-review agent shape: assemble → `hermes -z` → normalize → apply → human git review.
-- `extract_session` records per-stage timings (assemble/extract/normalize/apply/total) into `timings.json` in the run dir and surfaces them on `ExtractOutcome`.
-
-## Design decisions
+- `extract_session` records per-stage timings (assemble/extract/normalize/apply/total) into `timings.json` in the run dir and surfaces them on `ExtractOutcome`.## Design decisions
 
 - Extraction pipeline stages: assemble → hermes extract → normalize → apply.
 - Hermes is used as a CLI dependency (hermes -z), not included as vendored source.
@@ -30,9 +28,7 @@
 
 - `DEV_TEMPLATE` / `USAGE_TEMPLATE` in `apply.py` contain only the H1 and the blockquote — canonical H2 sections are created on first real content instead of being pre-scaffolded empty.
 - `sections.strip_placeholders` ends by calling `scrub_empty_h2_sections`, so placeholder removal and hollow-heading removal are a single pass on every apply.
-- `scrub_empty_h2_sections` drops an `## ` heading plus its trailing blanks when every body line up to the next H2 is whitespace, keeps H1/blockquotes untouched, and collapses runs of blank lines to at most two.
-
-## Patterns
+- `scrub_empty_h2_sections` drops an `## ` heading plus its trailing blanks when every body line up to the next H2 is whitespace, keeps H1/blockquotes untouched, and collapses runs of blank lines to at most two.## Patterns
 
 - Knowledge extraction pipeline runs as 4 separate phases: assemble context, extract knowledge using Hermes CLI call, normalize JSON output, then apply merged changes.
 - Localized knowledge files (DEV.md for engineering details, USAGE.md for operational instructions) live next to code modules to provide context-targeted documentation.
@@ -43,17 +39,11 @@
 - Schemas are frozen pydantic models: `KnowledgeUnit` / `ExtractionResult` in `schema.py`.
 - A session is only marked processed when `units > 0`, so empty or failed runs never poison the cursor.
 - An offline heuristic extract (path inference + command-line regex) keeps CI green without an OpenRouter key; it also acts as a fallback when a live run returns no parseable units.
-- Dogfood loop: improve the product → run extract on this repo → update DEV/USAGE → capture a showcase package → push.
-
-## Pitfalls
+- Dogfood loop: improve the product → run extract on this repo → update DEV/USAGE → capture a showcase package → push.## Pitfalls
 - Redacting secrets before parsing breaks JSON — run redaction on string fields *after* the JSON parse in `normalize.py`.
 - Without bullet near-dupe skipping, re-running extract thrashes DEV.md/USAGE.md with restated content.
 - LLM-invented paths create junk doc trees — always snap a unit's path onto an existing directory (or `.`).
 - Enabling terminal tools during extract slows the run and distracts the model from the JSON output contract.
 - Never commit `.env` alongside `.devmemory/` and raw transcripts.
 
-- Redacting secrets before JSON parse corrupts the payload — run redaction over string fields *after* `normalize.py` parses the units.
-- Re-running extract without bullet near-dupe skipping thrashes DEV.md/USAGE.md with restated bullets.
-- Model-invented paths create junk directory trees; every unit path must snap to a directory that already exists.
-- Enabling terminal tools during extract slows the run and pulls the model off the JSON output contract.
 - Pre-seeding every canonical H2 leaves hollow headings and `_(none yet)_` placeholders in shipped docs; let the merge create sections lazily.
diff --git a/src/devmemory/USAGE.md b/src/devmemory/USAGE.md
index aed1e56..fcb017e 100644
--- a/src/devmemory/USAGE.md
+++ b/src/devmemory/USAGE.md
@@ -9,9 +9,7 @@
 - Point env loading at an external file and pin the model before a live run: `export DEVMEMORY_ENV_FILE=<path to .env>` and `export DEVMEMORY_MODEL=anthropic/claude-opus-5`.
 - End-to-end smoke: `./scripts/smoke-e2e.sh`; Hermes-only connectivity check: `./scripts/smoke-hermes.sh`.
 - `devmemory review` shows the pending doc changes for human git review.
-- The last line of `devmemory extract` stdout is machine-readable JSON including `units`, `changes`, `model`, `hermes_rc`, `timings` and `showcase`.
-
-## Debugging
+- The last line of `devmemory extract` stdout is machine-readable JSON including `units`, `changes`, `model`, `hermes_rc`, `timings` and `showcase`.## Debugging
 
 - `hermes_rc != 0`: inspect `extract.raw.stderr` in the run dir, and confirm the seeded `HERMES_HOME/.env` is mode 0600 and contains `OPENROUTER_API_KEY`.
 - Zero units: read `extract.raw.md` for non-JSON output; the offline heuristic fallback should still produce units.
diff --git a/src/devmemory/apply.py b/src/devmemory/apply.py
index 0979ee1..9c89797 100644
--- a/src/devmemory/apply.py
+++ b/src/devmemory/apply.py
@@ -60,10 +60,44 @@ def _ensure_file(path: Path, kind: str) -> str:
 def _norm_bullet(line: str) -> str:
     s = line.strip().lstrip("-*").strip().lower()
     s = re.sub(r"\s+", " ", s)
-    s = re.sub(r"[`*]", "", s)
+    s = re.sub(r"[`*_'\".,;:()\[\]{}]", "", s)
     return s
 
 
+def _stem(tok: str) -> str:
+    t = tok
+    # longest-first; avoid over-stemming ("existing" must not become "exis")
+    for suf in ("ations", "ation", "tions", "iness", "ingly", "ing", "ers", "ies", "ied", "ed", "es", "s"):
+        if len(t) > len(suf) + 3 and t.endswith(suf):
+            return t[: -len(suf)]
+    return t
+
+
+def _token_set(norm: str) -> set[str]:
+    return {_stem(t) for t in norm.split() if len(t) > 2}
+
+
+def _near_duplicate(a: str, b: str, *, threshold: float = 0.52) -> bool:
+    """True if two normalized bullets are the same claim (containment or Jaccard)."""
+    if not a or not b:
+        return False
+    if a == b:
+        return True
+    if len(a) > 24 and len(b) > 24 and (a in b or b in a):
+        return True
+    ta, tb = _token_set(a), _token_set(b)
+    if not ta or not tb:
+        return False
+    inter = len(ta & tb)
+    union = len(ta | tb)
+    if union == 0:
+        return False
+    jacc = inter / union
+    smaller = min(len(ta), len(tb))
+    cover = inter / smaller if smaller else 0.0
+    return jacc >= threshold or cover >= 0.62
+
+
 def _content_bullets(content: str) -> list[str]:
     lines = []
     for ln in content.splitlines():
@@ -78,25 +112,54 @@ def _content_bullets(content: str) -> list[str]:
 
 
 def _filter_new_bullets(existing_section_body: str, content: str) -> str:
-    """Return only bullets not already present (normalized)."""
-    existing_norms = {
+    """Return only bullets not already present (normalized / near-dupe)."""
+    existing_norms = [
         _norm_bullet(ln)
         for ln in existing_section_body.splitlines()
         if ln.strip().startswith(("-", "*"))
-    }
+    ]
     kept: list[str] = []
     for b in _content_bullets(content):
         n = _norm_bullet(b)
-        if not n or n in existing_norms:
+        if not n:
             continue
-        # near-duplicate: existing bullet contains new or vice versa
-        if any(n in e or e in n for e in existing_norms if len(e) > 20 and len(n) > 20):
+        if any(_near_duplicate(n, e) for e in existing_norms):
             continue
         kept.append(b)
-        existing_norms.add(n)
+        existing_norms.append(n)
     return "\n".join(kept)
 
 
+def dedupe_section_bullets(body: str) -> str:
+    """Drop near-duplicate bullets already inside a section body (first wins)."""
+    out: list[str] = []
+    norms: list[str] = []
+    for ln in body.splitlines():
+        if ln.strip().startswith(("-", "*")):
+            n = _norm_bullet(ln)
+            if n and any(_near_duplicate(n, e) for e in norms):
+                continue
+            if n:
+                norms.append(n)
+            out.append(ln)
+        else:
+            out.append(ln)
+    return "\n".join(out)
+
+
+def scrub_file_near_dupes(text: str) -> str:
+    """Within each H2 section, keep first bullet when near-duplicates appear."""
+    pattern = re.compile(
+        r"(^##\s+[^\n]+\n)([\s\S]*?)(?=^##\s+|\Z)",
+        re.MULTILINE,
+    )
+
+    def repl(m: re.Match) -> str:
+        return m.group(1) + dedupe_section_bullets(m.group(2))
+
+    return strip_placeholders(pattern.sub(repl, text))
+
+
 def _section_exists(text: str, section: str) -> bool:
     heading = section.strip().lstrip("#").strip()
     pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE | re.IGNORECASE)
@@ -113,14 +176,19 @@ def _append_section(text: str, section: str | None, content: str) -> str:
         m = pattern.search(text)
         if m:
             body = m.group(2)
-            body_clean = "\n".join(
-                ln for ln in body.splitlines() if not is_placeholder_line(ln)
+            body_clean = dedupe_section_bullets(
+                "\n".join(
+                    ln for ln in body.splitlines() if not is_placeholder_line(ln)
+                )
             )
             new_bullets = _filter_new_bullets(body_clean, content)
             if not new_bullets.strip():
-                # still scrub placeholders if any
                 cleaned = strip_placeholders(
-                    text[: m.start()] + m.group(1) + body_clean.rstrip() + "\n\n" + text[m.end() :]
+                    text[: m.start()]
+                    + m.group(1)
+                    + body_clean.rstrip()
+                    + "\n\n"
+                    + text[m.end() :]
                 )
                 return cleaned if cleaned != strip_placeholders(text) else text
             new_body = body_clean.rstrip()
diff --git a/src/devmemory/assemble.py b/src/devmemory/assemble.py
index bf135a1..6409283 100644
--- a/src/devmemory/assemble.py
+++ b/src/devmemory/assemble.py
@@ -6,7 +6,7 @@ import os
 import subprocess
 from pathlib import Path
 
-from devmemory.paths import list_repo_dirs
+from devmemory.paths import is_knowledge_blocked, list_repo_dirs
 from devmemory.redaction import redact
 from devmemory.sources.base import SessionRecord
 from devmemory.state import RunContext, utc_now
@@ -14,6 +14,7 @@ from devmemory.state import RunContext, utc_now
 MAX_SESSION_CHARS = int(os.environ.get("DEVMEMORY_MAX_SESSION_CHARS", "24000"))
 MAX_DIFF_CHARS = int(os.environ.get("DEVMEMORY_MAX_DIFF_CHARS", "40000"))
 MAX_TREE_LINES = int(os.environ.get("DEVMEMORY_MAX_TREE_LINES", "200"))
+MAX_KNOWLEDGE_FILE_CHARS = int(os.environ.get("DEVMEMORY_MAX_KNOWLEDGE_CHARS", "1600"))
 
 
 def _run(cmd: list[str], cwd: Path) -> str:
@@ -60,24 +61,32 @@ def collect_repo_context(repo_root: Path) -> dict[str, str]:
         if len(tree_lines) >= MAX_TREE_LINES:
             break
 
-    # existing knowledge files
+    # existing knowledge — compact to cut restate thrash in the LLM
     knowledge: list[str] = []
     for name in ("DEV.md", "USAGE.md"):
         for p in repo_root.rglob(name):
             if any(part.startswith(".") for part in p.parts):
                 continue
             rel = p.relative_to(repo_root)
+            rel_s = str(rel.parent).replace("\\", "/") if rel.name else "."
+            if rel_s == ".":
+                owner = "."
+            else:
+                owner = str(rel.parent).replace("\\", "/")
+            if is_knowledge_blocked(owner if owner != "." else str(rel).split("/")[0] if "/" in str(rel) else "."):
+                # skip knowledge under blocked trees if any slipped in
+                if owner != "." and is_knowledge_blocked(owner):
+                    continue
             try:
-                body = p.read_text(encoding="utf-8", errors="replace")[:4000]
+                body = p.read_text(encoding="utf-8", errors="replace")
             except OSError:
                 continue
-            knowledge.append(f"### {rel}\n\n{body}\n")
+            knowledge.append(f"### {rel}\n\n{_compact_knowledge(body)}\n")
 
     if len(diff) > MAX_DIFF_CHARS:
         diff = diff[:MAX_DIFF_CHARS] + "\n\n… [diff truncated] …\n"
 
-    dirs = list_repo_dirs(repo_root)
-    # Prefer shorter list for the prompt (root + first 80)
+    dirs = [d for d in list_repo_dirs(repo_root) if d == "." or not is_knowledge_blocked(d)]
     dir_list = dirs[:80]
 
     return {
@@ -90,6 +99,27 @@ def collect_repo_context(repo_root: Path) -> dict[str, str]:
     }
 
 
+def _compact_knowledge(body: str) -> str:
+    """Keep H2 titles + up to 5 bullets per section (token thrift, anti-restate)."""
+    import re
+
+    parts: list[str] = []
+    for m in re.finditer(r"(^##\s+[^\n]+)\n([\s\S]*?)(?=^##\s+|\Z)", body, re.M):
+        title = m.group(1).strip()
+        bullets = [
+            ln.strip()
+            for ln in m.group(2).splitlines()
+            if ln.strip().startswith(("-", "*"))
+        ][:5]
+        if not bullets:
+            continue
+        parts.append(title + "\n" + "\n".join(bullets))
+    text = "\n\n".join(parts) if parts else body[:MAX_KNOWLEDGE_FILE_CHARS]
+    if len(text) > MAX_KNOWLEDGE_FILE_CHARS:
+        text = text[:MAX_KNOWLEDGE_FILE_CHARS] + "\n… [truncated; do not restate] …"
+    return text
+
+
 def assemble(
     ctx: RunContext,
     session: SessionRecord,
diff --git a/tests/test_apply.py b/tests/test_apply.py
index 446cc74..437ff2a 100644
--- a/tests/test_apply.py
+++ b/tests/test_apply.py
@@ -86,6 +86,38 @@ def test_apply_skips_near_duplicate_bullets(tmp_path: Path):
     assert changes == []
 
 
+def test_apply_skips_paraphrase_near_dupes(tmp_path: Path):
+    apply_result(
+        tmp_path,
+        ExtractionResult(
+            units=[
+                KnowledgeUnit(
+                    kind="dev",
+                    path=".",
+                    section="Pitfalls",
+                    content="- Redacting secrets before parsing breaks JSON — redact after parse",
+                    confidence="high",
+                )
+            ]
+        ),
+    )
+    changes = apply_result(
+        tmp_path,
+        ExtractionResult(
+            units=[
+                KnowledgeUnit(
+                    kind="dev",
+                    path=".",
+                    section="Pitfalls",
+                    content="- Redacting secrets before JSON parse corrupts the payload — run redaction after normalize parses units",
+                    confidence="high",
+                )
+            ]
+        ),
+    )
+    assert changes == []
+
+
 def test_apply_strips_placeholders(tmp_path: Path):
     p = tmp_path / "DEV.md"
     p.write_text(
```

## existing knowledge files

### DEV.md

## Pitfalls
- Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
- Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.## Patterns
- Eval notes live under docs/evals but knowledge should root

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

### USAGE.md

## Setup
- Create and activate Python virtual environment.
- Set `OPENROUTER_API_KEY` environment variable for live extraction.
- Optionally set `DEVMEMORY_ENV_FILE` for loading env vars.
- Run `./scripts/ensure-hermes.sh` to install Hermes CLI and verify setup.## Common commands
- pip install -e '.[dev]' to set up development environment.

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

