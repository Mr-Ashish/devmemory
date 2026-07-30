"""Redacted run traces for dogfood / showcase packages."""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from devmemory.redaction import redact

_SECRET_RE = re.compile(
    r"(sk-or-v1-[A-Za-z0-9_\-]+|sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._\-]+|"
    r"OPENROUTER_API_KEY\s*=\s*\S+)",
    re.I,
)


def _r(s: str) -> str:
    return redact(_SECRET_RE.sub("[REDACTED]", s or ""))


def _r_obj(o: Any) -> Any:
    if isinstance(o, str):
        return _r(o)
    if isinstance(o, list):
        return [_r_obj(x) for x in o]
    if isinstance(o, dict):
        return {k: _r_obj(v) for k, v in o.items()}
    return o


def slice_agent_log(hermes_home: Path, log_offset: int, dest: Path, *, max_bytes: int = 400_000) -> int:
    log = hermes_home / "logs" / "agent.log"
    if not log.exists():
        return 0
    data = log.read_bytes()
    chunk = data[log_offset:] if log_offset < len(data) else data[-max_bytes:]
    if len(chunk) > max_bytes:
        chunk = chunk[-max_bytes:]
    text = _r(chunk.decode("utf-8", errors="replace"))
    dest.write_text(text, encoding="utf-8")
    return len(chunk)


def export_session_messages(hermes_home: Path, dest: Path) -> dict:
    """Best-effort export of latest Hermes state.db messages (redacted)."""
    candidates = [
        hermes_home / "state.db",
        hermes_home / "sessions" / "state.db",
        Path.home() / ".hermes" / "state.db",
    ]
    db = next((p for p in candidates if p.is_file()), None)
    meta: dict[str, Any] = {"db": str(db) if db else None, "messages": 0}
    if not db:
        return meta
    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if "messages" not in tables:
            conn.close()
            return meta
        row = conn.execute(
            "SELECT session_id, COUNT(*) c FROM messages GROUP BY session_id ORDER BY c DESC LIMIT 1"
        ).fetchone()
        if not row:
            conn.close()
            return meta
        sid = row[0]
        cols = {r[1] for r in conn.execute("PRAGMA table_info(messages)").fetchall()}
        select = [c for c in ("id", "session_id", "role", "content", "timestamp", "tool_name", "tool_calls") if c in cols]
        rows = conn.execute(
            f"SELECT {', '.join(select)} FROM messages WHERE session_id = ? ORDER BY id ASC",
            (sid,),
        ).fetchall()
        messages = [_r_obj({k: r[k] for k in r.keys()}) for r in rows]
        conn.close()
        dest.write_text(json.dumps({"session_id": sid, "messages": messages}, indent=2) + "\n", encoding="utf-8")
        meta["messages"] = len(messages)
        meta["session_id"] = sid
    except Exception as e:
        meta["error"] = str(e)
    return meta


def write_agent_loop_md(
    dest: Path,
    *,
    run_id: str,
    model: str,
    hermes_rc: int,
    units: int,
    summary: str,
    usage: dict,
    timings: dict,
) -> None:
    lines = [
        f"# Agent loop · `{run_id}`",
        "",
        f"- **model:** `{model}`",
        f"- **hermes_rc:** {hermes_rc}",
        f"- **units:** {units}",
        f"- **at:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Summary",
        "",
        summary or "_(none)_",
        "",
        "## Usage",
        "",
        "```json",
        json.dumps(_r_obj(usage), indent=2)[:4000],
        "```",
        "",
        "## Timings (seconds)",
        "",
        "```json",
        json.dumps(timings, indent=2),
        "```",
        "",
        "## Pipeline",
        "",
        "```text",
        "session → assemble → hermes -z (OpenRouter) → normalize → apply → git review",
        "```",
        "",
    ]
    dest.write_text("\n".join(lines), encoding="utf-8")


def package_showcase(
    run_dir: Path,
    showcase_dir: Path,
    *,
    hermes_home: Path | None = None,
    log_offset: int = 0,
    model: str = "",
    hermes_rc: int = 0,
    units: int = 0,
    summary: str = "",
    timings: dict | None = None,
) -> Path:
    """Copy redacted run artifacts into docs/showcase/... for the README."""
    showcase_dir.mkdir(parents=True, exist_ok=True)
    loop = showcase_dir / "agent-loop"
    loop.mkdir(exist_ok=True)

    for name in (
        "units.json",
        "summary.md",
        "prompt.md",
        "session.md",
        "repo-context.md",
        "meta.env",
        "apply.json",
        "plan.json",
        "preview.diff",
        "preview.json",
        "extract.raw.md",
        "hermes-usage.json",
        "timings.json",
    ):
        src = run_dir / name
        if src.exists():
            text = _r(src.read_text(encoding="utf-8", errors="replace"))
            # cap huge prompts
            if name in ("prompt.md", "session.md", "repo-context.md") and len(text) > 80_000:
                text = text[:80_000] + "\n\n… [truncated for showcase] …\n"
            (showcase_dir / name).write_text(text, encoding="utf-8")

    stderr = run_dir / "extract.raw.stderr"
    if stderr.exists():
        (loop / "hermes.stderr").write_text(
            _r(stderr.read_text(encoding="utf-8", errors="replace"))[-12000:],
            encoding="utf-8",
        )

    usage: dict = {}
    uf = run_dir / "hermes-usage.json"
    if uf.exists():
        try:
            usage = _r_obj(json.loads(uf.read_text(encoding="utf-8")))
        except Exception:
            usage = {}
        (loop / "usage.json").write_text(json.dumps(usage, indent=2) + "\n", encoding="utf-8")

    if hermes_home:
        slice_agent_log(hermes_home, log_offset, loop / "agent.log")
        msg_meta = export_session_messages(hermes_home, loop / "messages.json")
    else:
        msg_meta = {}

    run_id = run_dir.name
    write_agent_loop_md(
        loop / "agent-loop.md",
        run_id=run_id,
        model=model,
        hermes_rc=hermes_rc,
        units=units,
        summary=summary,
        usage=usage,
        timings=timings or {},
    )
    agent_loop = {
        "run_id": run_id,
        "model": model,
        "hermes_rc": hermes_rc,
        "units": units,
        "summary": summary,
        "usage": usage,
        "timings": timings or {},
        "messages_meta": msg_meta,
        "pipeline": [
            "assemble",
            "hermes_extract",
            "normalize",
            "apply",
        ],
    }
    (loop / "agent-loop.json").write_text(
        json.dumps(_r_obj(agent_loop), indent=2) + "\n", encoding="utf-8"
    )

    # README for the showcase folder
    (showcase_dir / "README.md").write_text(
        f"""# Showcase · `{run_id}`

Live dogfood run of **devmemory on itself**.

| Field | Value |
|-------|-------|
| model | `{model}` |
| hermes_rc | {hermes_rc} |
| units | {units} |

## Files

- `units.json` — normalized knowledge units
- `apply.json` — files written
- `prompt.md` / `session.md` / `repo-context.md` — assembled context (redacted)
- `agent-loop/` — Hermes usage, logs, structured loop

## Privacy

Secrets redacted. Raw `.env` never copied. `.devmemory/` remains gitignored; this showcase is a **curated** public slice.
""",
        encoding="utf-8",
    )
    return showcase_dir
