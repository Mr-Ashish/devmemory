```json
{
  "summary": "Durable knowledge from the devmemory dogfood build sessions: the paraphrase-level bullet dedupe upgrade in apply.py, the assemble-side knowledge compaction plus blocked-tree filtering, a markdown heading-glue pitfall visible in the current diff, root-level model/dependency decisions, and the bounded-context env knobs for operators.",
  "session_ids": ["dogfood-build-narrative"],
  "units": [
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Design decisions",
      "content": "- Bullet dedupe in `apply.py` is paraphrase-aware, not just exact: `_near_duplicate` accepts a match on substring containment (both bullets >24 chars), Jaccard ≥ 0.52, or coverage of the smaller token set ≥ 0.62.\n- `_norm_bullet` strips quotes, underscores and punctuation (`_'\".,;:()[]{}`) in addition to backticks/asterisks so restated bullets normalize to the same string.\n- `_token_set` applies a longest-suffix-first `_stem` (ations/ation/tions/ing/ers/ies/ed/es/s) and drops tokens ≤2 chars; the stem guard requires `len(t) > len(suf) + 3` to avoid over-stemming words like \"existing\".\n- `dedupe_section_bullets` (first bullet wins) runs on the *existing* section body before new bullets are filtered, so a file that already contains duplicates gets cleaned on the next apply; `scrub_file_near_dupes` applies it per `## ` section and finishes with `strip_placeholders`.",
      "evidence": [
        "def _near_duplicate(a: str, b: str, *, threshold: float = 0.52) -> bool:",
        "return jacc >= threshold or cover >= 0.62",
        "\"\"\"Drop near-duplicate bullets already inside a section body (first wins).\"\"\""
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Architecture",
      "content": "- `assemble.collect_repo_context` compacts existing DEV.md/USAGE.md before they reach the model: `_compact_knowledge` keeps each `## ` title plus at most 5 bullets, sections with no bullets are dropped entirely, and the result is capped at `DEVMEMORY_MAX_KNOWLEDGE_CHARS` (default 1600) with a `… [truncated; do not restate] …` marker — this is an anti-restate/token-thrift measure, not just truncation.\n- `paths.is_knowledge_blocked` filters both the `EXISTING_DIRS` list and the collected knowledge files, so blocked trees (tests/docs-style dirs) can never be offered to the model as a knowledge home.\n- The directory list handed to the prompt is `list_repo_dirs` filtered by block rules and truncated to the first 80 entries.",
      "evidence": [
        "\"\"\"Keep H2 titles + up to 5 bullets per section (token thrift, anti-restate).\"\"\"",
        "MAX_KNOWLEDGE_FILE_CHARS = int(os.environ.get(\"DEVMEMORY_MAX_KNOWLEDGE_CHARS\", \"1600\"))",
        "dirs = [d for d in list_repo_dirs(repo_root) if d == \".\" or not is_knowledge_blocked(d)]"
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Pitfalls",
      "content": "- Section-append must preserve the blank line before the next `## ` heading: when the trailing newline is consumed, the following heading is glued onto the last bullet and stops rendering as a heading (`- …maintainability issues.## Patterns`). This regression shows up across every merged DEV.md/USAGE.md at once, so check one file's diff before re-running a full apply.\n- Exact-match dedupe is insufficient — the model happily re-emits the same claim in new words (e.g. \"breaks JSON — redact after parse\" vs \"corrupts the payload — run redaction after normalize parses units\"). Regression coverage for this lives in `tests/test_apply.py::test_apply_skips_paraphrase_near_dupes`, which asserts the second apply returns `changes == []`.\n- Feeding whole knowledge files back into the prompt encourages restatement; send only compacted H2 + top bullets.",
      "evidence": [
        "- Localized knowledge files are preferable ... maintainability issues.## Patterns",
        "def test_apply_skips_paraphrase_near_dupes(tmp_path: Path):",
        "assert changes == []"
      ],
      "confidence": "high"
    },
    {
      "kind": "dev",
      "path": ".",
      "action": "merge",
      "section": "Design decisions",
      "content": "- The product was built and validated entirely inside this repository (self-dogfooding); there is no external monorepo dependency.\n- Hermes Agent is consumed as an installed CLI (`hermes -z`) with OpenRouter inference — `anthropic/claude-opus-5` is the model pinned for dogfood-quality runs, `gpt-4.1-mini` for cheap iteration.\n- `hermes-agent-self-evolution` is treated as an idea source only (session importers, secret-redaction patterns, later skill GEPA); it is not part of the MVP runtime.\n- The apply layer — not the prompt — is the quality boundary: path snapping to existing dirs, canonical H2 titles, bullet near-dupe skipping and placeholder scrubbing. The LLM proposes; merge decides.\n- Hermes runs extract with empty toolsets (pure reasoning over assembled context); `DEVMEMORY_TOOLSETS=terminal` is an explicit opt-in override.",
      "evidence": [
        "Hermes Agent is a CLI dependency (not vendored). Inference is OpenRouter.",
        "Apply layer is the product quality boundary ... LLM proposes; merge decides.",
        "Default Hermes toolsets are empty for extract"
      ],
      "confidence": "high"
    },
    {
      "kind": "usage",
      "path": "src/devmemory",
      "action": "merge",
      "section": "Troubleshooting",
      "content": "- Context size is tunable via env: `DEVMEMORY_MAX_SESSION_CHARS` (24000), `DEVMEMORY_MAX_DIFF_CHARS` (40000), `DEVMEMORY_MAX_TREE_LINES` (200), `DEVMEMORY_MAX_KNOWLEDGE_CHARS` (1600). Raise these only when the model is clearly missing evidence — larger prompts increase restatement.\n- Unit landed under the wrong directory: confirm the target appears in the `EXISTING_DIRS` block of the assembled prompt and that the module dir shows up in the tree sample; blocked trees are filtered out on purpose and will never be accepted.\n- Docs growing on every run: verify near-dupe skipping is active (`apply.dedupe_section_bullets` / `scrub_file_near_dupes`) rather than editing the docs by hand.\n- Before publishing a run, remember `trace.py` redacts `sk-or` / `Bearer` tokens and env assignments on the way into `docs/showcase/` — never copy files there manually.",
      "evidence": [
        "MAX_KNOWLEDGE_FILE_CHARS = int(os.environ.get(\"DEVMEMORY_MAX_KNOWLEDGE_CHARS\", \"1600\"))",
        "If wrong path: ensure path appears in EXISTING_DIRS in assembled prompt",
        "Showcase privacy: trace.py redacts sk-or / Bearer / env assignments"
      ],
      "confidence": "medium"
    }
  ]
}
```
