# Repository context

- **root:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **assembled_at:** 2026-07-30T20:47:37Z

## git status

```
M src/devmemory/cli.py
 M src/devmemory/extract.py
?? fixtures/sessions/dogfood-build-narrative.json
?? src/devmemory/trace.py
```

## recent log

```
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
scripts/ensure-hermes.sh
scripts/load-env.sh
scripts/smoke-e2e.sh
scripts/smoke-hermes.sh
fixtures/sessions/dogfood-build-narrative.json
fixtures/sessions/sample-auth-module.json
fixtures/sessions/sample-cli-pipeline.json
src/auth/DEV.md
src/auth/USAGE.md
src/devmemory/DEV.md
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
diff --git a/src/devmemory/cli.py b/src/devmemory/cli.py
index a38fd71..26ccb38 100644
--- a/src/devmemory/cli.py
+++ b/src/devmemory/cli.py
@@ -191,7 +191,18 @@ def status_cmd(repo: str | None) -> None:
 @click.option("--apply/--no-apply", default=False, help="Write DEV.md/USAGE.md")
 @click.option("--offline/--live", default=False, help="Heuristic extract without Hermes")
 @click.option("--force", is_flag=True, help="Re-process already processed session")
-@click.option("--model", default=None, help="OpenRouter model id")
+@click.option("--model", default=None, help="OpenRouter model id (default: opus-5)")
+@click.option(
+    "--showcase/--no-showcase",
+    default=False,
+    help="Write redacted docs/showcase package for README",
+)
+@click.option(
+    "--showcase-dir",
+    type=click.Path(path_type=Path),
+    default=None,
+    help="Custom showcase output directory",
+)
 def extract_cmd(
     repo: str | None,
     session_id: str | None,
@@ -201,6 +212,8 @@ def extract_cmd(
     offline: bool,
     force: bool,
     model: str | None,
+    showcase: bool,
+    showcase_dir: Path | None,
 ) -> None:
     """Extract durable knowledge from a session."""
     root = _repo_path(repo)
@@ -211,6 +224,11 @@ def extract_cmd(
         f"[bold]extract[/bold] session={session.session_id} source={session.source} "
         f"apply={apply} offline={offline}"
     )
+    show: bool | Path | None = False
+    if showcase_dir is not None:
+        show = showcase_dir
+    elif showcase:
+        show = True
     try:
         outcome = extract_session(
             root,
@@ -219,6 +237,7 @@ def extract_cmd(
             offline=offline,
             model=model,
             force=force,
+            showcase=show,
         )
     except RuntimeError as e:
         raise click.ClickException(str(e)) from e
@@ -228,6 +247,8 @@ def extract_cmd(
     console.print(f"  model: {outcome.model} hermes_rc={outcome.hermes_rc}")
     console.print(f"  units: {len(outcome.result.units)}")
     console.print(f"  summary: {outcome.result.summary or '(none)'}")
+    if outcome.timings:
+        console.print(f"  timings: {outcome.timings}")
     for u in outcome.result.units:
         console.print(
             f"  - [{u.confidence}] {u.kind} path={u.path!r} section={u.section!r}"
@@ -240,6 +261,8 @@ def extract_cmd(
             except ValueError:
                 rel = c.path
             console.print(f"  - {rel} ({c.kind}/{c.action})")
+    if outcome.showcase_dir:
+        console.print(f"[green]showcase[/green] {outcome.showcase_dir}")
     # machine-readable last line for scripts
     print(
         json.dumps(
@@ -250,6 +273,8 @@ def extract_cmd(
                 "changes": len(outcome.changes),
                 "model": outcome.model,
                 "hermes_rc": outcome.hermes_rc,
+                "timings": outcome.timings,
+                "showcase": str(outcome.showcase_dir) if outcome.showcase_dir else None,
             }
         )
     )
diff --git a/src/devmemory/extract.py b/src/devmemory/extract.py
index fccd4a4..e8b4441 100644
--- a/src/devmemory/extract.py
+++ b/src/devmemory/extract.py
@@ -19,6 +19,7 @@ from devmemory.paths import infer_paths_from_text, list_repo_dirs
 from devmemory.schema import ExtractionResult
 from devmemory.sources.base import SessionRecord
 from devmemory.state import DevMemoryPaths, RunContext, utc_now
+from devmemory.trace import package_showcase
 
 _CMD_LINE = re.compile(
     r"(?m)^\s*(?:[-*]\s*)?(?:`)?((?:pytest|pip|uv|npm|pnpm|yarn|cargo|go|make|docker|"
@@ -38,6 +39,8 @@ class ExtractOutcome:
     changes: list[ApplyChange]
     hermes_rc: int
     model: str
+    timings: dict | None = None
+    showcase_dir: Path | None = None
 
 
 def package_root() -> Path:
@@ -150,6 +153,8 @@ def run_hermes_extract(
     env["HERMES_HOME"] = str(hermes_home)
     env["OPENROUTER_API_KEY"] = ensure_openrouter_key()
     env["PYTHONUNBUFFERED"] = "1"
+    # Verbose agent logging for dogfood traces
+    env["HERMES_TUI_TOOL_PROGRESS"] = env.get("HERMES_TUI_TOOL_PROGRESS", "verbose")
     path_extra = f"{Path.home() / '.local' / 'bin'}:{Path.home() / '.hermes' / 'bin'}"
     env["PATH"] = f"{path_extra}:{env.get('PATH', '')}"
 
@@ -316,6 +321,7 @@ def extract_session(
     model: str | None = None,
     skip_processed: bool = True,
     force: bool = False,
+    showcase: bool | Path | None = None,
 ) -> ExtractOutcome:
     paths = DevMemoryPaths.for_repo(repo_root)
     paths.ensure()
@@ -324,25 +330,41 @@ def extract_session(
             f"session {session.session_id} already processed (use --force to re-run)"
         )
 
+    t0 = time.perf_counter()
+    timings: dict[str, float] = {}
     run_id = f"run-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
     ctx = RunContext(paths=paths, run_id=run_id)
     pkg = package_root()
     prompt_template = load_prompt_template(pkg)
+
+    t_a = time.perf_counter()
     prompt_path = assemble(ctx, session, prompt_template=prompt_template)
+    timings["assemble_s"] = round(time.perf_counter() - t_a, 3)
 
-    model = model or os.environ.get("DEVMEMORY_MODEL") or "openai/gpt-4.1-mini"
+    model = (
+        model
+        or os.environ.get("DEVMEMORY_MODEL")
+        or "anthropic/claude-opus-5"
+    )
     raw_path = ctx.run_dir / "extract.raw.md"
     usage_file = ctx.run_dir / "hermes-usage.json"
     units_path = ctx.run_dir / "units.json"
     hermes_rc = 0
+    log_offset = 0
 
     if offline or os.environ.get("DEVMEMORY_OFFLINE") == "1":
+        t_e = time.perf_counter()
         result = offline_extract(session, repo_root)
         raw_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
         hermes_rc = 0
         model = "offline"
+        timings["extract_s"] = round(time.perf_counter() - t_e, 3)
     else:
         seed_hermes_home(paths.hermes_home, pkg)
+        log_file = paths.hermes_home / "logs" / "agent.log"
+        if log_file.exists():
+            log_offset = log_file.stat().st_size
+        t_e = time.perf_counter()
         hermes_rc = run_hermes_extract(
             prompt_path=prompt_path,
             workspace=repo_root,
@@ -351,17 +373,20 @@ def extract_session(
             usage_file=usage_file,
             model=model,
         )
+        timings["extract_s"] = round(time.perf_counter() - t_e, 3)
         raw_text = (
             raw_path.read_text(encoding="utf-8", errors="replace")
             if raw_path.exists()
             else ""
         )
+        t_n = time.perf_counter()
         result = normalize_extraction(
             raw_text,
             session_ids=[session.session_id],
             model=model,
             raw_path=str(raw_path),
         )
+        timings["normalize_s"] = round(time.perf_counter() - t_n, 3)
         # Fallback only when Hermes hard-failed or returned unparseable empty
         if not result.units:
             result = offline_extract(session, repo_root)
@@ -372,13 +397,16 @@ def extract_session(
         f"# Run {run_id}\n\n- session: `{session.session_id}`\n"
         f"- model: `{model}`\n- hermes_rc: {hermes_rc}\n"
         f"- units: {len(result.units)}\n- summary: {result.summary}\n"
-        f"- at: {utc_now()}\n",
+        f"- at: {utc_now()}\n"
+        f"- timings: {json.dumps(timings)}\n",
         encoding="utf-8",
     )
 
     changes: list[ApplyChange] = []
     if apply:
+        t_p = time.perf_counter()
         changes = apply_result(repo_root, result)
+        timings["apply_s"] = round(time.perf_counter() - t_p, 3)
         (ctx.run_dir / "apply.json").write_text(
             json.dumps(
                 [
@@ -397,6 +425,11 @@ def extract_session(
             encoding="utf-8",
         )
 
+    timings["total_s"] = round(time.perf_counter() - t0, 3)
+    (ctx.run_dir / "timings.json").write_text(
+        json.dumps(timings, indent=2) + "\n", encoding="utf-8"
+    )
+
     # Only mark processed when we extracted something durable (avoid poisoning the cursor)
     if result.units:
         paths.mark_processed(
@@ -406,6 +439,29 @@ def extract_session(
             summary=result.summary,
         )
 
+    showcase_dir: Path | None = None
+    if showcase:
+        if showcase is True:
+            showcase_dir = (
+                package_root()
+                / "docs"
+                / "showcase"
+                / f"dogfood-{run_id}"
+            )
+        else:
+            showcase_dir = Path(showcase)
+        package_showcase(
+            ctx.run_dir,
+            showcase_dir,
+            hermes_home=paths.hermes_home,
+            log_offset=log_offset,
+            model=model,
+            hermes_rc=hermes_rc,
+            units=len(result.units),
+            summary=result.summary,
+            timings=timings,
+        )
+
     return ExtractOutcome(
         run_id=run_id,
         run_dir=ctx.run_dir,
@@ -413,4 +469,6 @@ def extract_session(
         changes=changes,
         hermes_rc=hermes_rc,
         model=model,
+        timings=timings,
+        showcase_dir=showcase_dir,
     )
```

## existing knowledge files

### DEV.md

# DEV — engineering knowledge

> How this part of the system is built.

## Architecture

## Design decisions

## Patterns

## Pitfalls
- Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
- Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.


### src/auth/DEV.md

# DEV — engineering knowledge

> How this part of the system is built.

## Architecture

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

## Design decisions

- Extraction pipeline stages: assemble → hermes extract → normalize → apply.
- Hermes is used as a CLI dependency (hermes -z), not included as vendored source.
- OpenRouter serves as the LLM provider for extraction.
- Knowledge extraction operates entirely locally with transcripts never leaving the developer's machine.
- Knowledge files (DEV.md and USAGE.md) are maintained colocated next to code modules to keep documentation context-specific and easily accessible.
- The process avoids committing raw AI session transcripts or .devmemory/ run artifacts to source control.
- Extraction pipeline inputs include Claude Code session transcripts, current repository code changes, and outputs knowledge merged into local DEV.md and USAGE.md files.
- CI workflows validate the consistency and freshness of generated knowledge files without requiring access to local transcripts.

## Patterns

- Knowledge extraction pipeline runs as 4 separate phases: assemble context, extract knowledge using Hermes CLI call, normalize JSON output, then apply merged changes.
- Localized knowledge files (DEV.md for engineering details, USAGE.md for operational instructions) live next to code modules to provide context-targeted documentation.
- DEV.md captures architecture, design decisions, patterns, pitfalls, and module-specific engineering context.
- USAGE.md captures setup steps, commands, debugging, troubleshooting, and workflows essential for working with the code part.
- Extraction process keeps knowledge generation as an automatic by-product of development sessions.

## Pitfalls


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

## Debugging

## Troubleshooting


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

## Troubleshooting


