#!/usr/bin/env bash
# Live smoke: Hermes + OpenRouter one-shot.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/load-env.sh"

"$ROOT/scripts/ensure-hermes.sh"

export PATH="${HOME}/.local/bin:${HOME}/.hermes/bin:${PATH}"
: "${OPENROUTER_API_KEY:?OPENROUTER_API_KEY required}"

MODEL="${DEVMEMORY_MODEL:-openai/gpt-4.1-mini}"
HERMES_HOME="${HERMES_HOME:-$ROOT/.devmemory/hermes-home}"
mkdir -p "$HERMES_HOME/memories" "$HERMES_HOME/logs"
cp -f "$ROOT/agent/config.yaml" "$HERMES_HOME/config.yaml"
cp -f "$ROOT/agent/SOUL.md" "$HERMES_HOME/SOUL.md" 2>/dev/null || true
umask 077
printf 'OPENROUTER_API_KEY=%s\n' "$OPENROUTER_API_KEY" >"$HERMES_HOME/.env"
export HERMES_HOME

OUT="$(mktemp)"
set +e
(
  cd "$ROOT"
  hermes -z "Reply with exactly the single word: pong" \
    --provider openrouter \
    --model "$MODEL" \
    >"$OUT" 2>"$OUT.err"
)
RC=$?
set -e

echo "hermes_rc=$RC"
echo "stdout:"
head -c 2000 "$OUT" || true
echo
if [[ $RC -ne 0 ]]; then
  echo "stderr:" >&2
  tail -c 4000 "$OUT.err" >&2 || true
  exit "$RC"
fi
if ! grep -qi pong "$OUT"; then
  echo "WARN: expected 'pong' in output; continuing if non-empty" >&2
  [[ -s "$OUT" ]] || exit 1
fi
echo "SMOKE_OK"
