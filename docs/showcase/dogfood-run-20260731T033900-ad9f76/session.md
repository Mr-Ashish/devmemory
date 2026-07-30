# Session

- **session_id:** `r8-watch-ship`
- **source:** `file`
- **project:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **timestamp:** ``

## Transcript / notes

Session: shipped R8 devmemory watch.

Architecture:
- New module src/devmemory/watch.py polls Claude sessions for the repo cwd.
- State under .devmemory/watch.json tracks seen session fingerprints (id|timestamp|textlen).
- CLI: devmemory watch --once|--interval|--apply|--offline|--require-edits/--allow-chat|--json.

Design decisions:
- Watch is a backup when SessionEnd hook is not installed; default extract is dry-run.
- Tool-edit gate applies only to per-session project JSONL transcripts, not shared history.jsonl (scanning history would false-skip every row).
- max_extracts per cycle defaults to 3 to avoid stampeding Hermes.

Patterns:
- find_watch_candidates skips processed and already-seen fingerprints; mark_seen after extract or error to prevent poison loops.
- watch --once is the cron/tests entry; machine JSON summary line on stdout.

Commands:
- devmemory watch --once --offline --json
- devmemory watch --interval 120 --apply
- pytest tests/test_watch.py -q

Pitfalls:
- Do not pass multi-session history.jsonl into the tool-edit gate as if it were one transcript.
- Forever loop only when neither --once nor --max-polls; tests must use --once.

