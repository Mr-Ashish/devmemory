#!/usr/bin/env bash
# Load OpenRouter credentials without printing secrets.
# Order: existing env → repo .env → DEVMEMORY_ENV_FILE → sibling pr-review-agent .env
set -euo pipefail

# Resolve repo root whether invoked via bash or zsh source
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
  _LOAD_ENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [[ -n "${ZSH_VERSION:-}" ]]; then
  _LOAD_ENV_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
else
  _LOAD_ENV_DIR="$(cd "$(dirname "$0")" && pwd)"
fi
ROOT="$(cd "$_LOAD_ENV_DIR/.." && pwd)"

_load_file() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  set -a
  # shellcheck disable=SC1090
  source "$f"
  set +a
}

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  _load_file "$ROOT/.env"
fi
if [[ -z "${OPENROUTER_API_KEY:-}" && -n "${DEVMEMORY_ENV_FILE:-}" ]]; then
  _load_file "$DEVMEMORY_ENV_FILE"
fi
if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  _load_file "/Users/ashishmishra/Documents/experiments/pr-review-agent/.env"
fi

export OPENROUTER_BASE_URL="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}"
export DEVMEMORY_MODEL="${DEVMEMORY_MODEL:-openai/gpt-4.1-mini}"
