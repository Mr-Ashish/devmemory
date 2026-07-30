# DEV — engineering knowledge

> How this part of the system is built.

## Architecture

## Design decisions

## Patterns

## Pitfalls
- Never commit `.devmemory/` run artifacts or raw AI session transcripts to source control to protect privacy and reduce clutter.
- Use CI to validate generated knowledge files for form and freshness rather than requiring access to raw session data.
- Localized knowledge files are preferable to a large monolithic repository-wide context to avoid scalability and maintainability issues.
