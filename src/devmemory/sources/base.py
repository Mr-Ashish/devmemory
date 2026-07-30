from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SessionRecord:
    """Normalized session / message slice for extraction."""

    session_id: str
    source: str
    project: str = ""
    timestamp: str | float | int = ""
    text: str = ""
    path: Path | None = None
    meta: dict = field(default_factory=dict)

    def preview(self, n: int = 120) -> str:
        t = " ".join((self.text or "").split())
        return t if len(t) <= n else t[: n - 1] + "…"
