```json
{
  "summary": "Session added a SessionEnd tool-edit gate: new src/devmemory/hook_gate.py consulted by scripts/claude-code-hook.sh, with an edit-class tool allowlist, JSONL tool_use detection, fail-open semantics, a DEVMEMORY_HOOK_FORCE bypass, and hooks.log markers for diagnosis. Existing knowledge only noted the gate's default-on behavior and the REQUIRE_EDITS=0 opt-out, so the module shape, detection rules and debug signals are new.",
  "session_ids": ["r75-hook-tool-edit-gate"],
  "units": [
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Architecture",
      "content": "- `hook_gate.py` owns the SessionEnd run/skip decision: `should_run_extract_for_session` is called by `scripts/claude-code-hook.sh` *before* it spawns the extract process, so a skipped session costs no Hermes/CLI startup.\n- `DEVMEMORY_HOOK_FORCE=1` short-circuits the gate entirely (always extract); `DEVMEMORY_HOOK_REQUIRE_EDITS=0` restores the pre-gate always-run behavior.",
      "evidence": [
        "New module src/devmemory/hook_gate.py decides whether SessionEnd should run extract",
        "scripts/claude-code-hook.sh calls should_run_extract_for_session before spawn",
        "DEVMEMORY_HOOK_FORCE=1 bypasses the gate"
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Patterns",
      "content": "- Edit-class tool allowlist for the hook gate: `Write`, `Edit`, `MultiEdit`, `NotebookEdit`, `Create`, `str_replace`, `apply_patch`, `Delete`.\n- Detection reads Claude `tool_use` content blocks or `tool_complete` traces, fronted by a fast regex pre-scan over JSONL lines so large transcripts are not fully parsed.\n- Bash-only sessions count as non-edits: shell activity is not treated as a durable code-write signal.",
      "evidence": [
        "Edit-class tools: Write, Edit, MultiEdit, NotebookEdit, Create, str_replace, apply_patch, Delete",
        "Detect via Claude tool_use content blocks or tool_complete traces; fast regex pre-scan on JSONL lines",
        "Bash-only sessions are treated as non-edits"
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Pitfalls",
      "content": "- Do not treat every JSON `name` field in a transcript as a tool invocation — require a `tool_use` type or surrounding tool-event context, or unrelated payload keys produce false edit signals.\n- The gate must never block Claude: gate exceptions and import errors fall through to *allow* extract, and the hook script always exits 0.",
      "evidence": [
        "Do not treat every JSON \"name\" field as a tool — require tool_use type or tool event context",
        "Never block Claude: gate failures / import errors allow extract; hook always exit 0"
      ],
      "confidence": "high"
    },
    {
      "kind": "usage",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Debugging",
      "content": "- Gate decisions are logged to `.devmemory/hooks.log`: `skip: no tool edits` means the gate suppressed the run, `gate: tool_edits_present` means it allowed one.\n- To force a run past the gate without changing config: `export DEVMEMORY_HOOK_FORCE=1`.\n- Gate unit tests: `pytest tests/test_hook_gate.py -q`.",
      "evidence": [
        "Check .devmemory/hooks.log for \"skip: no tool edits\" vs \"gate: tool_edits_present\"",
        "pytest tests/test_hook_gate.py -q",
        "DEVMEMORY_HOOK_FORCE=1 bypasses the gate"
      ],
      "confidence": "high"
    }
  ]
}
```
