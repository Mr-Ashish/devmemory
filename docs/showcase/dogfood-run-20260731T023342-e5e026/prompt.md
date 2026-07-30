# Task

Extract **durable repository knowledge** from the development session below.
You already have enough context below — **do not explore the filesystem**.
Respond with **only** the JSON object (fence optional).

## Output contract (mandatory)

```json
{
  "summary": "1-3 sentences: what durable knowledge was found",
  "session_ids": ["dogfood-build-narrative"],
  "units": [
    {
      "kind": "dev",
      "path": "src/auth",
      "action": "merge",
      "section": "Design decisions",
      "content": "- Bullet one\n- Bullet two",
      "evidence": ["short quote"],
      "confidence": "high"
    }
  ]
}
```

### Field rules
- `kind`: `"dev"` (architecture/decisions/patterns/pitfalls) or `"usage"` (commands/setup/debug)
- `path`: **must be one of the existing directories listed below** (or `"."`). Never invent paths.
  Prefer code modules under `src/`. **Never** use `tests/`, `docs/`, `fixtures/`, `assets/`, or `scripts/` as knowledge homes.
- `section`: **must** be one of:
  - DEV: `Architecture` | `Design decisions` | `Patterns` | `Pitfalls`
  - USAGE: `Setup` | `Common commands` | `Debugging` | `Troubleshooting`
- `content`: markdown bullets only; concrete and non-duplicative of existing knowledge
- `confidence`: `high` | `medium` | `low`
- Prefer 1–6 units. When both design and commands appear, emit **both** kinds.
- **No secrets**. Never copy tokens, keys, or `.env` values.

## Session
- **id:** `dogfood-build-narrative`
- **source:** `fixture`

### Transcript

We built and dogfooded the entire devmemory product in this repository itself — no external monorepo (no Odoo). Everything below is durable engineering knowledge from the build sessions.

## Architecture decisions

- Control plane mirrors Luffy (luffy-pr-review-agent): assemble → hermes -z → normalize → apply → human git review.
- Hermes Agent is a CLI dependency (not vendored). Inference is OpenRouter. Default model for dogfood quality: anthropic/claude-opus-5; iteration can use gpt-4.1-mini.
- hermes-agent-self-evolution is used for ideas (session importers, secret redaction patterns, later skill GEPA) — not required for the MVP runtime.
- Product knowledge lives as colocated DEV.md (how built) and USAGE.md (how to operate), not a single root brain dump.
- Runtime state lives under .devmemory/ (gitignored). Curated public traces live under docs/showcase/ after redaction.
- Apply layer is the product quality boundary: path snap to existing dirs, canonical H2 sections, bullet near-dupe skip, placeholder scrub. LLM proposes; merge decides.
- Default Hermes toolsets are empty for extract (pure reasoning over assembled context). Override DEVMEMORY_TOOLSETS=terminal only when needed.

## Module layout

- src/devmemory/cli.py — Click CLI
- src/devmemory/assemble.py — bounded context (no LLM)
- src/devmemory/extract.py — Hermes orchestration + timings + showcase flag
- src/devmemory/normalize.py — JSON units + redaction after parse
- src/devmemory/apply.py — merge into DEV.md/USAGE.md
- src/devmemory/paths.py — list_repo_dirs + resolve_unit_path
- src/devmemory/sections.py — canonicalize section titles
- src/devmemory/trace.py — redacted showcase packaging
- src/devmemory/sources/ — fixtures + Claude history/project
- agent/ — SOUL.md, config.yaml, extract-prompt.md for Hermes home seeding

## Patterns

- Frozen schemas via pydantic KnowledgeUnit / ExtractionResult.
- Only mark sessions processed when units > 0 (do not poison cursor on empty runs).
- Offline heuristic extract for CI without OpenRouter (path inference + command lines).
- Dogfood loop: improve product → run extract on self → update DEV/USAGE → capture showcase → push.

## Pitfalls

- Never commit .devmemory/ or raw transcripts or .env.
- Pre-parse secret redaction can break JSON — redact string fields after parse.
- Re-running without bullet dedupe thrashs docs — always near-dupe skip.
- Invented paths create junk trees — always snap to existing directories.
- Using terminal tools on extract slows and distracts the model from JSON contract.

## Commands that worked

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
export DEVMEMORY_ENV_FILE=/Users/ashishmishra/Documents/experiments/pr-review-agent/.env
export DEVMEMORY_MODEL=anthropic/claude-opus-5
./scripts/ensure-hermes.sh
./scripts/smoke-e2e.sh
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase
pytest -q
devmemory review
```

## Debug tips

- If hermes_rc != 0: check extract.raw.stderr and HERMES_HOME/.env mode 0600 + OPENROUTER_API_KEY.
- If units empty: inspect extract.raw.md for non-JSON; offline fallback should still produce units.
- If wrong path: ensure path appears in EXISTING_DIRS in assembled prompt and tree contains the module dir.
- Showcase privacy: trace.py redacts sk-or / Bearer / env assignments before writing docs/showcase/.

## Eval notes

- Unit tests cover redaction, normalize, apply dedupe, path snap, offline extract (target ≥19 tests).
- Live eval: smoke-hermes pong + fixture extract produces src/auth DEV/USAGE split with high confidence.
- Dogfood eval: self-extract improves root and package DEV.md without reintroducing _(none yet)_ placeholders.

## Existing directories (allowed `path` values)

```
.
agent
src
src/auth
src/devmemory
src/devmemory/sources
```

## Repository snapshot

### git status
```
M src/devmemory/cli.py
 M src/devmemory/sources/__init__.py
 M src/devmemory/sources/claude.py
?? tests/test_claude_discovery.py
```

### recent log
```
3e0ebb3 Dogfood iter3: paraphrase near-dupe and assemble allowed-dir filter
3e2b3dd Dogfood loop: scrub empty H2s and block knowledge under tests/docs
a3dfefc Include redacted Hermes agent.log in dogfood showcase
2016aee Dogfood Opus 5 self-extract with traces, showcase, brand, and docs
d5f78f4 Implement devmemory MVP with high-ROI knowledge quality fixes
```

### tree (sample)
```
DEV.md
PLAN.md
README.md
USAGE.md
pyproject.toml
tests/test_apply.py
tests/test_claude_discovery.py
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

### git diff
```
diff --git a/src/devmemory/cli.py b/src/devmemory/cli.py
index 26ccb38..ce8e06b 100644
--- a/src/devmemory/cli.py
+++ b/src/devmemory/cli.py
@@ -15,7 +15,7 @@ from devmemory import __version__
 from devmemory.apply import apply_result
 from devmemory.extract import extract_session, package_root
 from devmemory.normalize import normalize_extraction
-from devmemory.sources.claude import discover_claude_sessions
+from devmemory.sources.claude import discover_claude_sessions, pick_latest_unprocessed
 from devmemory.sources.fixtures import FixtureSource
 from devmemory.sources.base import SessionRecord
 from devmemory.state import DevMemoryPaths
@@ -65,25 +65,28 @@ def _resolve_session(
             raise click.ClickException(f"Fixture not found: {fixture}")
         return s
     if session_id:
-        # search fixtures then claude
+        # search Claude first (real sessions), then fixtures
+        for cand in discover_claude_sessions(repo, limit=200):
+            if cand.session_id == session_id:
+                return cand
         src = FixtureSource(_fixtures_dir())
         s = src.get(session_id)
         if s:
             return s
-        for cand in discover_claude_sessions(repo, limit=200):
-            if cand.session_id == session_id:
-                return cand
         raise click.ClickException(f"Session not found: {session_id}")
-    # default: first unprocessed fixture or claude session
+    # default: latest unprocessed *real* Claude session for cwd, then fixtures
     paths = DevMemoryPaths.for_repo(repo)
     paths.ensure()
+    claude = discover_claude_sessions(repo, limit=50)
+    picked = pick_latest_unprocessed(claude, is_processed=paths.is_processed)
+    if picked is not None:
+        return picked
     for s in FixtureSource(_fixtures_dir()).list_sessions():
         if not paths.is_processed(s.session_id):
             return s
-    for s in discover_claude_sessions(repo, limit=50):
-        if not paths.is_processed(s.session_id):
-            return s
-    # fall back to first fixture even if processed
+    # fall back: newest Claude even if processed, else first fixture
+    if claude:
+        return claude[0]
     fixtures = FixtureSource(_fixtures_dir()).list_sessions()
     if fixtures:
         return fixtures[0]
@@ -139,18 +142,20 @@ def init_cmd(repo: str | None) -> None:
 @click.option("--claude/--no-claude", default=True)
 @click.option("--limit", default=30, show_default=True)
 def list_sessions(repo: str | None, fixtures: bool, claude: bool, limit: int) -> None:
-    """List discoverable sessions for a repo."""
+    """List discoverable sessions for a repo (Claude first, then fixtures)."""
     root = _repo_path(repo)
     rows: list[SessionRecord] = []
-    if fixtures:
-        rows.extend(FixtureSource(_fixtures_dir()).list_sessions(limit=limit))
+    # Real Claude sessions for cwd first (R1), then package fixtures
     if claude:
         rows.extend(discover_claude_sessions(root, limit=limit))
+    if fixtures:
+        rows.extend(FixtureSource(_fixtures_dir()).list_sessions(limit=limit))
     paths = DevMemoryPaths.for_repo(root)
     table = Table(title=f"Sessions for {root.name}")
     table.add_column("id")
     table.add_column("source")
     table.add_column("processed")
+    table.add_column("turns")
     table.add_column("preview")
     seen = set()
     for s in rows:
@@ -158,10 +163,20 @@ def list_sessions(repo: str | None, fixtures: bool, claude: bool, limit: int) ->
             continue
         seen.add(s.session_id)
         proc = "yes" if paths.is_processed(s.session_id) else "no"
-        table.add_row(s.session_id[:40], s.source, proc, s.preview(60))
+        turns = str((s.meta or {}).get("turns") or "")
+        table.add_row(s.session_id[:40], s.source, proc, turns, s.preview(60))
         if len(seen) >= limit:
             break
     console.print(table)
+    n_claude = sum(1 for s in rows if s.source.startswith("claude"))
+    n_unproc = sum(
+        1
+        for s in rows
+        if s.source.startswith("claude") and not paths.is_processed(s.session_id)
+    )
+    console.print(
+        f"[dim]claude={n_claude} unprocessed_claude={n_unproc} shown={min(len(seen), limit)}[/dim]"
+    )
 
 
 @main.command("status")
diff --git a/src/devmemory/sources/__init__.py b/src/devmemory/sources/__init__.py
index 8821400..a7a37c8 100644
--- a/src/devmemory/sources/__init__.py
+++ b/src/devmemory/sources/__init__.py
@@ -1,7 +1,12 @@
 """Session sources for knowledge extraction."""
 
 from .base import SessionRecord
-from .claude import ClaudeHistorySource, ClaudeProjectSource, discover_claude_sessions
+from .claude import (
+    ClaudeHistorySource,
+    ClaudeProjectSource,
+    discover_claude_sessions,
+    pick_latest_unprocessed,
+)
 from .fixtures import FixtureSource
 
 __all__ = [
@@ -10,4 +15,5 @@ __all__ = [
     "ClaudeProjectSource",
     "FixtureSource",
     "discover_claude_sessions",
+    "pick_latest_unprocessed",
 ]
diff --git a/src/devmemory/sources/claude.py b/src/devmemory/sources/claude.py
index 56c67bf..c8976a3 100644
--- a/src/devmemory/sources/claude.py
+++ b/src/devmemory/sources/claude.py
@@ -1,33 +1,83 @@
 """Claude Code session importers.
 
-- history.jsonl: flat user prompts (~/.claude/history.jsonl)
-- project jsonl: full sessions when present (~/.claude/projects/<id>/*.jsonl)
+- history.jsonl: flat user prompts (~/.claude/history.jsonl), grouped by sessionId
+- project jsonl: full sessions when present (~/.claude/projects/<encoded-path>/*.jsonl)
+
+Override paths with DEVMEMORY_CLAUDE_HISTORY / DEVMEMORY_CLAUDE_PROJECTS for tests.
 """
 
 from __future__ import annotations
 
 import json
+import os
+from collections import defaultdict
 from pathlib import Path
-from typing import Iterable
 
 from devmemory.redaction import contains_secret, redact
 from devmemory.sources.base import SessionRecord
 
 
 def _default_history() -> Path:
+    env = os.environ.get("DEVMEMORY_CLAUDE_HISTORY", "").strip()
+    if env:
+        return Path(env).expanduser()
     return Path.home() / ".claude" / "history.jsonl"
 
 
 def _default_projects() -> Path:
+    env = os.environ.get("DEVMEMORY_CLAUDE_PROJECTS", "").strip()
+    if env:
+        return Path(env).expanduser()
     return Path.home() / ".claude" / "projects"
 
 
-def _encode_project_path(repo_root: Path) -> str:
-    # Claude encodes absolute paths: /Users/foo/bar -> -Users-foo-bar
+def encode_project_path(repo_root: Path) -> str:
+    """Claude encodes absolute paths: /Users/foo/bar -> -Users-foo-bar."""
     abs_path = str(repo_root.resolve())
     return abs_path.replace("/", "-")
 
 
+# Back-compat alias used elsewhere / tests
+_encode_project_path = encode_project_path
+
+
+def project_matches_repo(project: str, repo_root: Path) -> bool:
+    """True when a Claude history/project path is relevant to repo_root (cwd).
+
+    Matches:
+    - exact absolute path of the repo
+    - sessions started in a subdirectory of the repo
+    """
+    if not project:
+        return False
+    root_n = str(repo_root.resolve()).rstrip("/")
+    proj = str(project).rstrip("/")
+    if proj == root_n:
+        return True
+    # session started inside the repo tree
+    if proj.startswith(root_n + "/"):
+        return True
+    return False
+
+
+def _ts_sort_key(ts: str | float | int) -> float:
+    """Normalize to unix seconds (Claude history often uses epoch ms)."""
+    if isinstance(ts, (int, float)):
+        val = float(ts)
+    else:
+        s = str(ts).strip()
+        if not s:
+            return 0.0
+        try:
+            val = float(s)
+        except ValueError:
+            return 0.0
+    # epoch milliseconds → seconds
+    if val > 1_000_000_000_000:  # ~2001-09 in ms
+        val = val / 1000.0
+    return val
+
+
 class ClaudeHistorySource:
     def __init__(self, history_path: Path | None = None) -> None:
         self.history_path = history_path or _default_history()
@@ -36,11 +86,16 @@ class ClaudeHistorySource:
         self,
         *,
         project_filter: str | None = None,
+        repo_root: Path | None = None,
         limit: int = 0,
     ) -> list[SessionRecord]:
+        """List sessions grouped by sessionId (multi-turn history → one record)."""
         if not self.history_path.exists():
             return []
-        out: list[SessionRecord] = []
+
+        # session_id -> list of (timestamp, text, project, raw_keys)
+        buckets: dict[str, list[tuple[float | str, str, str, list]]] = defaultdict(list)
+
         with self.history_path.open(encoding="utf-8", errors="replace") as f:
             for line in f:
                 if not line.strip():
@@ -50,31 +105,55 @@ class ClaudeHistorySource:
                 except json.JSONDecodeError:
                     continue
                 text = entry.get("display") or entry.get("text") or ""
-                if not text or len(text.strip()) < 10:
+                if not isinstance(text, str) or len(text.strip()) < 10:
                     continue
                 if contains_secret(text):
                     text = redact(text)
                 project = entry.get("project") or ""
-                if project_filter and project_filter not in project:
+                if not isinstance(project, str):
+                    project = str(project)
+
+                if repo_root is not None:
+                    if not project_matches_repo(project, repo_root):
+                        continue
+                elif project_filter and project_filter not in project:
                     continue
+
                 sid = str(entry.get("sessionId") or entry.get("session_id") or "")
+                ts = entry.get("timestamp", "")
                 if not sid:
-                    # synthesize stable id from project+timestamp+hash of text head
-                    ts = entry.get("timestamp", "")
                     sid = f"history-{ts}-{abs(hash(text[:80])) % 10_000_000}"
-                out.append(
-                    SessionRecord(
-                        session_id=sid,
-                        source="claude-history",
-                        project=project,
-                        timestamp=entry.get("timestamp", ""),
-                        text=text.strip(),
-                        path=self.history_path,
-                        meta={"raw_keys": list(entry.keys())},
-                    )
+
+                buckets[sid].append((ts, text.strip(), project, list(entry.keys())))
+
+        out: list[SessionRecord] = []
+        for sid, parts in buckets.items():
+            # chronological within session
+            parts_sorted = sorted(parts, key=lambda p: _ts_sort_key(p[0]))
+            texts = [p[1] for p in parts_sorted]
+            body = "\n\n".join(texts)
+            if len(body.strip()) < 10:
+                continue
+            last_ts = parts_sorted[-1][0]
+            project = parts_sorted[-1][2]
+            out.append(
+                SessionRecord(
+                    session_id=sid,
+                    source="claude-history",
+                    project=project,
+                    timestamp=last_ts,
+                    text=body,
+                    path=self.history_path,
+                    meta={
+                        "turns": len(parts_sorted),
+                        "raw_keys": parts_sorted[-1][3],
+                    },
                 )
-                if limit and len(out) >= limit:
-                    break
+            )
+
+        out.sort(key=lambda s: _ts_sort_key(s.timestamp), reverse=True)
+        if limit:
+            return out[:limit]
         return out
 
 
@@ -90,31 +169,51 @@ class ClaudeProjectSource:
     ) -> list[SessionRecord]:
         if not self.projects_dir.exists():
             return []
-        encoded = _encode_project_path(repo_root)
-        # exact or partial match (path suffixes)
-        candidates = [
-            d
-            for d in self.projects_dir.iterdir()
-            if d.is_dir() and (d.name == encoded or encoded.endswith(d.name) or d.name.endswith(encoded[-40:]))
-        ]
-        # also try any dir whose name contains the repo folder name
+        encoded = encode_project_path(repo_root)
         repo_name = repo_root.name
-        if not candidates:
-            candidates = [
-                d
-                for d in self.projects_dir.iterdir()
-                if d.is_dir() and repo_name in d.name
-            ]
-        out: list[SessionRecord] = []
+        candidates: list[Path] = []
+        for d in self.projects_dir.iterdir():
+            if not d.is_dir():
+                continue
+            name = d.name
+            if name == encoded:
+                candidates.append(d)
+                continue
+            # partial: encoded path contains this dir name or vice versa
+            if encoded.endswith(name) or name.endswith(encoded[-min(40, len(encoded)) :]):
+                candidates.append(d)
+                continue
+            # decode-ish: dir name contains repo folder and a slice of parent
+            if repo_name in name and "Users" in name:
+                # prefer dirs that look like this absolute path
+                if encoded in name or name in encoded or repo_name == name.split("-")[-1]:
+                    candidates.append(d)
+
+        # de-dupe while preserving order
+        seen_dirs: set[Path] = set()
+        uniq: list[Path] = []
         for d in candidates:
+            rp = d.resolve()
+            if rp not in seen_dirs:
+                seen_dirs.add(rp)
+                uniq.append(d)
+
+        out: list[SessionRecord] = []
+        for d in uniq:
             out.extend(self._read_project_dir(d, limit=0))
             if limit and len(out) >= limit:
-                return out[:limit]
+                break
+        out.sort(key=lambda s: _ts_sort_key(s.timestamp), reverse=True)
         return out[:limit] if limit else out
 
     def _read_project_dir(self, project_dir: Path, *, limit: int) -> list[SessionRecord]:
         out: list[SessionRecord] = []
-        for jsonl in sorted(project_dir.glob("*.jsonl")):
+        jsonl_files = sorted(
+            project_dir.glob("*.jsonl"),
+            key=lambda p: p.stat().st_mtime,
+            reverse=True,
+        )
+        for jsonl in jsonl_files:
             text_parts: list[str] = []
             with jsonl.open(encoding="utf-8", errors="replace") as f:
                 for line in f:
@@ -142,6 +241,7 @@ class ClaudeProjectSource:
                     timestamp=jsonl.stat().st_mtime,
                     text=body,
                     path=jsonl,
+                    meta={"turns": len(text_parts), "project_dir": str(project_dir)},
                 )
             )
             if limit and len(out) >= limit:
@@ -159,7 +259,6 @@ def _extract_message_text(entry: dict) -> str:
         text = _content_to_text(content)
         if text:
             return f"[{role or t}] {text}"
-    # some lines store text directly
     for key in ("text", "content", "display", "summary"):
         v = entry.get(key)
         if isinstance(v, str) and v.strip():
@@ -197,19 +296,14 @@ def discover_claude_sessions(
     projects_dir: Path | None = None,
     limit: int = 50,
 ) -> list[SessionRecord]:
-    """Discover sessions relevant to repo_root (history + project files)."""
+    """Discover sessions relevant to repo_root (project JSONL + history).
+
+    Project sessions (richer multi-role transcripts) are preferred when both
+    sources share a session id. Results are newest-first.
+    """
     root = repo_root.resolve()
-    root_str = str(root)
     hist = ClaudeHistorySource(history_path)
-    # filter history entries whose project path matches this repo
-    history = hist.list_sessions(project_filter=root_str, limit=0)
-    if not history:
-        # softer match: repo name in project path
-        history = [
-            s
-            for s in hist.list_sessions(limit=0)
-            if root.name in (s.project or "") or root_str in (s.project or "")
-        ]
+    history = hist.list_sessions(repo_root=root, limit=0)
     projects = ClaudeProjectSource(projects_dir).list_for_repo(root, limit=0)
 
     # Prefer project sessions (richer); append history-only ids not already covered
@@ -220,9 +314,18 @@ def discover_claude_sessions(
             continue
         seen.add(s.session_id)
         merged.append(s)
-    # newest first when timestamps comparable
-    def sort_key(s: SessionRecord):
-        return str(s.timestamp)
 
-    merged.sort(key=sort_key, reverse=True)
+    merged.sort(key=lambda s: _ts_sort_key(s.timestamp), reverse=True)
     return merged[:limit] if limit else merged
+
+
+def pick_latest_unprocessed(
+    sessions: list[SessionRecord],
+    *,
+    is_processed,
+) -> SessionRecord | None:
+    """Return newest unprocessed session, or None."""
+    for s in sessions:
+        if not is_processed(s.session_id):
+            return s
+    return None
```

### existing knowledge (do not repeat these bullets)
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

## Troubleshooting
- Context size is tunable via env: `DEVMEMORY_MAX_SESSION_CHARS` (24000), `DEVMEMORY_MAX_DIFF_CHARS` (40000), `DEVMEMORY_MAX_TREE_LINES` (200), `DEVMEMORY_MAX_KNOWLEDGE_CHARS` (1600). Raise these only when the model is clearly missing evidence — larger prompts increase restatement.
- Unit landed under the wrong directory: confirm the target appears in the `EXISTING_DIRS` block of the assembled prompt and that the module dir shows up in the tree sample; blocked trees are filtered out on purpose and will never be accepted.
- Docs growing on every run: verify near-dupe skipping is active (`apply.dedupe_section_bullets` / `scrub_file_near_dupes`) rather than editing the docs by hand.
- Before publishing a run, remember `trace.py` redacts `sk-or` / `Bearer` tokens and env assignments on the way into `docs/showcase/` — never copy files there manually.


## Final instruction
Return the JSON object now. If nothing durable is present, return `"units": []`.
