"""Path resolution: map knowledge units onto real repo directories."""

from __future__ import annotations

import os
import re
from pathlib import Path

_BLOCKED = frozenset({".git", ".devmemory", ".venv", "venv", "node_modules", "__pycache__"})

_PATH_IN_TEXT = re.compile(
    r"(?P<p>(?:src|lib|apps|packages|modules|addons|services|backend|frontend|"
    r"internal|cmd|pkg|app)(?:/[A-Za-z0-9_.\-]+){1,6}/?)"
)


def list_repo_dirs(repo_root: Path, *, max_dirs: int = 300) -> list[str]:
    """Return repo-relative directory paths (including '.')."""
    root = repo_root.resolve()
    out: list[str] = ["."]
    for dirpath, dirnames, _filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        parts = rel.parts
        if any(p in _BLOCKED or p.startswith(".") for p in parts):
            dirnames[:] = []
            continue
        if len(parts) > 4:
            dirnames[:] = []
            continue
        if str(rel) != ".":
            out.append(str(rel).replace("\\", "/"))
        if len(out) >= max_dirs:
            break
    return out


def path_exists_dir(repo_root: Path, rel: str) -> bool:
    if rel in (".", "", None):
        return True
    p = (repo_root / rel).resolve()
    try:
        p.relative_to(repo_root.resolve())
    except ValueError:
        return False
    return p.is_dir()


def resolve_unit_path(
    repo_root: Path,
    path: str,
    *,
    existing_dirs: list[str] | None = None,
) -> str:
    """Snap a unit path to an existing directory; never invent deep trees."""
    raw = (path or ".").strip().replace("\\", "/")
    while raw.startswith("./"):
        raw = raw[2:]
    raw = raw.strip("/") or "."
    if ".." in raw.split("/"):
        return "."
    if raw == ".":
        return "."

    dirs = existing_dirs if existing_dirs is not None else list_repo_dirs(repo_root)
    dir_set = set(dirs)

    candidate = raw
    full = repo_root / candidate
    if full.is_file():
        parent = str(Path(candidate).parent).replace("\\", "/")
        candidate = "." if parent in (".", "") else parent

    if candidate in dir_set or path_exists_dir(repo_root, candidate):
        return candidate

    parts = candidate.split("/")
    for i in range(len(parts), 0, -1):
        prefix = "/".join(parts[:i])
        if prefix in dir_set or path_exists_dir(repo_root, prefix):
            return prefix
    return "."


def infer_paths_from_text(text: str, existing_dirs: list[str]) -> list[str]:
    """Best-effort paths mentioned in session text that exist in the repo."""
    found: list[str] = []
    dir_set = set(existing_dirs)
    for m in _PATH_IN_TEXT.finditer(text or ""):
        p = m.group("p").rstrip("/")
        parts = p.split("/")
        for i in range(len(parts), 0, -1):
            prefix = "/".join(parts[:i])
            if prefix in dir_set and prefix not in found:
                found.append(prefix)
                break
    for d in existing_dirs:
        if d == ".":
            continue
        if d in (text or "") and d not in found:
            found.append(d)
    return found
