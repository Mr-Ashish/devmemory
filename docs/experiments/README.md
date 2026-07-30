# Experiments

Running notes from dogfood experiments. Prefer short entries with command + outcome.

## 2026-07-31 · no-tools extract

**Hypothesis:** Terminal toolsets slow extract and cause path wandering.  
**Method:** Default `DEVMEMORY_TOOLSETS=""`; full context in prompt.  
**Result:** Live extract ~10–40s, stable JSON, correct `src/auth` mapping.  
**Keep:** default no tools.

## 2026-07-31 · apply quality ROI

**Hypothesis:** Doc quality is dominated by merge layer, not model size.  
**Method:** placeholder scrub + bullet near-dupe + path snap + section canonicalize.  
**Result:** Re-runs no longer leave `_(none yet)_` or double HS256 bullets.  
**Keep:** all four.

## 2026-07-31 · dogfood narrative + Opus 5

**Hypothesis:** Self-describing build session produces better package-level DEV.md than auth fixture alone.  
**Method:** `fixtures/sessions/dogfood-build-narrative.json` + `--model anthropic/claude-opus-5 --showcase`.  
**Result:** See `docs/showcase/dogfood-*` after the run lands.

## Ideas backlog

- Semantic dedupe (embedding or LLM-judge) for paraphrases
- `devmemory watch` on Claude history mtime
- GEPA skill evolution from self-evolution repo (Phase later)
- Pure OpenRouter HTTP path without Hermes CLI for CI minimalism

## 2026-07-31 · empty H2 scrub (dogfood iter1)

**Hypothesis:** Empty template H2s make knowledge files look unfinished.  
**Method:** `scrub_empty_h2_sections` in `strip_placeholders`; lean DEV/USAGE templates.  
**Result:** empty_h2 check → none; 20 tests.  
**Keep.**

## 2026-07-31 · knowledge path blocklist (dogfood iter2)

**Hypothesis:** Model puts knowledge under tests/docs because those dirs exist.  
**Method:** `is_knowledge_blocked` + resolve to `.`; prompt forbids those trees; delete stray DEV.md.  
**Result:** unit tests green; prompt updated.  
**Keep.**

## 2026-07-31 · paraphrase near-dupe (dogfood iter3)

**Hypothesis:** Containment-only dedupe misses reworded pitfalls.  
**Method:** token Jaccard + light stemming; section-internal scrub.  
**Result:** path-snap / redaction paraphrases collapsed; 22 tests.  
**Keep.**

## 2026-07-31 · allowed dirs in assemble (dogfood iter3)

**Hypothesis:** Model proposes tests/docs because they appear in EXISTING_DIRS.  
**Method:** filter dirs with `is_knowledge_blocked`; compact knowledge context.  
**Result:** live Opus units had zero blocked paths.  
**Keep.**

## 2026-07-31 · R1 Claude session discovery

**Hypothesis:** Real Claude Code sessions for cwd must surface in list/extract without fixture flags.  
**Method:** group history by `sessionId`; project JSONL by encoded path; strict cwd path match; newest-first with ms-normalized timestamps; default pick Claude before fixtures; env path overrides for tests.  
**Result:** 8 discovery tests green; staged live layout `claude=2 unprocessed_claude=2`; default resolve picks real session; Opus dogfood lands `sources/DEV.md`.  
**Keep.** Real `~/.claude` for this repo still empty until Claude Code is used here (fixtures remain fallback).

## 2026-07-31 · R2 dry-run units+paths

**Hypothesis:** Default extract should preview proposed knowledge paths so humans can gate before write; only `--apply` should mutate docs and the processed cursor.  
**Method:** split `plan_unit`/`plan_result` from apply; extract always plans; mark processed only when `apply=True` and units>0; CLI machine JSON includes `proposed[]`.  
**Result:** 5 dry-run tests green (35 total); offline dry-run writes zero DEV/USAGE files; live Opus apply hermes_rc=0, showcase `dogfood-run-20260731T024229-b45cff`, eval 4.8/5.  
**Keep.**

## 2026-07-31 · R3 Claude Code SessionEnd hook

**Hypothesis:** AI-native builders will not retype `devmemory extract` after every Claude Code session; a SessionEnd hook with dry-run default closes the loop without thrash.  
**Method:** `claude-code-hook.sh` (exit 0 always, background default, debounce, SessionEnd-only unless `DEVMEMORY_HOOK_ON_STOP=1`, offline if no key) + `install-claude-hook.sh` merge into project/user settings.  
**Result:** 9 hook tests green (44 total); install is idempotent; Stop ignored by default.  
**Keep.** Prefer SessionEnd over Stop; leave R8 watch for multi-session polling.

## 2026-07-31 · R4 unified knowledge preview diff

**Hypothesis:** Path lists alone are weak for human gate; AI-native builders need a git-style unified diff of DEV/USAGE before `--apply`.  
**Method:** sequential in-memory `plan_preview` (multi-unit same file), `difflib.unified_diff` with `diff --git` headers, `preview.diff`/`preview.json` artifacts, CLI colorized print.  
**Result:** 7 preview tests green (51 total); dry-run preview matches post-apply content.  
**Keep.**

## ROI ideas (persona jobs: session→discover→extract→apply→reuse)

1. **R5 doctor** — one command for hermes/OpenRouter/sessions/model readiness (highest next ROI).
2. **R6 anti-restate** — compact knowledge index so re-runs add nothing when stable.
3. **Hook apply gate** — only suggest extract when session had tool edits (lower thrash than Stop).
