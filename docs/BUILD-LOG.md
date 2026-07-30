# Build log — how devmemory was built (dogfood)

This document externalizes the construction of **devmemory** while using the product **on itself**. No third-party monorepo was used as the demo surface: the source of truth is this repository.

## Principles

1. **Dogfood over demo theater** — every durable lesson lands in `DEV.md` / `USAGE.md` here.
2. **Traces are first-class** — live Hermes runs are packaged under `docs/showcase/` (redacted).
3. **Apply is the product** — LLM proposes; path snap / sections / dedupe decide what the repo accepts.
4. **Hermes + OpenRouter** — runtime from Nous Hermes Agent; inference via OpenRouter (Opus 5 for dogfood quality).

## Timeline (condensed)

| Phase | What happened | Artifact |
|-------|---------------|----------|
| Vision | README-only vision (archit15singh essay) | initial commit |
| Scaffold | Python package, CLI, fixtures, Luffy-shaped pipeline | `src/devmemory/*` |
| Live wire | Hermes install, OpenRouter smoke (`pong`) | `scripts/smoke-hermes.sh` |
| Quality ROI | Path snap, sections, dedupe, no-tools extract | `paths.py`, `sections.py`, `apply.py` |
| Dogfood | Self-extract with Opus 5 + showcase packaging | `docs/showcase/dogfood-*` |
| Brand | Three.js living-memory artifact + README architecture | `assets/devmemory-core.html` |

## Dependency map (borrowed, not forked)

| Source | Borrowed |
|--------|----------|
| [luffy-pr-review-agent](https://github.com/Mr-Ashish/luffy-pr-review-agent) | assemble → hermes -z → normalize → distill/trace pattern; OpenRouter env; SOUL/config seeding |
| [hermes-agent](https://github.com/NousResearch/hermes-agent) | CLI runtime only |
| [hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) | secret patterns, session-import ideas; GEPA later |

## Recursive improvement loop

```text
change code
  → pytest
  → live extract (fixture or dogfood narrative) --apply --showcase
  → review DEV.md / USAGE.md diffs
  → capture eval notes in docs/evals/
  → push
  → repeat
```

## Privacy rules for public traces

- Never commit `.env` or raw OpenRouter keys
- Showcase packages run through `trace.py` redaction
- `.devmemory/` remains gitignored; only curated slices are published

## 2026-07-31 · recursive dogfood loop started

- Iter1: empty H2 scrub (sections.py + apply templates)
- Iter2: block knowledge under tests/docs/fixtures/assets/scripts
- Live Opus 5 extract + showcase after each meaningful fix

## 2026-07-31 · dogfood loop iter3

- Paraphrase-level bullet near-dupe (Jaccard + stems)
- Assemble-side allowed-dir filter + compact existing knowledge
- Live Opus 5 showcase `dogfood-run-20260731T022731-f1515c` (blocked paths: none)

## 2026-07-31 · R1 Claude session discovery

- `sources/claude.py`: history multi-turn grouping, project JSONL, cwd path match, epoch-ms sort, env overrides, `pick_latest_unprocessed`
- CLI: list-sessions Claude-first + turns; extract default prefers latest unprocessed real session
- Tests: `tests/test_claude_discovery.py` (8)
- Live Opus showcase `dogfood-run-20260731T023342-e5e026` → knowledge in `src/devmemory/sources/DEV.md`
- **Backlog:** R1 done → next **R2** (dry-run units+proposed paths; --apply writes)

## 2026-07-31 · R2 dry-run UX

- `apply.plan_result` / `plan_unit`: proposed DEV.md/USAGE.md paths without disk writes
- Extract always plans; `--apply` writes + marks processed; dry-run leaves cursor intact
- CLI: `mode=dry-run|apply`, proposed path list, machine JSON `proposed[]`
- Artifacts: `plan.json` (dry-run) vs `apply.json` (write)
- Tests: `tests/test_dry_run.py` (5) → 35 total
- Live Opus showcase `dogfood-run-20260731T024229-b45cff` hermes_rc=0 units=5
- **Backlog:** R2 done → next **R3** (Claude Code stop-hook / one-liner)

## 2026-07-31 · R3 Claude Code SessionEnd hook

- `scripts/claude-code-hook.sh`: stdin JSON → SessionEnd (Stop opt-in) → background dry-run extract; debounce; never block Claude (exit 0); offline fallback without key; log `.devmemory/hooks.log`
- `scripts/install-claude-hook.sh`: one-liner merge into `.claude/settings.json` (`--user`, `--with-stop`, `--print`)
- Tests: `tests/test_claude_hook.py` (9) → 44 total
- Docs: README + USAGE one-liner and env table
- Live Opus showcase `dogfood-run-20260731T025126-b52ea6` hermes_rc=0 units=4 · eval 4.8/5
- **Backlog:** R3 done → next **R4** (preview as unified knowledge git-style diff before apply)

## 2026-07-31 · R4 unified knowledge preview diff

- `apply.plan_preview` / `FileDiff` / `PreviewPlan`: sequential in-memory merge → one git-style unified diff per knowledge file
- Artifacts: `preview.diff` + `preview.json` (stats) on every extract; dry-run CLI prints colorized unified diff
- Machine JSON: `preview.stats` + `preview.diff_path` + `preview.files`
- `plan_result` now uses sequential preview (matches multi-unit `--apply`)
- Tests: `tests/test_preview_diff.py` (7) → 51 total
- Showcase packs `preview.diff` / `preview.json`; live Opus `dogfood-run-20260731T025840-bf64f4` hermes_rc=0 units=4 · eval 4.8/5
- **Backlog:** R4 done → next **R5** (devmemory doctor)

## 2026-07-31 · R5 devmemory doctor

- `doctor.py` + `devmemory doctor`: hermes, OPENROUTER key (masked), sessions, model, git, gitignore, hook, state
- Flags: `--json`, `--strict` (exit 1 unless ready_live); machine JSON line always
- Never prints raw keys — fingerprint only
- Tests: `tests/test_doctor.py` (7) → 58 total
- Live: `doctor --strict` ready_live=yes; Opus showcase `dogfood-run-20260731T030327-011c11` hermes_rc=0; smoke-e2e **E2E_OK**; eval 4.7/5
- **Milestone:** R1–R5 proven (tests+live). Next optional **R6** anti-restate

## 2026-07-31 · R6 anti-restate (claim index)

- `_near_duplicate`: stopwords + significant-token overlap (inter≥4 / cover≥0.55); norm strips `/`
- Whole-file claim norms in `_append_section` (cross-section restates skipped)
- `scrub_file_near_dupes` file-wide, wired into `_compute_unit_text` (was dead/section-local)
- Assemble: compact claim index fingerprints + excerpts; prompt “return units:[] if only restates”
- Offline fallback only on `hermes_rc != 0` or parse failure — intentional empty units preserved
- Tests: 3 apply + 2 fallback → **63 total**
- Live Opus showcase `dogfood-run-20260731T031810-c66390` hermes_rc=0 units=2 (+4/-0) · eval **5.0/5**
- **Backlog:** R6 done → next **R7** CI form-validator

## 2026-07-31 · R7 CI form-validator

- `validate.py` + `devmemory validate`: H1, placeholders, empty H2, glued section H2 (ignore inline `` `##` ``), blocked path, secrets, unknown-section warn
- Flags: `--json`, `--strict` (warns fail); machine JSON summary line
- `scripts/validate-knowledge.sh` → validate --strict; `.github/workflows/ci.yml` pytest + soft validate
- Fixed historical mid-line `.## Section` thrash in knowledge files
- Tests: `tests/test_validate.py` (12) → **75 total**
- Live Opus showcase `dogfood-run-20260731T032614-a2aa70` hermes_rc=0 units=4 · eval **5.0/5**
- **Backlog:** R7 done → next **hook apply gate** (tool-edit only) or R8 watch

## 2026-07-31 · Hook tool-edit gate (R7.5)

- `hook_gate.py`: detect Write/Edit/MultiEdit/NotebookEdit/… in Claude JSONL; `should_run_extract_for_session`
- `claude-code-hook.sh`: default require edits; skip chat-only; missing transcript allows; FORCE bypasses
- Fail-open on import/IO errors; hook still always exit 0
- Tests: `tests/test_hook_gate.py` (+ hook integration) → **87 total**
- Live Opus showcase `dogfood-run-20260731T033504-281af8` hermes_rc=0 units=4 · eval **5.0/5**
- **Backlog:** core habit loop solid. Optional **R8 watch**; else P2 polish only

## 2026-07-31 · R8 watch

- `watch.py` + `devmemory watch`: poll Claude sessions; `.devmemory/watch.json` fingerprints
- Flags: `--once`, `--interval`, `--max-polls`, `--apply`, `--offline`, `--require-edits/--allow-chat`, `--json`
- Tool-edit gate only on per-session project JSONL (not multi-session history.jsonl)
- `mark_seen` after success or error; max 3 extracts per cycle
- Tests: `tests/test_watch.py` → **92 total**
- Live Opus showcase `dogfood-run-20260731T033900-ad9f76` hermes_rc=0 units=5 · eval **5.0/5**
- **Milestone:** R1–R8 complete. Remaining backlog is P2+ only
