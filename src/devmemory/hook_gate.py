"""Gate SessionEnd hook extracts on real tool edits (R7.5).

Chat-only Claude sessions should not trigger knowledge extract noise.
Detect Write/Edit-class tool uses in a Claude Code transcript JSONL (or raw text).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

# Claude Code / agent tools that mutate the workspace (durable knowledge signal).
EDIT_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "Write",
        "Edit",
        "MultiEdit",
        "NotebookEdit",
        "Create",
        "create_file",
        "str_replace",
        "apply_patch",
        "ApplyPatch",
        "Delete",
        "delete_file",
    }
)

# Fast path for large JSONL without full parse of every message.
_TOOL_NAME_RE = re.compile(
    r'"(?:name|tool)"\s*:\s*"(?P<n>'
    + "|".join(re.escape(t) for t in sorted(EDIT_TOOL_NAMES, key=len, reverse=True))
    + r')"',
    re.IGNORECASE,
)


def _norm_tool(name: str | None) -> str:
    return (name or "").strip()


def _is_edit_tool(name: str | None) -> bool:
    n = _norm_tool(name)
    if not n:
        return False
    if n in EDIT_TOOL_NAMES:
        return True
    # case-insensitive fallback
    lower = {t.lower() for t in EDIT_TOOL_NAMES}
    return n.lower() in lower


def _walk_for_tools(obj: Any) -> Iterable[str]:
    """Yield tool names from nested Claude / agent JSON shapes."""
    if isinstance(obj, dict):
        # Claude message content blocks
        t = obj.get("type")
        if t == "tool_use" and obj.get("name"):
            yield str(obj["name"])
        # tool_complete / simplified traces
        if obj.get("tool") and (
            obj.get("event") in (None, "tool_complete", "tool_start", "tool_use")
            or "tool" in obj
        ):
            # only treat as tool name when looks like a tool field
            if isinstance(obj.get("tool"), str):
                yield str(obj["tool"])
        if obj.get("name") and t in ("tool_use", "tool_result", None):
            # avoid treating every "name" as a tool — require tool-ish context
            if t == "tool_use" or obj.get("input") is not None or obj.get("id", "").startswith("tool"):
                yield str(obj["name"])
        for v in obj.values():
            yield from _walk_for_tools(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_for_tools(item)


def text_has_tool_edits(text: str) -> bool:
    """True if raw transcript/session text mentions an edit-class tool use."""
    if not text or not text.strip():
        return False
    if _TOOL_NAME_RE.search(text):
        return True
    # loose markers used in some export formats
    for name in EDIT_TOOL_NAMES:
        if f"tool_use" in text and name in text:
            return True
    return False


def record_has_tool_edits(obj: Any) -> bool:
    for name in _walk_for_tools(obj):
        if _is_edit_tool(name):
            return True
    return False


def transcript_has_tool_edits(
    path: Path | str | None,
    *,
    max_bytes: int = 8_000_000,
) -> bool | None:
    """Inspect a Claude transcript JSONL/JSON file for edit-class tools.

    Returns:
      True  — at least one edit tool found
      False — file readable, no edit tools
      None  — path missing / unreadable (caller decides allow vs skip)
    """
    if path is None:
        return None
    p = Path(path).expanduser()
    if not p.is_file():
        return None
    try:
        size = p.stat().st_size
        # Fast path: scan raw bytes/text for tool name markers first
        with p.open("r", encoding="utf-8", errors="replace") as f:
            if size > max_bytes:
                chunk = f.read(max_bytes)
                if text_has_tool_edits(chunk):
                    return True
                # still try line-wise on the cap
                f.seek(0)
            found_any_json = False
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # cheap reject
                if "tool" not in line.lower() and "Write" not in line and "Edit" not in line:
                    continue
                if text_has_tool_edits(line):
                    return True
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                found_any_json = True
                if record_has_tool_edits(obj):
                    return True
            # whole-file JSON (not JSONL)
            if not found_any_json and size <= max_bytes:
                f.seek(0)
                body = f.read()
                try:
                    obj = json.loads(body)
                except json.JSONDecodeError:
                    return text_has_tool_edits(body)
                return record_has_tool_edits(obj)
            return False
    except OSError:
        return None


def resolve_transcript_path(
    *,
    hook_transcript: str | None = None,
    session_id: str | None = None,
    repo_root: Path | None = None,
    projects_dir: Path | None = None,
) -> Path | None:
    """Prefer hook-provided transcript; else Claude projects/<encoded>/session.jsonl."""
    if hook_transcript:
        p = Path(hook_transcript).expanduser()
        if p.is_file():
            return p
    if not session_id or not repo_root:
        return None
    from devmemory.sources.claude import encode_project_path, _default_projects

    root = projects_dir or _default_projects()
    cand = root / encode_project_path(repo_root) / f"{session_id}.jsonl"
    if cand.is_file():
        return cand
    # some layouts nest deeper
    if root.is_dir():
        for p in root.rglob(f"{session_id}.jsonl"):
            return p
    return None


def should_run_extract_for_session(
    *,
    require_edits: bool = True,
    hook_transcript: str | None = None,
    session_id: str | None = None,
    repo_root: Path | None = None,
    projects_dir: Path | None = None,
) -> tuple[bool, str]:
    """Decide whether the SessionEnd hook should run extract.

    Returns (should_run, reason).
    """
    if not require_edits:
        return True, "require_edits=off"

    path = resolve_transcript_path(
        hook_transcript=hook_transcript,
        session_id=session_id,
        repo_root=repo_root,
        projects_dir=projects_dir,
    )
    if path is None:
        # Unknown — do not block habit loop when Claude does not supply a transcript.
        return True, "no_transcript_allow"

    result = transcript_has_tool_edits(path)
    if result is None:
        return True, f"transcript_unreadable_allow path={path}"
    if result:
        return True, f"tool_edits_present path={path.name}"
    return False, f"no_tool_edits path={path.name}"
