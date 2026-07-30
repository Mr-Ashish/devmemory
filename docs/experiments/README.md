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
