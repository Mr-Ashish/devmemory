#!/usr/bin/env bash
# Install devmemory as a Claude Code SessionEnd hook (project or user settings).
#
# Usage:
#   ./scripts/install-claude-hook.sh              # project .claude/settings.json
#   ./scripts/install-claude-hook.sh --user       # ~/.claude/settings.json
#   ./scripts/install-claude-hook.sh --repo /path
#   ./scripts/install-claude-hook.sh --with-stop  # also enable Stop (debounced)
#   ./scripts/install-claude-hook.sh --print      # print JSON fragment only
#
# One-liner (from repo root, after pip install -e .):
#   ./scripts/install-claude-hook.sh && echo "SessionEnd → devmemory dry-run"
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK_SCRIPT="$ROOT/scripts/claude-code-hook.sh"
TARGET="project"
REPO=""
WITH_STOP=0
PRINT_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) TARGET="user"; shift ;;
    --repo)
      REPO="$2"
      shift 2
      ;;
    --with-stop) WITH_STOP=1; shift ;;
    --print) PRINT_ONLY=1; shift ;;
    -h|--help)
      sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -x "$HOOK_SCRIPT" ]]; then
  chmod +x "$HOOK_SCRIPT" || true
fi
if [[ ! -f "$HOOK_SCRIPT" ]]; then
  echo "Missing hook script: $HOOK_SCRIPT" >&2
  exit 1
fi

if [[ -z "$REPO" ]]; then
  REPO="$(pwd)"
fi
REPO="$(cd "$REPO" && pwd)"

if [[ "$TARGET" == "user" ]]; then
  SETTINGS="${HOME}/.claude/settings.json"
else
  SETTINGS="$REPO/.claude/settings.json"
fi

export INSTALL_HOOK_SCRIPT="$HOOK_SCRIPT"
export INSTALL_SETTINGS="$SETTINGS"
export INSTALL_WITH_STOP="$WITH_STOP"
export INSTALL_PRINT_ONLY="$PRINT_ONLY"

python3 - <<'PY'
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

hook = Path(os.environ["INSTALL_HOOK_SCRIPT"]).resolve()
settings_path = Path(os.environ["INSTALL_SETTINGS"]).expanduser()
with_stop = os.environ.get("INSTALL_WITH_STOP") == "1"
print_only = os.environ.get("INSTALL_PRINT_ONLY") == "1"

# Absolute path so Claude Code can invoke regardless of cwd quirks.
cmd = str(hook)

session_end_entry = {
    "hooks": [
        {
            "type": "command",
            "command": cmd,
            "timeout": 30,
            "statusMessage": "devmemory extracting knowledge…",
        }
    ]
}
stop_entry = {
    "hooks": [
        {
            "type": "command",
            "command": f"DEVMEMORY_HOOK_ON_STOP=1 {cmd}",
            "timeout": 15,
            "statusMessage": "devmemory (stop)…",
        }
    ]
}

fragment = {"hooks": {"SessionEnd": [session_end_entry]}}
if with_stop:
    fragment["hooks"]["Stop"] = [stop_entry]

if print_only:
    print(json.dumps(fragment, indent=2))
    sys.exit(0)

settings_path.parent.mkdir(parents=True, exist_ok=True)
if settings_path.exists():
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {settings_path}: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict):
        print(f"{settings_path} root must be an object", file=sys.stderr)
        sys.exit(1)
else:
    data = {}

hooks = data.setdefault("hooks", {})
if not isinstance(hooks, dict):
    print(f"{settings_path}: hooks must be an object", file=sys.stderr)
    sys.exit(1)


def _command_of(entry: dict) -> str:
    for h in entry.get("hooks") or []:
        if isinstance(h, dict) and h.get("command"):
            return str(h["command"])
    return ""


def _merge_event(event: str, new_entry: dict) -> None:
    existing = hooks.get(event)
    if existing is None:
        hooks[event] = [new_entry]
        return
    if not isinstance(existing, list):
        hooks[event] = [new_entry]
        return
    new_cmd = _command_of(new_entry)
    # Replace prior devmemory hook entries; keep unrelated hooks.
    kept = []
    for item in existing:
        if not isinstance(item, dict):
            kept.append(item)
            continue
        cmd = _command_of(item)
        if "claude-code-hook.sh" in cmd or "devmemory" in cmd.lower() and "hook" in cmd.lower():
            continue
        # also drop exact same command path
        if new_cmd and cmd == new_cmd:
            continue
        if new_cmd and cmd.endswith("claude-code-hook.sh"):
            continue
        kept.append(item)
    kept.append(new_entry)
    hooks[event] = kept


_merge_event("SessionEnd", session_end_entry)
if with_stop:
    _merge_event("Stop", stop_entry)
else:
    # Do not remove user Stop hooks; only SessionEnd is required for R3.
    pass

text = json.dumps(data, indent=2) + "\n"
settings_path.write_text(text, encoding="utf-8")
print(f"installed SessionEnd hook → {settings_path}")
print(f"  command: {cmd}")
if with_stop:
    print("  also: Stop (DEVMEMORY_HOOK_ON_STOP=1, debounced)")
print("default: background dry-run extract; set DEVMEMORY_HOOK_APPLY=1 to write")
print("log: <repo>/.devmemory/hooks.log")
PY
