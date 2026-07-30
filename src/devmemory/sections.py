"""Canonical DEV.md / USAGE.md section titles."""

from __future__ import annotations

import re

DEV_SECTIONS = (
    "Architecture",
    "Design decisions",
    "Patterns",
    "Pitfalls",
    "Extension points",
)

USAGE_SECTIONS = (
    "Setup",
    "Common commands",
    "Debugging",
    "Troubleshooting",
)

_PLACEHOLDER_RE = re.compile(
    r"^\s*(_\(none yet\)_|_\(seeded by devmemory init\)_|_\(todo\)_|TODO)\s*$",
    re.IGNORECASE,
)

# alias → (kind, canonical section)
_ALIASES: dict[str, tuple[str, str]] = {
    "architecture": ("dev", "Architecture"),
    "design": ("dev", "Design decisions"),
    "design decisions": ("dev", "Design decisions"),
    "decisions": ("dev", "Design decisions"),
    "patterns": ("dev", "Patterns"),
    "pattern": ("dev", "Patterns"),
    "pitfalls": ("dev", "Pitfalls"),
    "pitfall": ("dev", "Pitfalls"),
    "gotchas": ("dev", "Pitfalls"),
    "extension points": ("dev", "Extension points"),
    "extensions": ("dev", "Extension points"),
    "setup": ("usage", "Setup"),
    "install": ("usage", "Setup"),
    "common commands": ("usage", "Common commands"),
    "commands": ("usage", "Common commands"),
    "usage": ("usage", "Common commands"),
    "usage and cli": ("usage", "Common commands"),
    "cli": ("usage", "Common commands"),
    "local development": ("usage", "Common commands"),
    "local development and debugging": ("usage", "Debugging"),
    "debugging": ("usage", "Debugging"),
    "debug": ("usage", "Debugging"),
    "debug tip": ("usage", "Debugging"),
    "troubleshooting": ("usage", "Troubleshooting"),
}


def normalize_heading(section: str | None) -> str | None:
    if not section:
        return None
    return section.strip().lstrip("#").strip() or None


def canonicalize_section(kind: str, section: str | None) -> str | None:
    """Map free-form section titles onto the template H2 set."""
    heading = normalize_heading(section)
    if not heading:
        return "Design decisions" if kind == "dev" else "Common commands"
    key = heading.lower()
    if key in _ALIASES:
        _k, canon = _ALIASES[key]
        return canon
    # fuzzy contains
    for alias, (ak, canon) in _ALIASES.items():
        if alias in key or key in alias:
            if kind == "dev" and ak == "usage":
                # keep usage-ish headings out of DEV
                return "Design decisions"
            if kind == "usage" and ak == "dev":
                return "Common commands"
            return canon
    # kind default if unknown custom heading — keep short custom only when not placeholder-y
    if kind == "dev":
        return heading if len(heading) < 40 else "Design decisions"
    return heading if len(heading) < 40 else "Common commands"


def is_placeholder_line(line: str) -> bool:
    return bool(_PLACEHOLDER_RE.match(line.strip()))


def strip_placeholders(text: str) -> str:
    lines = [ln for ln in text.splitlines() if not is_placeholder_line(ln)]
    # collapse triple blank lines
    out: list[str] = []
    blank = 0
    for ln in lines:
        if not ln.strip():
            blank += 1
            if blank <= 2:
                out.append(ln)
        else:
            blank = 0
            out.append(ln)
    return scrub_empty_h2_sections("\n".join(out).rstrip() + "\n")


def scrub_empty_h2_sections(text: str) -> str:
    """Drop ## sections whose body is only whitespace (or placeholders already removed).

    Keeps H1, blockquotes, and any H2 that has at least one non-empty body line.
    """
    if not text.strip():
        return text if text.endswith("\n") else text + "\n"

    lines = text.splitlines()
    # Find H2 indices
    h2_idx = [i for i, ln in enumerate(lines) if re.match(r"^##\s+\S", ln)]
    if not h2_idx:
        return text if text.endswith("\n") else text + "\n"

    drop: set[int] = set()
    for n, start in enumerate(h2_idx):
        end = h2_idx[n + 1] if n + 1 < len(h2_idx) else len(lines)
        body = lines[start + 1 : end]
        if any(ln.strip() for ln in body):
            continue
        # empty body → drop heading and blank lines until next H2
        for j in range(start, end):
            drop.add(j)

    kept = [ln for i, ln in enumerate(lines) if i not in drop]
    # collapse excess blanks
    out: list[str] = []
    blank = 0
    for ln in kept:
        if not ln.strip():
            blank += 1
            if blank <= 2:
                out.append(ln)
        else:
            blank = 0
            out.append(ln)
    result = "\n".join(out).rstrip() + "\n"
    return result
