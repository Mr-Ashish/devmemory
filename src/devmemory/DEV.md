# DEV — engineering knowledge

> How this part of the system is built.

## Architecture

## Design decisions

- Extraction pipeline stages: assemble → hermes extract → normalize → apply.
- Hermes is used as a CLI dependency (hermes -z), not included as vendored source.
- OpenRouter serves as the LLM provider for extraction.
- Knowledge extraction operates entirely locally with transcripts never leaving the developer's machine.
- Knowledge files (DEV.md and USAGE.md) are maintained colocated next to code modules to keep documentation context-specific and easily accessible.
- The process avoids committing raw AI session transcripts or .devmemory/ run artifacts to source control.
- Extraction pipeline inputs include Claude Code session transcripts, current repository code changes, and outputs knowledge merged into local DEV.md and USAGE.md files.
- CI workflows validate the consistency and freshness of generated knowledge files without requiring access to local transcripts.

## Patterns

- Knowledge extraction pipeline runs as 4 separate phases: assemble context, extract knowledge using Hermes CLI call, normalize JSON output, then apply merged changes.
- Localized knowledge files (DEV.md for engineering details, USAGE.md for operational instructions) live next to code modules to provide context-targeted documentation.
- DEV.md captures architecture, design decisions, patterns, pitfalls, and module-specific engineering context.
- USAGE.md captures setup steps, commands, debugging, troubleshooting, and workflows essential for working with the code part.
- Extraction process keeps knowledge generation as an automatic by-product of development sessions.

## Pitfalls
