"""Apply knowledge units to colocated DEV.md / USAGE.md files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from devmemory.paths import list_repo_dirs, resolve_unit_path
from devmemory.redaction import contains_secret, redact
from devmemory.schema import ExtractionResult, KnowledgeUnit
from devmemory.sections import (
    canonicalize_section,
    is_placeholder_line,
    strip_placeholders,
)

# Sections are created on first content — avoid empty H2 scaffolding.
DEV_TEMPLATE = """# DEV — engineering knowledge

> How this part of the system is built.

"""

USAGE_TEMPLATE = """# USAGE — operational knowledge

> How to work with this part of the system.

"""


@dataclass
class ApplyChange:
    path: Path
    kind: str
    action: str
    section: str | None
    bytes_written: int


def knowledge_filename(kind: str) -> str:
    return "DEV.md" if kind == "dev" else "USAGE.md"


def target_file(repo_root: Path, unit: KnowledgeUnit, *, existing_dirs: list[str] | None = None) -> Path:
    resolved = resolve_unit_path(repo_root, unit.path, existing_dirs=existing_dirs)
    rel = Path(".") if resolved in (".", "") else Path(resolved)
    return (repo_root / rel / knowledge_filename(unit.kind)).resolve()


def _ensure_file(path: Path, kind: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    path.parent.mkdir(parents=True, exist_ok=True)
    body = DEV_TEMPLATE if kind == "dev" else USAGE_TEMPLATE
    path.write_text(body, encoding="utf-8")
    return body


def _norm_bullet(line: str) -> str:
    s = line.strip().lstrip("-*").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[`*]", "", s)
    return s


def _content_bullets(content: str) -> list[str]:
    lines = []
    for ln in content.splitlines():
        t = ln.strip()
        if not t or is_placeholder_line(t):
            continue
        if t.startswith(("-", "*")):
            lines.append(t if t.startswith("-") else "- " + t.lstrip("*").strip())
        else:
            lines.append(f"- {t}")
    return lines


def _filter_new_bullets(existing_section_body: str, content: str) -> str:
    """Return only bullets not already present (normalized)."""
    existing_norms = {
        _norm_bullet(ln)
        for ln in existing_section_body.splitlines()
        if ln.strip().startswith(("-", "*"))
    }
    kept: list[str] = []
    for b in _content_bullets(content):
        n = _norm_bullet(b)
        if not n or n in existing_norms:
            continue
        # near-duplicate: existing bullet contains new or vice versa
        if any(n in e or e in n for e in existing_norms if len(e) > 20 and len(n) > 20):
            continue
        kept.append(b)
        existing_norms.add(n)
    return "\n".join(kept)


def _section_exists(text: str, section: str) -> bool:
    heading = section.strip().lstrip("#").strip()
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE | re.IGNORECASE)
    return bool(pattern.search(text))


def _append_section(text: str, section: str | None, content: str) -> str:
    if section:
        heading = section.strip().lstrip("#").strip()
        pattern = re.compile(
            rf"(^##\s+{re.escape(heading)}\s*\n)([\s\S]*?)(?=^##\s+|\Z)",
            re.MULTILINE | re.IGNORECASE,
        )
        m = pattern.search(text)
        if m:
            body = m.group(2)
            body_clean = "\n".join(
                ln for ln in body.splitlines() if not is_placeholder_line(ln)
            )
            new_bullets = _filter_new_bullets(body_clean, content)
            if not new_bullets.strip():
                # still scrub placeholders if any
                cleaned = strip_placeholders(
                    text[: m.start()] + m.group(1) + body_clean.rstrip() + "\n\n" + text[m.end() :]
                )
                return cleaned if cleaned != strip_placeholders(text) else text
            new_body = body_clean.rstrip()
            if new_body:
                new_body = new_body + "\n\n" + new_bullets + "\n"
            else:
                new_body = new_bullets + "\n"
            rebuilt = text[: m.start()] + m.group(1) + new_body + "\n" + text[m.end() :]
            return strip_placeholders(rebuilt)

        # create section
        new_bullets = _filter_new_bullets("", content)
        if not new_bullets.strip():
            return strip_placeholders(text)
        return strip_placeholders(
            text.rstrip() + f"\n\n## {heading}\n\n{new_bullets}\n"
        )

    new_bullets = _filter_new_bullets(text, content)
    if not new_bullets.strip():
        return strip_placeholders(text)
    return strip_placeholders(text.rstrip() + "\n\n" + new_bullets + "\n")


def _replace_section(text: str, section: str, content: str) -> str:
    heading = section.strip().lstrip("#").strip()
    pattern = re.compile(
        rf"(^##\s+{re.escape(heading)}\s*\n)([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.IGNORECASE,
    )
    bullets = "\n".join(_content_bullets(content)) + "\n"
    if pattern.search(text):
        return strip_placeholders(pattern.sub(rf"\1{bullets}\n", text, count=1))
    return strip_placeholders(text.rstrip() + f"\n\n## {heading}\n\n{bullets}\n")


def prepare_unit(
    repo_root: Path,
    unit: KnowledgeUnit,
    *,
    existing_dirs: list[str] | None = None,
) -> KnowledgeUnit:
    """Normalize path/section/content before apply."""
    dirs = existing_dirs if existing_dirs is not None else list_repo_dirs(repo_root)
    content = unit.content
    if contains_secret(content):
        content = redact(content)
    path = resolve_unit_path(repo_root, unit.path, existing_dirs=dirs)
    section = canonicalize_section(unit.kind, unit.section)
    # If content is clearly usage but kind is dev (mixed), leave kind as declared —
    # section canonicalize already steers headings.
    return unit.model_copy(update={"path": path, "section": section, "content": content})


def apply_unit(
    repo_root: Path,
    unit: KnowledgeUnit,
    *,
    existing_dirs: list[str] | None = None,
) -> ApplyChange | None:
    dirs = existing_dirs if existing_dirs is not None else list_repo_dirs(repo_root)
    unit = prepare_unit(repo_root, unit, existing_dirs=dirs)

    path = target_file(repo_root, unit, existing_dirs=dirs)
    try:
        path.relative_to(repo_root.resolve())
    except ValueError:
        return None

    # Only create parent dirs that already exist as module roots (or root).
    # resolve_unit_path already snapped to existing dirs, so parent should exist.
    if not path.parent.exists() and path.parent != repo_root.resolve():
        return None

    existing = _ensure_file(path, unit.kind)
    if unit.action == "replace_section" and unit.section:
        new_text = _replace_section(existing, unit.section, unit.content)
    else:
        new_text = _append_section(existing, unit.section, unit.content)

    new_text = strip_placeholders(new_text)
    if new_text == strip_placeholders(existing) and path.exists():
        # no material change
        if new_text == existing:
            return None
        # placeholders cleaned only
        path.write_text(new_text if new_text.endswith("\n") else new_text + "\n", encoding="utf-8")
        return ApplyChange(
            path=path,
            kind=unit.kind,
            action="scrub",
            section=unit.section,
            bytes_written=len(new_text.encode("utf-8")),
        )

    if new_text == existing:
        return None
    path.write_text(new_text if new_text.endswith("\n") else new_text + "\n", encoding="utf-8")
    return ApplyChange(
        path=path,
        kind=unit.kind,
        action=unit.action,
        section=unit.section,
        bytes_written=len(new_text.encode("utf-8")),
    )


def apply_result(
    repo_root: Path,
    result: ExtractionResult,
    *,
    min_confidence: set[str] | None = None,
) -> list[ApplyChange]:
    allowed = min_confidence or {"high", "medium"}
    dirs = list_repo_dirs(repo_root)
    changes: list[ApplyChange] = []
    for unit in result.units:
        if unit.confidence not in allowed:
            continue
        ch = apply_unit(repo_root, unit, existing_dirs=dirs)
        if ch:
            changes.append(ch)
    return changes
