# Eval · R6 anti-restate (claim index) · 2026-07-31

| Field | Value |
|-------|-------|
| run_id | `run-20260731T031810-c66390` |
| model | `anthropic/claude-opus-5` |
| hermes_rc | 0 |
| units | 2 (only net-new R6 claims; rest of narrative dropped) |
| changes applied | 2 (both `src/devmemory/DEV.md`) |
| preview | +4 / -0 |
| total_s | ~19.5 |
| showcase | `docs/showcase/dogfood-run-20260731T031810-c66390/` |
| tests | **63 passed** (3 apply + 2 offline-fallback) |
| code commit | `7efbf1c` (+ follow-up fallback gate) |

## What shipped (R6)

1. **Significant-token near-dupe** — stopwords + `_sig_tokens`; inter≥4 or cover≥0.55 catches frozen-pydantic paraphrases (Jaccard alone was 0.25)
2. **Whole-file claim norms** — restates under a different H2 are skipped
3. **File-wide `scrub_file_near_dupes`** — wired into apply (was dead code; was section-local)
4. **Compact claim index in assemble** — fingerprints fed to the model with “do not restate”
5. **Prompt anti-restate** — prefer `units: []` over paraphrase
6. **Offline fallback gate** — intentional empty units no longer replaced by heuristics (path thrash fix)

## Live proof

```text
# Opus returned only net-new R6 knowledge; narrative restates dropped
devmemory extract --fixture dogfood-build-narrative --apply --force --showcase \
  --model anthropic/claude-opus-5
# → hermes_rc=0 model=anthropic/claude-opus-5 units=2 preview +4/-0
```

Earlier false-start (same fire): model correctly returned `units: []` but offline fallback polluted USAGE with absolute paths → fixed by fallback gate + re-run.

## Rubric (1–5)

| Axis | Score | Notes |
|------|-------|-------|
| Path accuracy | 5 | `src/devmemory/DEV.md` only |
| Kind split | 5 | Design decisions + Pitfalls |
| Dedupe | 5 | frozen pydantic collapsed to 1; re-run adds only true delta |
| Privacy | 5 | no keys; showcase redacted (local paths in fixture narrative only) |
| Actionability | 5 | R6 pitfalls + regression test names landed in knowledge |

**Composite: 5.0 / 5**

## R1–R6 milestone

| Item | Status |
|------|--------|
| R1 Claude discovery | done |
| R2 dry-run UX | done |
| R3 SessionEnd hook | done |
| R4 preview.diff | done |
| R5 doctor | done |
| R6 anti-restate | **done** (this eval) |

**Next:** R7 CI form-validator (DEV/USAGE shape without transcripts).
