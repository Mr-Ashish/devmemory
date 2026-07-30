"""Environment readiness checks for live extract (R5).

Reports hermes CLI, OpenRouter key, sessions, model, and related path/hooks.
Never prints secret values — only presence + fingerprint.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from devmemory import __version__
from devmemory.extract import find_hermes, package_root
from devmemory.sources.claude import (
    _default_history,
    _default_projects,
    discover_claude_sessions,
    pick_latest_unprocessed,
)
from devmemory.sources.fixtures import FixtureSource
from devmemory.state import DevMemoryPaths

Status = Literal["ok", "warn", "fail", "info"]


@dataclass
class Check:
    id: str
    status: Status
    summary: str
    detail: str = ""
    fix: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DoctorReport:
    ok: bool
    repo: str
    version: str
    checks: list[Check] = field(default_factory=list)
    ready_live: bool = False
    ready_offline: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "ready_live": self.ready_live,
            "ready_offline": self.ready_offline,
            "repo": self.repo,
            "version": self.version,
            "checks": [c.to_dict() for c in self.checks],
        }


def _mask_key(key: str) -> str:
    """Show only a short fingerprint — never the raw key."""
    key = key.strip()
    if not key:
        return "(empty)"
    if len(key) < 12:
        return "***"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]
    return f"{key[:4]}…{key[-4:]} (sha256:{digest})"


def _load_env_quietly() -> None:
    """Best-effort load of OPENROUTER key without raising."""
    if os.environ.get("OPENROUTER_API_KEY", "").strip():
        return
    env_file = os.environ.get("DEVMEMORY_ENV_FILE", "").strip()
    candidates: list[Path] = []
    if env_file:
        candidates.append(Path(env_file).expanduser())
    candidates.append(Path.cwd() / ".env")
    for parent in [Path.cwd(), *Path.cwd().parents[:4]]:
        cand = parent / "experiments" / "pr-review-agent" / ".env"
        if cand.exists():
            candidates.append(cand)
            break
    for c in candidates:
        if not c.is_file():
            continue
        try:
            for line in c.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
        except OSError:
            continue
        if os.environ.get("OPENROUTER_API_KEY", "").strip():
            return


def check_python() -> Check:
    import sys

    ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ok = sys.version_info >= (3, 11)
    return Check(
        id="python",
        status="ok" if ok else "fail",
        summary=f"Python {ver}",
        detail=sys.executable,
        fix="" if ok else "Use Python ≥3.11",
    )


def check_package() -> Check:
    return Check(
        id="devmemory",
        status="ok",
        summary=f"devmemory {__version__}",
        detail=str(Path(__file__).resolve().parent),
    )


def check_git_repo(repo: Path) -> Check:
    git_dir = repo / ".git"
    if git_dir.exists():
        return Check(
            id="git",
            status="ok",
            summary="git repository",
            detail=str(repo),
        )
    # also allow worktrees / bare
    r = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    if r.returncode == 0 and r.stdout.strip() == "true":
        return Check(id="git", status="ok", summary="git work tree", detail=str(repo))
    return Check(
        id="git",
        status="warn",
        summary="not a git repository",
        detail=str(repo),
        fix="git init (assemble uses git status/diff/tree)",
    )


def check_hermes() -> Check:
    path = find_hermes()
    if not path:
        return Check(
            id="hermes",
            status="fail",
            summary="hermes CLI not found",
            detail="PATH + ~/.local/bin + ~/.hermes/bin",
            fix="./scripts/ensure-hermes.sh",
        )
    version = ""
    try:
        r = subprocess.run(
            [path, "--version"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        version = (r.stdout or r.stderr or "").strip().splitlines()[:1]
        version = version[0] if version else ""
    except (OSError, subprocess.TimeoutExpired):
        version = "(version check failed)"
    return Check(
        id="hermes",
        status="ok",
        summary=f"hermes present{(': ' + version) if version else ''}",
        detail=path,
    )


def check_openrouter_key() -> Check:
    _load_env_quietly()
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    env_file = os.environ.get("DEVMEMORY_ENV_FILE", "").strip()
    if key:
        detail_parts = [_mask_key(key)]
        if env_file:
            detail_parts.append(f"DEVMEMORY_ENV_FILE={env_file}")
        return Check(
            id="openrouter",
            status="ok",
            summary="OPENROUTER_API_KEY set",
            detail="; ".join(detail_parts),
        )
    return Check(
        id="openrouter",
        status="fail",
        summary="OPENROUTER_API_KEY missing",
        detail=f"DEVMEMORY_ENV_FILE={env_file or '(unset)'}",
        fix="export OPENROUTER_API_KEY=… or DEVMEMORY_ENV_FILE=/path/to/.env",
    )


def check_model() -> Check:
    model = (
        os.environ.get("DEVMEMORY_MODEL", "").strip()
        or "anthropic/claude-opus-5"
    )
    source = (
        "DEVMEMORY_MODEL"
        if os.environ.get("DEVMEMORY_MODEL", "").strip()
        else "default"
    )
    # cheap smoke models and dogfood models both ok
    warn = False
    note = ""
    if "opus" not in model.lower() and "gpt" not in model.lower() and "claude" not in model.lower():
        warn = True
        note = "unusual model id — confirm OpenRouter supports it"
    return Check(
        id="model",
        status="warn" if warn else "ok",
        summary=f"model={model}",
        detail=f"source={source}" + (f"; {note}" if note else ""),
        fix="export DEVMEMORY_MODEL=anthropic/claude-opus-5  # dogfood quality",
    )


def check_sessions(repo: Path) -> Check:
    paths = DevMemoryPaths.for_repo(repo)
    claude = discover_claude_sessions(repo, limit=50)
    fixtures_dir = package_root() / "fixtures" / "sessions"
    fixtures = (
        FixtureSource(fixtures_dir).list_sessions(limit=20)
        if fixtures_dir.is_dir()
        else []
    )
    unproc = [s for s in claude if not paths.is_processed(s.session_id)]
    picked = pick_latest_unprocessed(claude, is_processed=paths.is_processed)
    default = "none"
    if picked is not None:
        default = f"claude:{picked.session_id[:24]}"
    elif any(not paths.is_processed(s.session_id) for s in fixtures):
        default = "fixture:unprocessed"
    elif claude:
        default = f"claude-reprocess:{claude[0].session_id[:24]}"
    elif fixtures:
        default = f"fixture:{fixtures[0].session_id}"

    hist = _default_history()
    proj = _default_projects()
    detail = (
        f"claude={len(claude)} unprocessed_claude={len(unproc)} "
        f"fixtures={len(fixtures)} default→{default}; "
        f"history={hist} exists={hist.is_file()}; "
        f"projects={proj} exists={proj.is_dir()}"
    )
    if not claude and not fixtures:
        return Check(
            id="sessions",
            status="fail",
            summary="no sessions discoverable",
            detail=detail,
            fix="Use Claude Code in this repo, or --fixture sample-auth-module",
        )
    if not claude:
        return Check(
            id="sessions",
            status="warn",
            summary=f"fixtures only ({len(fixtures)}); no Claude sessions for cwd",
            detail=detail,
            fix="Open Claude Code in this repo to populate ~/.claude history",
        )
    return Check(
        id="sessions",
        status="ok",
        summary=(
            f"claude={len(claude)} unprocessed={len(unproc)} fixtures={len(fixtures)}"
        ),
        detail=detail,
    )


def check_devmemory_home(repo: Path) -> Check:
    paths = DevMemoryPaths.for_repo(repo)
    exists = paths.home.is_dir()
    return Check(
        id="state",
        status="ok" if exists else "info",
        summary=".devmemory/ " + ("present" if exists else "not initialized (ok)"),
        detail=str(paths.home),
        fix="" if exists else "devmemory init",
    )


def check_hook(repo: Path) -> Check:
    """Detect Claude Code SessionEnd hook install (project or user)."""
    candidates = [
        repo / ".claude" / "settings.json",
        Path.home() / ".claude" / "settings.json",
    ]
    found: list[str] = []
    for p in candidates:
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "claude-code-hook.sh" in text or "devmemory" in text and "SessionEnd" in text:
            found.append(str(p))
        elif "SessionEnd" in text and "hook" in text.lower():
            found.append(f"{p} (SessionEnd present)")
    if found:
        return Check(
            id="hook",
            status="ok",
            summary="Claude Code SessionEnd hook configured",
            detail="; ".join(found),
        )
    return Check(
        id="hook",
        status="info",
        summary="Claude Code hook not installed",
        detail="optional; enables auto dry-run extract on session end",
        fix="./scripts/install-claude-hook.sh",
    )


def check_gitignore(repo: Path) -> Check:
    gi = repo / ".gitignore"
    if not gi.is_file():
        return Check(
            id="gitignore",
            status="warn",
            summary=".gitignore missing",
            fix="devmemory init  # adds .devmemory/",
        )
    text = gi.read_text(encoding="utf-8", errors="replace")
    if ".devmemory/" in text or ".devmemory" in text:
        return Check(
            id="gitignore",
            status="ok",
            summary=".devmemory/ gitignored",
            detail=str(gi),
        )
    return Check(
        id="gitignore",
        status="warn",
        summary=".devmemory/ not in .gitignore",
        detail=str(gi),
        fix="echo '.devmemory/' >> .gitignore",
    )


def run_doctor(repo: Path) -> DoctorReport:
    """Run all readiness checks for ``repo``."""
    repo = repo.resolve()
    checks = [
        check_python(),
        check_package(),
        check_git_repo(repo),
        check_hermes(),
        check_openrouter_key(),
        check_model(),
        check_sessions(repo),
        check_devmemory_home(repo),
        check_gitignore(repo),
        check_hook(repo),
    ]
    by_id = {c.id: c for c in checks}
    ready_offline = by_id["python"].status != "fail" and by_id["sessions"].status != "fail"
    ready_live = (
        ready_offline
        and by_id["hermes"].status == "ok"
        and by_id["openrouter"].status == "ok"
    )
    # Overall ok: no fail checks that block offline at least
    hard_fail = any(
        c.status == "fail" and c.id in ("python", "sessions", "hermes", "openrouter")
        for c in checks
    )
    # For doctor exit: ok if live-ready OR (offline-ready and only live deps missing)
    # Product: exit 0 when ready_offline and no unexpected fails; exit 1 when not offline-ready
    # Prefer: exit 0 if ready_live, exit 0 with warnings if ready_offline, exit 1 if not.
    ok = ready_offline
    return DoctorReport(
        ok=ok,
        repo=str(repo),
        version=__version__,
        checks=checks,
        ready_live=ready_live,
        ready_offline=ready_offline,
    )
