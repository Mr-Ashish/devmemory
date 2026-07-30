"""CI knowledge form validator (R7).

Validates colocated DEV.md / USAGE.md shape without transcripts or LLM:
H1, placeholders, empty H2s, glued headings, blocked trees, secrets.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from devmemory import __version__
from devmemory.paths import is_knowledge_blocked
from devmemory.redaction import contains_secret
from devmemory.sections import (
    DEV_SECTIONS,
    USAGE_SECTIONS,
    is_placeholder_line,
)

Status = Literal["ok", "warn", "fail", "info"]

_SKIP_DIR_PARTS = frozenset(
    {
        ".git",
        ".devmemory",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".tox",
        "dist",
        "build",
    }
)

_H1_DEV = re.compile(r"^#\s+DEV\b", re.IGNORECASE | re.MULTILINE)
_H1_USAGE = re.compile(r"^#\s+USAGE\b", re.IGNORECASE | re.MULTILINE)
_H2 = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Issue:
    path: str
    check: str
    status: Status
    message: str
    fix: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FileReport:
    path: str
    kind: str  # dev | usage
    issues: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.status == "fail" for i in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "kind": self.kind,
            "ok": self.ok,
            "issues": [i.to_dict() for i in self.issues],
        }


@dataclass
class ValidateReport:
    ok: bool
    repo: str
    version: str
    files: list[FileReport] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    file_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "repo": self.repo,
            "version": self.version,
            "file_count": self.file_count,
            "fail": [i.to_dict() for i in self.issues if i.status == "fail"],
            "warn": [i.to_dict() for i in self.issues if i.status == "warn"],
            "files": [f.to_dict() for f in self.files],
        }


def discover_knowledge_files(repo_root: Path) -> list[Path]:
    """Find DEV.md / USAGE.md under repo, skipping tooling trees."""
    root = repo_root.resolve()
    found: list[Path] = []
    for name in ("DEV.md", "USAGE.md"):
        for p in root.rglob(name):
            try:
                rel_parts = p.relative_to(root).parts
            except ValueError:
                continue
            # skip if any parent dir is tooling/hidden
            if any(
                part in _SKIP_DIR_PARTS or part.startswith(".")
                for part in rel_parts[:-1]
            ):
                continue
            found.append(p.resolve())
    return sorted(set(found), key=lambda x: str(x))


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def _owner_rel(path: Path, root: Path) -> str:
    """Directory that owns the knowledge file (repo-relative)."""
    rel = Path(_rel(path, root))
    parent = rel.parent
    if str(parent) in (".", ""):
        return "."
    return str(parent).replace("\\", "/")


def validate_file(path: Path, *, repo_root: Path) -> FileReport:
    rel = _rel(path, repo_root)
    kind = "dev" if path.name.upper() == "DEV.MD" else "usage"
    report = FileReport(path=rel, kind=kind)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        report.issues.append(
            Issue(rel, "readable", "fail", f"cannot read: {e}", "fix permissions")
        )
        return report

    if not text.strip():
        report.issues.append(
            Issue(rel, "empty", "fail", "file is empty", "seed content or delete")
        )
        return report

    # blocked tree
    owner = _owner_rel(path, repo_root)
    if is_knowledge_blocked(owner):
        report.issues.append(
            Issue(
                rel,
                "blocked_path",
                "fail",
                f"knowledge under blocked tree '{owner}'",
                "move to a code module dir or delete",
            )
        )

    # H1
    if kind == "dev":
        if not _H1_DEV.search(text):
            report.issues.append(
                Issue(
                    rel,
                    "h1",
                    "fail",
                    "missing `# DEV` H1",
                    "start with `# DEV — engineering knowledge`",
                )
            )
    else:
        if not _H1_USAGE.search(text):
            report.issues.append(
                Issue(
                    rel,
                    "h1",
                    "fail",
                    "missing `# USAGE` H1",
                    "start with `# USAGE — operational knowledge`",
                )
            )

    # placeholders
    for i, ln in enumerate(text.splitlines(), 1):
        if is_placeholder_line(ln):
            report.issues.append(
                Issue(
                    rel,
                    "placeholder",
                    "fail",
                    f"line {i}: placeholder left in file",
                    "re-run apply or fill real content",
                )
            )
            break  # one is enough for CI noise

    # glued ## — real section heading stuck mid-line (ignore inline `## foo` prose)
    _canon = "|".join(
        re.escape(s) for s in (DEV_SECTIONS if kind == "dev" else USAGE_SECTIONS)
    )
    glue_re = re.compile(rf"(?<![`#])##\s+(?:{_canon})\b")
    for i, ln in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*##\s+\S", ln):
            continue
        if glue_re.search(ln):
            report.issues.append(
                Issue(
                    rel,
                    "glued_h2",
                    "fail",
                    f"line {i}: H2 glued to previous text",
                    "ensure blank line before each `## ` heading",
                )
            )
            break

    # empty H2 sections
    lines = text.splitlines()
    h2_idx = [i for i, ln in enumerate(lines) if re.match(r"^##\s+\S", ln)]
    for n, start in enumerate(h2_idx):
        end = h2_idx[n + 1] if n + 1 < len(h2_idx) else len(lines)
        body = lines[start + 1 : end]
        if not any(ln.strip() for ln in body):
            title = lines[start].lstrip("#").strip()
            report.issues.append(
                Issue(
                    rel,
                    "empty_h2",
                    "fail",
                    f"empty H2 section: {title}",
                    "add bullets or drop the heading",
                )
            )

    # unknown sections (warn)
    allowed = set(DEV_SECTIONS if kind == "dev" else USAGE_SECTIONS)
    for m in _H2.finditer(text):
        title = m.group(1).strip()
        if title not in allowed:
            report.issues.append(
                Issue(
                    rel,
                    "unknown_section",
                    "warn",
                    f"non-canonical H2: {title}",
                    f"prefer one of: {', '.join(sorted(allowed))}",
                )
            )

    # secrets
    if contains_secret(text):
        report.issues.append(
            Issue(
                rel,
                "secret",
                "fail",
                "possible secret pattern in knowledge file",
                "redact keys/tokens before commit",
            )
        )

    # content: at least one bullet somewhere if file has more than H1/blockquote
    bullets = [ln for ln in lines if ln.strip().startswith(("-", "*"))]
    if not bullets and h2_idx:
        report.issues.append(
            Issue(
                rel,
                "no_bullets",
                "warn",
                "has H2 sections but no markdown bullets",
                "add durable `-` bullets under sections",
            )
        )

    if not report.issues:
        report.issues.append(
            Issue(rel, "form", "ok", "form ok", "")
        )
    return report


def run_validate(repo_root: Path) -> ValidateReport:
    root = repo_root.resolve()
    paths = discover_knowledge_files(root)
    files = [validate_file(p, repo_root=root) for p in paths]
    all_issues: list[Issue] = []
    for fr in files:
        for iss in fr.issues:
            if iss.status != "ok":
                all_issues.append(iss)
    has_fail = any(i.status == "fail" for i in all_issues)
    return ValidateReport(
        ok=not has_fail,
        repo=str(root),
        version=__version__,
        files=files,
        issues=all_issues,
        file_count=len(files),
    )
