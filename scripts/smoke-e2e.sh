#!/usr/bin/env bash
# Full e2e: offline unit path + optional live Hermes extract.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/load-env.sh"

cd "$ROOT"
export PATH="${ROOT}/.venv/bin:${HOME}/.local/bin:${HOME}/.hermes/bin:${PATH}"

echo "== pytest =="
python -m pytest -q

echo "== offline extract+apply on fixture sample_repo =="
TMP="$(mktemp -d)"
cp -R "$ROOT/fixtures/sample_repo/." "$TMP/"
# make it a git repo for assemble
(
  cd "$TMP"
  git init -q
  git add -A
  git -c user.email=dev@local -c user.name=dev commit -qm "init sample"
)
devmemory extract --repo "$TMP" --fixture sample-auth-module --offline --apply --force
test -f "$TMP/DEV.md" -o -f "$TMP/USAGE.md"
echo "offline e2e ok → $TMP"

if [[ "${DEVMEMORY_SKIP_LIVE:-0}" == "1" ]]; then
  echo "SKIP live (DEVMEMORY_SKIP_LIVE=1)"
  exit 0
fi

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "SKIP live (no OPENROUTER_API_KEY)"
  exit 0
fi

echo "== live hermes smoke =="
"$ROOT/scripts/smoke-hermes.sh"

echo "== live extract (dry apply on temp) =="
TMP2="$(mktemp -d)"
cp -R "$ROOT/fixtures/sample_repo/." "$TMP2/"
(
  cd "$TMP2"
  git init -q
  git add -A
  git -c user.email=dev@local -c user.name=dev commit -qm "init sample"
)
devmemory extract --repo "$TMP2" --fixture sample-auth-module --apply --force
echo "live extract units:"
find "$TMP2/.devmemory/out" -name units.json | head -1 | xargs cat
echo "E2E_OK"
