# Session

- **session_id:** `r75-hook-tool-edit-gate`
- **source:** `file`
- **project:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **timestamp:** ``

## Transcript / notes

Session: shipped hook tool-edit gate for devmemory SessionEnd.

Architecture:
- New module src/devmemory/hook_gate.py decides whether SessionEnd should run extract.
- scripts/claude-code-hook.sh calls should_run_extract_for_session before spawn.

Design decisions:
- Default DEVMEMORY_HOOK_REQUIRE_EDITS=1 so chat-only Claude sessions skip extract (no Hermes/offline noise).
- Missing transcript still allows extract (cannot prove chat-only without JSONL).
- DEVMEMORY_HOOK_FORCE=1 bypasses the gate; DEVMEMORY_HOOK_REQUIRE_EDITS=0 restores old always-run behavior.

Patterns:
- Edit-class tools: Write, Edit, MultiEdit, NotebookEdit, Create, str_replace, apply_patch, Delete.
- Detect via Claude tool_use content blocks or tool_complete traces; fast regex pre-scan on JSONL lines.
- Bash-only sessions are treated as non-edits (no durable code write signal).

Pitfalls:
- Do not treat every JSON "name" field as a tool — require tool_use type or tool event context.
- Never block Claude: gate failures / import errors allow extract; hook always exit 0.

Commands:
- export DEVMEMORY_HOOK_REQUIRE_EDITS=0   # allow chat-only
- Check .devmemory/hooks.log for "skip: no tool edits" vs "gate: tool_edits_present"
- pytest tests/test_hook_gate.py -q

