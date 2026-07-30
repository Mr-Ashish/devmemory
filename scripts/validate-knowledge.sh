#!/usr/bin/env bash
# CI helper: validate DEV.md / USAGE.md form without transcripts or LLM.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ -x "$ROOT/.venv/bin/devmemory" ]]; then
  DM="$ROOT/.venv/bin/devmemory"
elif command -v devmemory >/dev/null 2>&1; then
  DM=devmemory
else
  echo "devmemory not found; pip install -e '.[dev]' first" >&2
  exit 1
fi
exec "$DM" validate --strict "$@"
