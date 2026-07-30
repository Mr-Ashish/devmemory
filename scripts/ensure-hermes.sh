#!/usr/bin/env bash
# Ensure Hermes Agent CLI is available on PATH.
set -euo pipefail

log() { echo "$*" >&2; }
notice() { echo "[ensure-hermes] $*" >&2; }

export PATH="${HOME}/.local/bin:${HOME}/.hermes/bin:${PATH}"

if command -v hermes >/dev/null 2>&1; then
  notice "hermes present: $(command -v hermes)"
  hermes --version 2>/dev/null || true
  exit 0
fi

notice "Installing Hermes Agent..."
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
export PATH="${HOME}/.local/bin:${HOME}/.hermes/bin:${PATH}"
# shellcheck disable=SC1091
[[ -f "${HOME}/.bashrc" ]] && source "${HOME}/.bashrc" || true
hash -r 2>/dev/null || true

for candidate in \
  "${HOME}/.local/bin/hermes" \
  "${HOME}/.hermes/bin/hermes" \
  "${HOME}/.hermes/hermes"; do
  if [[ -x "$candidate" ]]; then
    export PATH="$(dirname "$candidate"):${PATH}"
    break
  fi
done

command -v hermes >/dev/null 2>&1 || {
  log "ERROR: hermes not found after install"
  exit 1
}
notice "hermes installed: $(command -v hermes)"
hermes --version 2>/dev/null || true
