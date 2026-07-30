"""Run state under <repo>/.devmemory/ — never commit raw transcripts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class DevMemoryPaths:
    repo_root: Path
    home: Path
    state_file: Path
    runs_dir: Path
    out_dir: Path
    hermes_home: Path

    @classmethod
    def for_repo(cls, repo_root: Path) -> "DevMemoryPaths":
        root = repo_root.resolve()
        home = root / ".devmemory"
        return cls(
            repo_root=root,
            home=home,
            state_file=home / "state.json",
            runs_dir=home / "runs",
            out_dir=home / "out",
            hermes_home=home / "hermes-home",
        )

    def ensure(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.hermes_home.mkdir(parents=True, exist_ok=True)
        gitignore = self.home / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n!.gitignore\n")
        if not self.state_file.exists():
            self.write_state({"version": 1, "processed_sessions": {}, "runs": []})

    def read_state(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {"version": 1, "processed_sessions": {}, "runs": []}
        return json.loads(self.state_file.read_text(encoding="utf-8"))

    def write_state(self, state: dict[str, Any]) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(
            json.dumps(state, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def is_processed(self, session_id: str) -> bool:
        return session_id in (self.read_state().get("processed_sessions") or {})

    def mark_processed(
        self,
        session_id: str,
        *,
        run_id: str,
        units: int = 0,
        summary: str = "",
    ) -> None:
        state = self.read_state()
        processed = state.setdefault("processed_sessions", {})
        processed[session_id] = {
            "run_id": run_id,
            "at": utc_now(),
            "units": units,
            "summary": summary[:500],
        }
        runs = state.setdefault("runs", [])
        runs.append(
            {
                "run_id": run_id,
                "session_id": session_id,
                "at": utc_now(),
                "units": units,
            }
        )
        # keep last 100 run records
        state["runs"] = runs[-100:]
        self.write_state(state)


@dataclass
class RunContext:
    paths: DevMemoryPaths
    run_id: str
    run_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.run_dir = self.paths.out_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
