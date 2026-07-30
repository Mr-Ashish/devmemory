"""Apply knowledge units to colocated DEV.md / USAGE.md files."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
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
    applied: bool = True  # False when planned (dry-run), True after write
    unit_path: str | None = None  # resolved module path for the unit


@dataclass
class FileDiff:
    """One knowledge file's before/after for git-style preview (R4)."""

    path: Path
    rel_path: str
    old_text: str
    new_text: str
    is_new: bool = False

    def unified(self, *, context: int = 3) -> str:
        """Unified diff with a/ b/ prefixes (git-style)."""
        old = self.old_text.splitlines(keepends=True)
        new = self.new_text.splitlines(keepends=True)
        # Normalize trailing newline for stable diffs
        if old and not old[-1].endswith("\n"):
            old[-1] = old[-1] + "\n"
        if new and not new[-1].endswith("\n"):
            new[-1] = new[-1] + "\n"
        from_label = "/dev/null" if self.is_new else f"a/{self.rel_path}"
        to_label = f"b/{self.rel_path}"
        lines = list(
            difflib.unified_diff(
                old,
                new,
                fromfile=from_label,
                tofile=to_label,
                n=context,
            )
        )
        if not lines:
            return ""
        # git-style file headers when creating a new file
        if self.is_new and lines:
            header = [
                f"diff --git a/{self.rel_path} b/{self.rel_path}\n",
                "new file mode 100644\n",
            ]
            return "".join(header + lines)
        return f"diff --git a/{self.rel_path} b/{self.rel_path}\n" + "".join(lines)

    def stats(self) -> tuple[int, int]:
        """Return (lines_added, lines_removed) from the unified hunk body."""
        added = removed = 0
        for ln in self.unified().splitlines():
            if ln.startswith("+++") or ln.startswith("---") or ln.startswith("@@"):
                continue
            if ln.startswith("diff ") or ln.startswith("new file"):
                continue
            if ln.startswith("+"):
                added += 1
            elif ln.startswith("-"):
                removed += 1
        return added, removed


@dataclass
class PreviewPlan:
    """Sequential dry-run plan with unified knowledge diffs (R4)."""

    changes: list[ApplyChange] = field(default_factory=list)
    files: list[FileDiff] = field(default_factory=list)

    def unified_text(self) -> str:
        parts = [fd.unified() for fd in self.files]
        parts = [p for p in parts if p.strip()]
        if not parts:
            return ""
        return "\n".join(parts).rstrip() + "\n"

    def stats(self) -> dict[str, int]:
        files = len(self.files)
        added = removed = 0
        for fd in self.files:
            a, r = fd.stats()
            added += a
            removed += r
        return {
            "files": files,
            "lines_added": added,
            "lines_removed": removed,
            "changes": len(self.changes),
        }


def knowledge_filename(kind: str) -> str:
    return "DEV.md" if kind == "dev" else "USAGE.md"


def target_file(repo_root: Path, unit: KnowledgeUnit, *, existing_dirs: list[str] | None = None) -> Path:
    resolved = resolve_unit_path(repo_root, unit.path, existing_dirs=existing_dirs)
    rel = Path(".") if resolved in (".", "") else Path(resolved)
    return (repo_root / rel / knowledge_filename(unit.kind)).resolve()


def _read_or_template(path: Path, kind: str) -> str:
    """Read existing knowledge file or return template body (no disk write)."""
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return DEV_TEMPLATE if kind == "dev" else USAGE_TEMPLATE


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
    s = re.sub(r"[`*_'\".,;:()\[\]{}]", "", s)
    return s


def _stem(tok: str) -> str:
    t = tok
    # longest-first; avoid over-stemming ("existing" must not become "exis")
    for suf in ("ations", "ation", "tions", "iness", "ingly", "ing", "ers", "ies", "ied", "ed", "es", "s"):
        if len(t) > len(suf) + 3 and t.endswith(suf):
            return t[: -len(suf)]
    return t


def _token_set(norm: str) -> set[str]:
    return {_stem(t) for t in norm.split() if len(t) > 2}


def _near_duplicate(a: str, b: str, *, threshold: float = 0.52) -> bool:
    """True if two normalized bullets are the same claim (containment or Jaccard)."""
    if not a or not b:
        return False
    if a == b:
        return True
    if len(a) > 24 and len(b) > 24 and (a in b or b in a):
        return True
    ta, tb = _token_set(a), _token_set(b)
    if not ta or not tb:
        return False
    inter = len(ta & tb)
    union = len(ta | tb)
    if union == 0:
        return False
    jacc = inter / union
    smaller = min(len(ta), len(tb))
    cover = inter / smaller if smaller else 0.0
    return jacc >= threshold or cover >= 0.62


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
    """Return only bullets not already present (normalized / near-dupe)."""
    existing_norms = [
        _norm_bullet(ln)
        for ln in existing_section_body.splitlines()
        if ln.strip().startswith(("-", "*"))
    ]
    kept: list[str] = []
    for b in _content_bullets(content):
        n = _norm_bullet(b)
        if not n:
            continue
        if any(_near_duplicate(n, e) for e in existing_norms):
            continue
        kept.append(b)
        existing_norms.append(n)
    return "\n".join(kept)


def dedupe_section_bullets(body: str) -> str:
    """Drop near-duplicate bullets already inside a section body (first wins)."""
    out: list[str] = []
    norms: list[str] = []
    for ln in body.splitlines():
        if ln.strip().startswith(("-", "*")):
            n = _norm_bullet(ln)
            if n and any(_near_duplicate(n, e) for e in norms):
                continue
            if n:
                norms.append(n)
            out.append(ln)
        else:
            out.append(ln)
    return "\n".join(out)


def scrub_file_near_dupes(text: str) -> str:
    """Within each H2 section, keep first bullet when near-duplicates appear."""
    pattern = re.compile(
        r"(^##\s+[^\n]+\n)([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )

    def repl(m: re.Match) -> str:
        return m.group(1) + dedupe_section_bullets(m.group(2))

    return strip_placeholders(pattern.sub(repl, text))


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
            body_clean = dedupe_section_bullets(
                "\n".join(
                    ln for ln in body.splitlines() if not is_placeholder_line(ln)
                )
            )
            new_bullets = _filter_new_bullets(body_clean, content)
            if not new_bullets.strip():
                cleaned = strip_placeholders(
                    text[: m.start()]
                    + m.group(1)
                    + body_clean.rstrip()
                    + "\n\n"
                    + text[m.end() :]
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


def _compute_unit_text(
    repo_root: Path,
    unit: KnowledgeUnit,
    *,
    existing_dirs: list[str] | None = None,
    existing_override: str | None = None,
) -> tuple[KnowledgeUnit, Path, str, str, str] | None:
    """Plan one unit write.

    Returns (prepared_unit, target_path, existing_text, new_text, action)
    or None when the unit is a no-op / out of bounds.
    Does not touch the filesystem (except reading existing files).

    When ``existing_override`` is set, merge against that in-memory body
    (sequential multi-unit preview) instead of re-reading disk.
    """
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

    if existing_override is not None:
        existing = existing_override
    else:
        existing = _read_or_template(path, unit.kind)
    if unit.action == "replace_section" and unit.section:
        new_text = _replace_section(existing, unit.section, unit.content)
        action = unit.action
    else:
        new_text = _append_section(existing, unit.section, unit.content)
        action = unit.action

    new_text = strip_placeholders(new_text)
    # existing_override means we already have a simulated body (possibly template).
    has_prior = path.exists() or existing_override is not None
    if new_text == strip_placeholders(existing) and has_prior:
        if new_text == existing:
            return None
        # placeholders cleaned only
        return unit, path, existing, new_text, "scrub"

    if new_text == existing:
        return None
    return unit, path, existing, new_text, action


def plan_unit(
    repo_root: Path,
    unit: KnowledgeUnit,
    *,
    existing_dirs: list[str] | None = None,
) -> ApplyChange | None:
    """Dry-run a single unit: proposed path/section without writing."""
    computed = _compute_unit_text(repo_root, unit, existing_dirs=existing_dirs)
    if computed is None:
        return None
    prepared, path, _existing, new_text, action = computed
    final = new_text if new_text.endswith("\n") else new_text + "\n"
    return ApplyChange(
        path=path,
        kind=prepared.kind,
        action=action,
        section=prepared.section,
        bytes_written=len(final.encode("utf-8")),
        applied=False,
        unit_path=prepared.path,
    )


def apply_unit(
    repo_root: Path,
    unit: KnowledgeUnit,
    *,
    existing_dirs: list[str] | None = None,
) -> ApplyChange | None:
    computed = _compute_unit_text(repo_root, unit, existing_dirs=existing_dirs)
    if computed is None:
        return None
    prepared, path, _existing, new_text, action = computed
    final = new_text if new_text.endswith("\n") else new_text + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(final, encoding="utf-8")
    return ApplyChange(
        path=path,
        kind=prepared.kind,
        action=action,
        section=prepared.section,
        bytes_written=len(final.encode("utf-8")),
        applied=True,
        unit_path=prepared.path,
    )


def plan_preview(
    repo_root: Path,
    result: ExtractionResult,
    *,
    min_confidence: set[str] | None = None,
) -> PreviewPlan:
    """Sequential dry-run: ApplyChange list + unified git-style diffs (R4).

    Units are applied in memory in order so multi-unit merges into the same
    DEV.md/USAGE.md produce one accurate file-level diff (not N independent
    plans each against the original disk body).
    """
    allowed = min_confidence or {"high", "medium"}
    dirs = list_repo_dirs(repo_root)
    root = repo_root.resolve()

    # path -> original disk body (empty string if file does not exist yet)
    originals: dict[Path, str] = {}
    # path -> current simulated body
    virtual: dict[Path, str] = {}
    # path -> last unit kind (for template)
    kinds: dict[Path, str] = {}
    changes: list[ApplyChange] = []

    for unit in result.units:
        if unit.confidence not in allowed:
            continue
        prepared = prepare_unit(repo_root, unit, existing_dirs=dirs)
        path = target_file(repo_root, prepared, existing_dirs=dirs)
        try:
            path.relative_to(root)
        except ValueError:
            continue
        if not path.parent.exists() and path.parent != root:
            continue

        if path not in originals:
            if path.exists():
                originals[path] = path.read_text(encoding="utf-8", errors="replace")
            else:
                originals[path] = ""  # true empty for new-file diff
            # Start virtual from disk or template
            virtual[path] = (
                originals[path]
                if originals[path]
                else (DEV_TEMPLATE if prepared.kind == "dev" else USAGE_TEMPLATE)
            )
            kinds[path] = prepared.kind

        computed = _compute_unit_text(
            repo_root,
            unit,
            existing_dirs=dirs,
            existing_override=virtual[path],
        )
        if computed is None:
            continue
        prep, tpath, _existing, new_text, action = computed
        final = new_text if new_text.endswith("\n") else new_text + "\n"
        virtual[tpath] = final
        kinds[tpath] = prep.kind
        changes.append(
            ApplyChange(
                path=tpath,
                kind=prep.kind,
                action=action,
                section=prep.section,
                bytes_written=len(final.encode("utf-8")),
                applied=False,
                unit_path=prep.path,
            )
        )

    files: list[FileDiff] = []
    for path, new_body in sorted(virtual.items(), key=lambda kv: str(kv[0])):
        old_body = originals.get(path, "")
        # Compare against what was on disk (empty if new); normalize trailing nl
        old_cmp = old_body if old_body.endswith("\n") or old_body == "" else old_body + "\n"
        new_cmp = new_body if new_body.endswith("\n") else new_body + "\n"
        # If file did not exist, old for diff is empty (new file), not the template
        is_new = not path.exists() and originals.get(path, "") == ""
        if is_new:
            old_cmp = ""
        if old_cmp == new_cmp:
            continue
        try:
            rel = str(path.relative_to(root))
        except ValueError:
            rel = str(path)
        files.append(
            FileDiff(
                path=path,
                rel_path=rel,
                old_text=old_cmp,
                new_text=new_cmp,
                is_new=is_new,
            )
        )

    return PreviewPlan(changes=changes, files=files)


def plan_result(
    repo_root: Path,
    result: ExtractionResult,
    *,
    min_confidence: set[str] | None = None,
) -> list[ApplyChange]:
    """Dry-run all units: proposed knowledge file paths without writing.

    Uses sequential in-memory preview (same as plan_preview) so multi-unit
    merges match what --apply would write.
    """
    return plan_preview(repo_root, result, min_confidence=min_confidence).changes


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
