"""Poll Claude sessions for new unprocessed work (R8).

Backup habit loop when SessionEnd hook is not installed. Tracks seen session
fingerprints under .devmemory/watch.json (gitignored via .devmemory/*).
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from devmemory.hook_gate import should_run_extract_for_session
from devmemory.sources.base import SessionRecord
from devmemory.sources.claude import discover_claude_sessions
from devmemory.state import DevMemoryPaths, utc_now


@dataclass
class WatchHit:
    session_id: str
    source: str
    action: str  # extract | skip_processed | skip_seen | skip_no_edits | error
    detail: str = ""
    run_id: str | None = None
    units: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WatchCycle:
    at: str
    hits: list[WatchHit] = field(default_factory=list)
    discovered: int = 0
    extracted: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "at": self.at,
            "discovered": self.discovered,
            "extracted": self.extracted,
            "hits": [h.to_dict() for h in self.hits],
        }


def watch_state_path(paths: DevMemoryPaths) -> Path:
    return paths.home / "watch.json"


def read_watch_state(paths: DevMemoryPaths) -> dict[str, Any]:
    p = watch_state_path(paths)
    if not p.exists():
        return {"version": 1, "seen": {}}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "seen": {}}


def write_watch_state(paths: DevMemoryPaths, state: dict[str, Any]) -> None:
    paths.ensure()
    watch_state_path(paths).write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def session_fingerprint(session: SessionRecord) -> str:
    """Identity for watch dedupe: id + timestamp + text length."""
    ts = str(session.timestamp or "")
    n = len(session.text or "")
    return f"{session.session_id}|{ts}|{n}"


def _transcript_for(session: SessionRecord) -> str | None:
    """Per-session transcript path only (not shared history.jsonl)."""
    if not session.path:
        return None
    p = Path(session.path)
    if not p.is_file():
        return None
    # history.jsonl is multi-session — tool-edit scan would false-skip all rows
    if session.source == "claude-history" or p.name == "history.jsonl":
        return None
    return str(p)


def find_watch_candidates(
    repo_root: Path,
    *,
    paths: DevMemoryPaths | None = None,
    limit: int = 30,
    require_edits: bool = True,
    include_processed: bool = False,
) -> list[tuple[SessionRecord, str]]:
    """Return (session, reason) for sessions watch should consider extracting.

    reason is 'new' or 'updated'. Skips already-seen fingerprints and
    (optionally) processed sessions / no-tool-edit chats.
    """
    root = repo_root.resolve()
    dm = paths or DevMemoryPaths.for_repo(root)
    dm.ensure()
    state = read_watch_state(dm)
    seen: dict[str, str] = dict(state.get("seen") or {})

    sessions = discover_claude_sessions(root, limit=limit)
    out: list[tuple[SessionRecord, str]] = []
    for s in sessions:
        if not include_processed and dm.is_processed(s.session_id):
            continue
        fp = session_fingerprint(s)
        prev = seen.get(s.session_id)
        if prev == fp:
            continue
        if require_edits:
            run, gate_reason = should_run_extract_for_session(
                require_edits=True,
                hook_transcript=_transcript_for(s),
                session_id=s.session_id,
                repo_root=root,
            )
            if not run:
                continue
        reason = "updated" if prev else "new"
        out.append((s, reason))
    return out


def mark_seen(paths: DevMemoryPaths, session: SessionRecord) -> None:
    state = read_watch_state(paths)
    seen = state.setdefault("seen", {})
    seen[session.session_id] = session_fingerprint(session)
    # cap
    if len(seen) > 500:
        # drop oldest-ish by keeping last 400 keys insertion order (py3.7+)
        keys = list(seen.keys())
        for k in keys[: len(keys) - 400]:
            seen.pop(k, None)
    state["last_poll_at"] = utc_now()
    write_watch_state(paths, state)


ExtractFn = Callable[..., Any]


def run_watch_cycle(
    repo_root: Path,
    *,
    apply: bool = False,
    offline: bool = False,
    model: str | None = None,
    require_edits: bool = True,
    limit: int = 30,
    max_extracts: int = 3,
    extract_fn: ExtractFn | None = None,
) -> WatchCycle:
    """One poll: discover candidates and extract up to max_extracts."""
    from devmemory.extract import extract_session

    root = repo_root.resolve()
    paths = DevMemoryPaths.for_repo(root)
    paths.ensure()
    cycle = WatchCycle(at=utc_now())

    candidates = find_watch_candidates(
        root,
        paths=paths,
        limit=limit,
        require_edits=require_edits,
    )
    cycle.discovered = len(candidates)
    do_extract = extract_fn or extract_session

    for session, why in candidates[:max_extracts]:
        try:
            outcome = do_extract(
                root,
                session,
                apply=apply,
                offline=offline,
                model=model,
                force=False,
                skip_processed=True,
            )
            units = len(outcome.result.units) if outcome and outcome.result else 0
            cycle.hits.append(
                WatchHit(
                    session_id=session.session_id,
                    source=session.source,
                    action="extract",
                    detail=why,
                    run_id=getattr(outcome, "run_id", None),
                    units=units,
                )
            )
            cycle.extracted += 1
            mark_seen(paths, session)
        except Exception as e:
            # still mark seen to avoid tight error loops on poison sessions
            cycle.hits.append(
                WatchHit(
                    session_id=session.session_id,
                    source=session.source,
                    action="error",
                    detail=f"{why}: {e}",
                )
            )
            mark_seen(paths, session)

    # record poll even when empty
    st = read_watch_state(paths)
    st["last_poll_at"] = cycle.at
    st["last_cycle"] = cycle.to_dict()
    write_watch_state(paths, st)
    return cycle


def watch_loop(
    repo_root: Path,
    *,
    interval_s: float = 60.0,
    once: bool = False,
    max_polls: int = 0,
    apply: bool = False,
    offline: bool = False,
    model: str | None = None,
    require_edits: bool = True,
    on_cycle: Callable[[WatchCycle], None] | None = None,
) -> list[WatchCycle]:
    """Poll until once/max_polls. max_polls=0 means forever (when not once)."""
    cycles: list[WatchCycle] = []
    n = 0
    while True:
        cycle = run_watch_cycle(
            repo_root,
            apply=apply,
            offline=offline,
            model=model,
            require_edits=require_edits,
        )
        cycles.append(cycle)
        if on_cycle:
            on_cycle(cycle)
        n += 1
        if once:
            break
        if max_polls and n >= max_polls:
            break
        time.sleep(max(1.0, float(interval_s)))
    return cycles
