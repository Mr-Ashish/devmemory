#!/usr/bin/env bash
# Claude Code hook for devmemory.
#
# Wire via SessionEnd (recommended) or Stop. Always exits 0 so Claude is never
# blocked. Default: background dry-run extract of the session (or latest
# unprocessed for cwd). Never commits secrets; never touches .env.
#
# Env (all optional):
#   DEVMEMORY_HOOK_APPLY=1       write DEV.md/USAGE.md (default: dry-run)
#   DEVMEMORY_HOOK_OFFLINE=1     heuristic extract (no Hermes/OpenRouter)
#   DEVMEMORY_HOOK_BG=0          run foreground (default: background)
#   DEVMEMORY_HOOK_ON_STOP=1     allow Stop events (default: SessionEnd only)
#   DEVMEMORY_HOOK_DEBOUNCE_S=N  min seconds between runs per session (default 120)
#   DEVMEMORY_HOOK_FORCE=1       pass --force (re-process)
#   DEVMEMORY_HOOK_MODEL=...     model override
#   DEVMEMORY_ENV_FILE=...       load OpenRouter key
#   DEVMEMORY_BIN=...            path to devmemory executable
#
# Stdin: Claude Code hook JSON (session_id, cwd, hook_event_name, ...).
set -u

_log() {
  local msg="$1"
  local log_file="${DEVMEMORY_HOOK_LOG:-}"
  if [[ -n "$log_file" ]]; then
    mkdir -p "$(dirname "$log_file")" 2>/dev/null || true
    printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$msg" >>"$log_file" 2>/dev/null || true
  fi
  # stderr only when foreground / debug — never pollute hook protocol stdout
  if [[ "${DEVMEMORY_HOOK_VERBOSE:-0}" == "1" ]]; then
    printf 'devmemory-hook: %s\n' "$msg" >&2
  fi
}

# Always exit 0 for Claude Code (do not block Stop / SessionEnd).
_finish() {
  exit 0
}
trap _finish EXIT

INPUT="$(cat || true)"
if [[ -z "${INPUT//[[:space:]]/}" ]]; then
  _log "skip: empty stdin"
  exit 0
fi

# Parse hook payload with Python (no jq dependency).
eval "$(
  DEVMEMORY_HOOK_JSON="$INPUT" python3 - <<'PY'
import json, os, shlex, sys

raw = os.environ.get("DEVMEMORY_HOOK_JSON", "")
try:
    data = json.loads(raw) if raw.strip() else {}
except json.JSONDecodeError:
    data = {}

def emit(k, v):
    if v is None:
        v = ""
    print(f"export {k}={shlex.quote(str(v))}")

event = (
    data.get("hook_event_name")
    or data.get("hookEventName")
    or os.environ.get("CLAUDE_HOOK_EVENT", "")
    or ""
)
emit("HOOK_EVENT", event)
emit("HOOK_SESSION_ID", data.get("session_id") or data.get("sessionId") or "")
emit("HOOK_CWD", data.get("cwd") or data.get("cwd_path") or os.getcwd())
emit("HOOK_TRANSCRIPT", data.get("transcript_path") or data.get("transcriptPath") or "")
stop_active = data.get("stop_hook_active")
if stop_active is None:
    stop_active = data.get("stopHookActive")
emit("HOOK_STOP_ACTIVE", "1" if stop_active else "0")
# reason for SessionEnd matcher values
emit("HOOK_REASON", data.get("reason") or data.get("session_end_reason") or "")
PY
)"

# Resolve paths
REPO="${HOOK_CWD:-$(pwd)}"
REPO="$(cd "$REPO" 2>/dev/null && pwd || echo "$REPO")"

# Prefer repo-local hook log under .devmemory (gitignored)
if [[ -z "${DEVMEMORY_HOOK_LOG:-}" ]]; then
  DEVMEMORY_HOOK_LOG="$REPO/.devmemory/hooks.log"
fi
export DEVMEMORY_HOOK_LOG

_log "event=${HOOK_EVENT:-?} session=${HOOK_SESSION_ID:-?} cwd=$REPO reason=${HOOK_REASON:-}"

# Avoid recursive Stop loops when Claude was continued by a prior stop hook.
if [[ "${HOOK_STOP_ACTIVE:-0}" == "1" ]]; then
  _log "skip: stop_hook_active"
  exit 0
fi

EVENT_LC="$(printf '%s' "${HOOK_EVENT:-}" | tr '[:upper:]' '[:lower:]')"
case "$EVENT_LC" in
  sessionend|session_end|"")
    # SessionEnd or unknown (manual invoke) → run
    ;;
  stop)
    if [[ "${DEVMEMORY_HOOK_ON_STOP:-0}" != "1" ]]; then
      _log "skip: Stop ignored (set DEVMEMORY_HOOK_ON_STOP=1 to enable; prefer SessionEnd)"
      exit 0
    fi
    ;;
  *)
    _log "skip: unsupported event ${HOOK_EVENT}"
    exit 0
    ;;
esac

# Debounce per session (or per repo when session id missing)
DEBOUNCE="${DEVMEMORY_HOOK_DEBOUNCE_S:-120}"
STAMP_DIR="$REPO/.devmemory/hook-stamps"
mkdir -p "$STAMP_DIR" 2>/dev/null || true
STAMP_KEY="${HOOK_SESSION_ID:-nosession}"
STAMP_KEY="$(printf '%s' "$STAMP_KEY" | tr -c 'A-Za-z0-9._-' '_')"
STAMP_FILE="$STAMP_DIR/$STAMP_KEY"
NOW="$(date +%s)"
if [[ -f "$STAMP_FILE" && "${DEVMEMORY_HOOK_FORCE:-0}" != "1" ]]; then
  LAST="$(cat "$STAMP_FILE" 2>/dev/null || echo 0)"
  if [[ "$LAST" =~ ^[0-9]+$ ]] && (( NOW - LAST < DEBOUNCE )); then
    _log "skip: debounced (${DEBOUNCE}s) last=$((NOW - LAST))s ago"
    exit 0
  fi
fi
printf '%s' "$NOW" >"$STAMP_FILE" 2>/dev/null || true

# Locate devmemory CLI
find_devmemory() {
  if [[ -n "${DEVMEMORY_BIN:-}" && -x "${DEVMEMORY_BIN}" ]]; then
    echo "$DEVMEMORY_BIN"
    return
  fi
  if command -v devmemory >/dev/null 2>&1; then
    command -v devmemory
    return
  fi
  # Walk up from REPO for .venv
  local d="$REPO"
  while [[ "$d" != "/" ]]; do
    if [[ -x "$d/.venv/bin/devmemory" ]]; then
      echo "$d/.venv/bin/devmemory"
      return
    fi
    d="$(dirname "$d")"
  done
  # Script lives in repo/scripts → sibling .venv
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd || true)"
  if [[ -n "$here" && -x "$here/.venv/bin/devmemory" ]]; then
    echo "$here/.venv/bin/devmemory"
    return
  fi
  echo ""
}

DM="$(find_devmemory)"
if [[ -z "$DM" ]]; then
  _log "skip: devmemory not found on PATH or in .venv"
  exit 0
fi

# Load OpenRouter key quietly if present (never print)
if [[ -n "${DEVMEMORY_ENV_FILE:-}" && -f "${DEVMEMORY_ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${DEVMEMORY_ENV_FILE}" 2>/dev/null || true
  set +a
fi
# Also try repo scripts/load-env.sh when available
_HOOK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd || true)"
if [[ -z "${OPENROUTER_API_KEY:-}" && -n "$_HOOK_ROOT" && -f "$_HOOK_ROOT/scripts/load-env.sh" ]]; then
  # shellcheck disable=SC1091
  source "$_HOOK_ROOT/scripts/load-env.sh" 2>/dev/null || true
fi

ARGS=(extract --repo "$REPO")
if [[ -n "${HOOK_SESSION_ID:-}" ]]; then
  ARGS+=(--session "$HOOK_SESSION_ID")
fi
if [[ "${DEVMEMORY_HOOK_APPLY:-0}" == "1" ]]; then
  ARGS+=(--apply)
fi
if [[ "${DEVMEMORY_HOOK_OFFLINE:-0}" == "1" ]]; then
  ARGS+=(--offline)
elif [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  # No key → offline so hook still produces units without failing silently forever
  ARGS+=(--offline)
  _log "note: no OPENROUTER_API_KEY; using --offline"
fi
if [[ "${DEVMEMORY_HOOK_FORCE:-0}" == "1" ]]; then
  ARGS+=(--force)
fi
if [[ -n "${DEVMEMORY_HOOK_MODEL:-${DEVMEMORY_MODEL:-}}" ]]; then
  ARGS+=(--model "${DEVMEMORY_HOOK_MODEL:-$DEVMEMORY_MODEL}")
fi

_run() {
  _log "run: $DM ${ARGS[*]}"
  # shellcheck disable=SC2086
  if OUT="$("$DM" "${ARGS[@]}" 2>>"${DEVMEMORY_HOOK_LOG}" )"; then
    _log "ok: ${OUT##*$'\n'}"
  else
    _log "warn: devmemory exit non-zero (see log)"
  fi
}

if [[ "${DEVMEMORY_HOOK_BG:-1}" == "1" ]]; then
  # SessionEnd budget can be ~1.5s; never block Claude on Hermes.
  (
    _run
  ) >/dev/null 2>&1 &
  _log "spawned pid=$!"
else
  _run
fi

exit 0
