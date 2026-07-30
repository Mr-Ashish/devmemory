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

## 2026-07-31 · R5 devmemory doctor

**Hypothesis:** After Claude sessions, the first failure mode is "why won't extract run?" — hermes missing, key unset, no sessions — not model quality.  
**Method:** single `devmemory doctor` with ok/warn/fail/info checks, masked key fingerprint, ready_live/ready_offline, `--strict` for scripts.  
**Result:** 7 doctor tests green (58 total); live machine reports ready_live=yes with fixtures-only sessions warn.  
**Keep.**

## ROI ideas (persona jobs: session→discover→extract→apply→reuse)

1. **R6 anti-restate** — compact knowledge index so re-runs add nothing when stable (highest next after R1–R5).
2. **R7 CI form-validator** — DEV.md/USAGE.md shape without transcripts.
3. **Hook apply gate** — only suggest extract when session had tool edits.
4. **R8 watch** — mtime poll on Claude history (defer until habit loop solid).
5. **Semantic embedding dedupe** — only if R6 still leaks paraphrases (P2).

## 2026-07-31 · fire · R6 anti-restate (claim index)

**Persona jobs:** extract→apply→reuse. Stable knowledge must not thrash on every dogfood re-run.
**Gap:** R5 eval Dedupe 3.5 — frozen-pydantic restates keep landing; Jaccard 0.52 misses long technical paraphrases; `scrub_file_near_dupes` was dead code; filter was section-local only; assemble sent bulky partial bullets not a claim index.

### ROI rank (this fire)

| Rank | Idea | Impact×adoption / effort |
|------|------|--------------------------|
| 1 | **R6 claim-index anti-restate** | High — stops doc thrash on every re-run; low effort |
| 2 | R7 CI form-validator | Med — CI safety without transcripts |
| 3 | Hook apply gate (tool-edit only) | Med — less noise after chat-only sessions |
| 4 | R8 `watch` | Low until real Claude use here |
| 5 | GEPA / self-evolution | Skip — core habit loop first |

### Build plan (R6)

1. Strengthen `_near_duplicate` with significant-token overlap + strip `/` in norm.
2. Whole-file claim norms when filtering new bullets (cross-section).
3. Wire `scrub_file_near_dupes` file-wide into apply path; compact **claim index** in assemble + prompt “return units:[] if only restates”.
4. Tests: technical restate skip, cross-section skip, file-wide scrub.
5. pytest → live Opus dogfood → eval → push.

### Result

**Keep.** Live Opus: narrative restates dropped; only R6 delta units applied (+4/-0). Offline fallback gated so intentional `units:[]` is not replaced. Showcase `dogfood-run-20260731T031810-c66390`, eval 5.0/5, 63 tests.

## 2026-07-31 · fire · R7 CI form-validator

**Persona jobs:** apply→reuse (and CI gate without transcripts).
**Gap:** README promises “CI validates knowledge form, never transcripts” but there is no `devmemory validate` / CI workflow — only live extract + doctor.

### ROI rank (this fire)

| Rank | Idea | Impact×adoption / effort |
|------|------|--------------------------|
| 1 | **R7 CI form-validator** | High for trust/reuse — blocks hollow/glued/secret knowledge on PR |
| 2 | Hook apply gate (tool-edit only) | Med — less thrash after chat-only sessions |
| 3 | R8 `watch` | Low until real Claude sessions land here |
| 4 | Semantic embedding dedupe | P2 — R6 already at 5.0 dedupe |
| 5 | GEPA | Skip |

### Build plan (R7)

1. `validate.py`: discover DEV.md/USAGE.md; checks H1, placeholders, empty H2, glued `##`, blocked path, secrets, unknown section warn.
2. CLI `devmemory validate --json/--strict`; exit 1 on fail.
3. Tests on good/bad fixtures; thin `scripts/validate-knowledge.sh` + optional GH workflow.
4. pytest → live Opus dogfood → eval → push.

### Result

**Keep.** 75 tests; repo `validate` ok (1 custom-section warn). Live Opus R7 ship narrative units=4 → showcase `dogfood-run-20260731T032614-a2aa70`, eval 5.0/5.

## 2026-07-31 · fire · hook tool-edit gate (R7.5 / pre-R8)

**Persona jobs:** session→extract (habit loop without thrash).
**Gap:** SessionEnd hook fires after every session including pure chat; dry-runs still burn Hermes/offline noise and log spam when nothing was written to the tree.

### ROI rank (this fire)

| Rank | Idea | Impact×adoption / effort |
|------|------|--------------------------|
| 1 | **Hook tool-edit gate** | High adoption ROI — less noise after chat-only Claude sessions |
| 2 | R8 `watch` | Lower until real Claude sessions land on this repo |
| 3 | Canonicalize custom USAGE H2 (Claude hook) | P2 polish |
| 4 | Semantic embedding dedupe | P2 |
| 5 | GEPA | Skip |

### Build plan

1. `hook_gate.py`: detect Write/Edit/MultiEdit/NotebookEdit (and kin) in transcript JSONL or text.
2. Hook: default `DEVMEMORY_HOOK_REQUIRE_EDITS=1` → skip when transcript has no tool edits; missing transcript still allows run.
3. Tests: chat-only skip, edit-present run, env opt-out.
4. pytest → live Opus dogfood → eval → push.
