"""Claude Code session importers.

- history.jsonl: flat user prompts (~/.claude/history.jsonl)
- project jsonl: full sessions when present (~/.claude/projects/<id>/*.jsonl)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from devmemory.redaction import contains_secret, redact
from devmemory.sources.base import SessionRecord


def _default_history() -> Path:
    return Path.home() / ".claude" / "history.jsonl"


def _default_projects() -> Path:
    return Path.home() / ".claude" / "projects"


def _encode_project_path(repo_root: Path) -> str:
    # Claude encodes absolute paths: /Users/foo/bar -> -Users-foo-bar
    abs_path = str(repo_root.resolve())
    return abs_path.replace("/", "-")


class ClaudeHistorySource:
    def __init__(self, history_path: Path | None = None) -> None:
        self.history_path = history_path or _default_history()

    def list_sessions(
        self,
        *,
        project_filter: str | None = None,
        limit: int = 0,
    ) -> list[SessionRecord]:
        if not self.history_path.exists():
            return []
        out: list[SessionRecord] = []
        with self.history_path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = entry.get("display") or entry.get("text") or ""
                if not text or len(text.strip()) < 10:
                    continue
                if contains_secret(text):
                    text = redact(text)
                project = entry.get("project") or ""
                if project_filter and project_filter not in project:
                    continue
                sid = str(entry.get("sessionId") or entry.get("session_id") or "")
                if not sid:
                    # synthesize stable id from project+timestamp+hash of text head
                    ts = entry.get("timestamp", "")
                    sid = f"history-{ts}-{abs(hash(text[:80])) % 10_000_000}"
                out.append(
                    SessionRecord(
                        session_id=sid,
                        source="claude-history",
                        project=project,
                        timestamp=entry.get("timestamp", ""),
                        text=text.strip(),
                        path=self.history_path,
                        meta={"raw_keys": list(entry.keys())},
                    )
                )
                if limit and len(out) >= limit:
                    break
        return out


class ClaudeProjectSource:
    def __init__(self, projects_dir: Path | None = None) -> None:
        self.projects_dir = projects_dir or _default_projects()

    def list_for_repo(
        self,
        repo_root: Path,
        *,
        limit: int = 0,
    ) -> list[SessionRecord]:
        if not self.projects_dir.exists():
            return []
        encoded = _encode_project_path(repo_root)
        # exact or partial match (path suffixes)
        candidates = [
            d
            for d in self.projects_dir.iterdir()
            if d.is_dir() and (d.name == encoded or encoded.endswith(d.name) or d.name.endswith(encoded[-40:]))
        ]
        # also try any dir whose name contains the repo folder name
        repo_name = repo_root.name
        if not candidates:
            candidates = [
                d
                for d in self.projects_dir.iterdir()
                if d.is_dir() and repo_name in d.name
            ]
        out: list[SessionRecord] = []
        for d in candidates:
            out.extend(self._read_project_dir(d, limit=0))
            if limit and len(out) >= limit:
                return out[:limit]
        return out[:limit] if limit else out

    def _read_project_dir(self, project_dir: Path, *, limit: int) -> list[SessionRecord]:
        out: list[SessionRecord] = []
        for jsonl in sorted(project_dir.glob("*.jsonl")):
            text_parts: list[str] = []
            with jsonl.open(encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    chunk = _extract_message_text(entry)
                    if chunk:
                        if contains_secret(chunk):
                            chunk = redact(chunk)
                        text_parts.append(chunk)
            if not text_parts:
                continue
            body = "\n\n".join(text_parts)
            if len(body.strip()) < 20:
                continue
            out.append(
                SessionRecord(
                    session_id=jsonl.stem,
                    source="claude-project",
                    project=project_dir.name,
                    timestamp=jsonl.stat().st_mtime,
                    text=body,
                    path=jsonl,
                )
            )
            if limit and len(out) >= limit:
                break
        return out


def _extract_message_text(entry: dict) -> str:
    """Best-effort extract human-readable text from a Claude session line."""
    t = entry.get("type") or entry.get("subtype") or ""
    msg = entry.get("message")
    if isinstance(msg, dict):
        role = msg.get("role") or ""
        content = msg.get("content")
        text = _content_to_text(content)
        if text:
            return f"[{role or t}] {text}"
    # some lines store text directly
    for key in ("text", "content", "display", "summary"):
        v = entry.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, list):
            joined = _content_to_text(v)
            if joined:
                return joined
    return ""


def _content_to_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                if block.get("type") == "text" and block.get("text"):
                    parts.append(str(block["text"]))
                elif "text" in block:
                    parts.append(str(block["text"]))
        return "\n".join(p for p in parts if p).strip()
    return ""


def discover_claude_sessions(
    repo_root: Path,
    *,
    history_path: Path | None = None,
    projects_dir: Path | None = None,
    limit: int = 50,
) -> list[SessionRecord]:
    """Discover sessions relevant to repo_root (history + project files)."""
    root = repo_root.resolve()
    root_str = str(root)
    hist = ClaudeHistorySource(history_path)
    # filter history entries whose project path matches this repo
    history = hist.list_sessions(project_filter=root_str, limit=0)
    if not history:
        # softer match: repo name in project path
        history = [
            s
            for s in hist.list_sessions(limit=0)
            if root.name in (s.project or "") or root_str in (s.project or "")
        ]
    projects = ClaudeProjectSource(projects_dir).list_for_repo(root, limit=0)

    # Prefer project sessions (richer); append history-only ids not already covered
    seen: set[str] = set()
    merged: list[SessionRecord] = []
    for s in projects + history:
        if s.session_id in seen:
            continue
        seen.add(s.session_id)
        merged.append(s)
    # newest first when timestamps comparable
    def sort_key(s: SessionRecord):
        return str(s.timestamp)

    merged.sort(key=sort_key, reverse=True)
    return merged[:limit] if limit else merged
