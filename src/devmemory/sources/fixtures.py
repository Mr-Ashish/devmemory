"""Load fixture sessions from fixtures/sessions/*.json."""

from __future__ import annotations

import json
from pathlib import Path

from devmemory.sources.base import SessionRecord


class FixtureSource:
    def __init__(self, fixtures_dir: Path) -> None:
        self.fixtures_dir = fixtures_dir

    def list_sessions(self, *, limit: int = 0) -> list[SessionRecord]:
        if not self.fixtures_dir.exists():
            return []
        out: list[SessionRecord] = []
        for path in sorted(self.fixtures_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            out.append(
                SessionRecord(
                    session_id=str(data.get("session_id") or path.stem),
                    source="fixture",
                    project=data.get("project") or "",
                    timestamp=data.get("timestamp") or "",
                    text=(data.get("text") or "").strip(),
                    path=path,
                    meta=data.get("meta") or {},
                )
            )
            if limit and len(out) >= limit:
                break
        return out

    def get(self, session_id: str) -> SessionRecord | None:
        for s in self.list_sessions():
            if s.session_id == session_id or (s.path and s.path.stem == session_id):
                return s
        return None
