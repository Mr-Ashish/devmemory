# DEV — engineering knowledge

> How this part of the system is built.

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
- `encode_project_path` (public; `_encode_project_path` kept as a back-compat alias) implements Claude's `/Users/foo/bar -> -Users-foo-bar` encoding, and project-dir matching layers exact match, encoded-suffix match, then a `repo_name` + `Users` heuristic — de-duped by resolved path.
- Within a project dir, `*.jsonl` files are read newest-mtime-first rather than in name order.

## Pitfalls

- Claude timestamps are mixed types: history often uses epoch **milliseconds** while project records use file mtime seconds. Always sort through `_ts_sort_key`, which coerces str/int/float and divides by 1000 when the value exceeds 1_000_000_000_000 — sorting on `str(timestamp)` (the old behaviour) mis-orders sessions.
- Never assume `display`/`text`/`project` are strings; malformed lines are guarded with `isinstance` checks and coerced/skipped rather than allowed to raise mid-scan.
- Secret redaction happens per history line at import time (`contains_secret` → `redact`) before the text is ever bucketed into a record.
- A session bucket can still be too small after joining turns; drop it when the joined body is under 10 chars instead of emitting an empty record.
