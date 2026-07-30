# DEV — engineering knowledge

> How this part of the system is built.

## Pitfalls
- Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
- Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.## Patterns

- Eval notes live under docs/evals but knowledge should root

## Design decisions

- The product was built and validated entirely inside this repository (self-dogfooding); there is no external monorepo dependency.
- Hermes Agent is consumed as an installed CLI (`hermes -z`) with OpenRouter inference — `anthropic/claude-opus-5` is the model pinned for dogfood-quality runs, `gpt-4.1-mini` for cheap iteration.
- `hermes-agent-self-evolution` is treated as an idea source only (session importers, secret-redaction patterns, later skill GEPA); it is not part of the MVP runtime.
- The apply layer — not the prompt — is the quality boundary: path snapping to existing dirs, canonical H2 titles, bullet near-dupe skipping and placeholder scrubbing. The LLM proposes; merge decides.
- Hermes runs extract with empty toolsets (pure reasoning over assembled context); `DEVMEMORY_TOOLSETS=terminal` is an explicit opt-in override.
