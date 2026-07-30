# Session

- **session_id:** `r7-validate-ship`
- **source:** `file`
- **project:** `/Users/ashishmishra/Documents/experimentation/devmemory`
- **timestamp:** ``

## Transcript / notes

Session notes for R7 CI form-validator in devmemory:

Built `devmemory validate` (validate.py) so CI can check colocated DEV.md/USAGE.md
form without transcripts or LLM. Checks: H1 present, no _(none yet)_ placeholders,
no empty H2 sections, no glued mid-line ## section headings (ignores inline `## Architecture`
prose), knowledge not under blocked trees (tests/docs/fixtures/assets/scripts),
secret pattern scan, warn on non-canonical H2. CLI: `devmemory validate`, `--json`,
`--strict` (fails on warns). Script: `./scripts/validate-knowledge.sh` runs validate --strict.
GitHub Actions `.github/workflows/ci.yml` runs pytest + `devmemory validate` (soft; not --strict).
Design decision: form validation is local pure-Python — no Hermes, no OpenRouter, no session access.
Pitfall: do not treat inline backtick mentions of `## Section` as glued headings.
Command: `devmemory validate --json` for CI machine output; exit 1 on fail.

