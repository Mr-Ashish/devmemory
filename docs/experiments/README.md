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
