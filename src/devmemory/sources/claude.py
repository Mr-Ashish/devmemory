"""Claude Code session importers.

- history.jsonl: flat user prompts (~/.claude/history.jsonl), grouped by sessionId
- project jsonl: full sessions when present (~/.claude/projects/<encoded-path>/*.jsonl)

Override paths with DEVMEMORY_CLAUDE_HISTORY / DEVMEMORY_CLAUDE_PROJECTS for tests.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

from devmemory.redaction import contains_secret, redact
from devmemory.sources.base import SessionRecord


def _default_history() -> Path:
    env = os.environ.get("DEVMEMORY_CLAUDE_HISTORY", "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / ".claude" / "history.jsonl"


def _default_projects() -> Path:
    env = os.environ.get("DEVMEMORY_CLAUDE_PROJECTS", "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / ".claude" / "projects"


def encode_project_path(repo_root: Path) -> str:
    """Claude encodes absolute paths: /Users/foo/bar -> -Users-foo-bar."""
    abs_path = str(repo_root.resolve())
    return abs_path.replace("/", "-")


# Back-compat alias used elsewhere / tests
_encode_project_path = encode_project_path


def project_matches_repo(project: str, repo_root: Path) -> bool:
    """True when a Claude history/project path is relevant to repo_root (cwd).

    Matches:
    - exact absolute path of the repo
    - sessions started in a subdirectory of the repo
    """
    if not project:
        return False
    root_n = str(repo_root.resolve()).rstrip("/")
    proj = str(project).rstrip("/")
    if proj == root_n:
        return True
    # session started inside the repo tree
    if proj.startswith(root_n + "/"):
        return True
    return False


def _ts_sort_key(ts: str | float | int) -> float:
    """Normalize to unix seconds (Claude history often uses epoch ms)."""
    if isinstance(ts, (int, float)):
        val = float(ts)
    else:
        s = str(ts).strip()
        if not s:
            return 0.0
        try:
            val = float(s)
        except ValueError:
            return 0.0
    # epoch milliseconds → seconds
    if val > 1_000_000_000_000:  # ~2001-09 in ms
        val = val / 1000.0
    return val


class ClaudeHistorySource:
    def __init__(self, history_path: Path | None = None) -> None:
        self.history_path = history_path or _default_history()

    def list_sessions(
        self,
        *,
        project_filter: str | None = None,
        repo_root: Path | None = None,
        limit: int = 0,
    ) -> list[SessionRecord]:
        """List sessions grouped by sessionId (multi-turn history → one record)."""
        if not self.history_path.exists():
            return []

        # session_id -> list of (timestamp, text, project, raw_keys)
        buckets: dict[str, list[tuple[float | str, str, str, list]]] = defaultdict(list)

        with self.history_path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = entry.get("display") or entry.get("text") or ""
                if not isinstance(text, str) or len(text.strip()) < 10:
                    continue
                if contains_secret(text):
                    text = redact(text)
                project = entry.get("project") or ""
                if not isinstance(project, str):
                    project = str(project)

                if repo_root is not None:
                    if not project_matches_repo(project, repo_root):
                        continue
                elif project_filter and project_filter not in project:
                    continue

                sid = str(entry.get("sessionId") or entry.get("session_id") or "")
                ts = entry.get("timestamp", "")
                if not sid:
                    sid = f"history-{ts}-{abs(hash(text[:80])) % 10_000_000}"

                buckets[sid].append((ts, text.strip(), project, list(entry.keys())))

        out: list[SessionRecord] = []
        for sid, parts in buckets.items():
            # chronological within session
            parts_sorted = sorted(parts, key=lambda p: _ts_sort_key(p[0]))
            texts = [p[1] for p in parts_sorted]
            body = "\n\n".join(texts)
            if len(body.strip()) < 10:
                continue
            last_ts = parts_sorted[-1][0]
            project = parts_sorted[-1][2]
            out.append(
                SessionRecord(
                    session_id=sid,
                    source="claude-history",
                    project=project,
                    timestamp=last_ts,
                    text=body,
                    path=self.history_path,
                    meta={
                        "turns": len(parts_sorted),
                        "raw_keys": parts_sorted[-1][3],
                    },
                )
            )

        out.sort(key=lambda s: _ts_sort_key(s.timestamp), reverse=True)
        if limit:
            return out[:limit]
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
        encoded = encode_project_path(repo_root)
        repo_name = repo_root.name
        candidates: list[Path] = []
        for d in self.projects_dir.iterdir():
            if not d.is_dir():
                continue
            name = d.name
            if name == encoded:
                candidates.append(d)
                continue
            # partial: encoded path contains this dir name or vice versa
            if encoded.endswith(name) or name.endswith(encoded[-min(40, len(encoded)) :]):
                candidates.append(d)
                continue
            # decode-ish: dir name contains repo folder and a slice of parent
            if repo_name in name and "Users" in name:
                # prefer dirs that look like this absolute path
                if encoded in name or name in encoded or repo_name == name.split("-")[-1]:
                    candidates.append(d)

        # de-dupe while preserving order
        seen_dirs: set[Path] = set()
        uniq: list[Path] = []
        for d in candidates:
            rp = d.resolve()
            if rp not in seen_dirs:
                seen_dirs.add(rp)
                uniq.append(d)

        out: list[SessionRecord] = []
        for d in uniq:
            out.extend(self._read_project_dir(d, limit=0))
            if limit and len(out) >= limit:
                break
        out.sort(key=lambda s: _ts_sort_key(s.timestamp), reverse=True)
        return out[:limit] if limit else out

    def _read_project_dir(self, project_dir: Path, *, limit: int) -> list[SessionRecord]:
        out: list[SessionRecord] = []
        jsonl_files = sorted(
            project_dir.glob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for jsonl in jsonl_files:
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
                    meta={"turns": len(text_parts), "project_dir": str(project_dir)},
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
    """Discover sessions relevant to repo_root (project JSONL + history).

    Project sessions (richer multi-role transcripts) are preferred when both
    sources share a session id. Results are newest-first.
    """
    root = repo_root.resolve()
    hist = ClaudeHistorySource(history_path)
    history = hist.list_sessions(repo_root=root, limit=0)
    projects = ClaudeProjectSource(projects_dir).list_for_repo(root, limit=0)

    # Prefer project sessions (richer); append history-only ids not already covered
    seen: set[str] = set()
    merged: list[SessionRecord] = []
    for s in projects + history:
        if s.session_id in seen:
            continue
        seen.add(s.session_id)
        merged.append(s)

    merged.sort(key=lambda s: _ts_sort_key(s.timestamp), reverse=True)
    return merged[:limit] if limit else merged


def pick_latest_unprocessed(
    sessions: list[SessionRecord],
    *,
    is_processed,
) -> SessionRecord | None:
    """Return newest unprocessed session, or None."""
    for s in sessions:
        if not is_processed(s.session_id):
            return s
    return None
