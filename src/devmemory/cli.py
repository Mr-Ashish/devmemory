"""devmemory CLI."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from devmemory import __version__
from devmemory.apply import apply_result
from devmemory.extract import extract_session, package_root
from devmemory.normalize import normalize_extraction
from devmemory.sources.claude import discover_claude_sessions
from devmemory.sources.fixtures import FixtureSource
from devmemory.sources.base import SessionRecord
from devmemory.state import DevMemoryPaths

console = Console(stderr=True)


def _repo_path(repo: str | None) -> Path:
    return Path(repo or os.getcwd()).resolve()


def _fixtures_dir() -> Path:
    return package_root() / "fixtures" / "sessions"


def _resolve_session(
    repo: Path,
    *,
    session_id: str | None,
    fixture: str | None,
    text_file: Path | None,
) -> SessionRecord:
    if text_file:
        body = text_file.read_text(encoding="utf-8")
        return SessionRecord(
            session_id=session_id or f"file-{text_file.stem}",
            source="file",
            project=str(repo),
            text=body,
            path=text_file,
        )
    if fixture:
        src = FixtureSource(_fixtures_dir())
        s = src.get(fixture)
        if not s:
            # try as path
            p = Path(fixture)
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                return SessionRecord(
                    session_id=str(data.get("session_id") or p.stem),
                    source="fixture",
                    project=data.get("project") or str(repo),
                    text=data.get("text") or "",
                    path=p,
                )
            raise click.ClickException(f"Fixture not found: {fixture}")
        return s
    if session_id:
        # search fixtures then claude
        src = FixtureSource(_fixtures_dir())
        s = src.get(session_id)
        if s:
            return s
        for cand in discover_claude_sessions(repo, limit=200):
            if cand.session_id == session_id:
                return cand
        raise click.ClickException(f"Session not found: {session_id}")
    # default: first unprocessed fixture or claude session
    paths = DevMemoryPaths.for_repo(repo)
    paths.ensure()
    for s in FixtureSource(_fixtures_dir()).list_sessions():
        if not paths.is_processed(s.session_id):
            return s
    for s in discover_claude_sessions(repo, limit=50):
        if not paths.is_processed(s.session_id):
            return s
    # fall back to first fixture even if processed
    fixtures = FixtureSource(_fixtures_dir()).list_sessions()
    if fixtures:
        return fixtures[0]
    raise click.ClickException("No sessions found. Pass --fixture or --session.")


@click.group()
@click.version_option(__version__, prog_name="devmemory")
def main() -> None:
    """Continuous knowledge extraction into colocated DEV.md / USAGE.md."""


@main.command("init")
@click.option("--repo", "repo", default=None, help="Target repository root")
def init_cmd(repo: str | None) -> None:
    """Initialize .devmemory/ and root knowledge templates if missing."""
    root = _repo_path(repo)
    paths = DevMemoryPaths.for_repo(root)
    paths.ensure()
    for name, body in (
        (
            "DEV.md",
            "# DEV — engineering knowledge\n\n> How this repository is built.\n\n## Architecture\n\n_(seeded by devmemory init)_\n",
        ),
        (
            "USAGE.md",
            "# USAGE — operational knowledge\n\n> How to work with this repository.\n\n## Common commands\n\n```bash\ndevmemory extract --fixture sample-auth-module --apply\n```\n",
        ),
    ):
        p = root / name
        if not p.exists():
            p.write_text(body, encoding="utf-8")
            console.print(f"[green]created[/green] {p}")
        else:
            console.print(f"[dim]exists[/dim] {p}")
    # ensure root gitignore has .devmemory
    gi = root / ".gitignore"
    line = ".devmemory/"
    if gi.exists():
        text = gi.read_text(encoding="utf-8")
        if line not in text:
            gi.write_text(text.rstrip() + f"\n{line}\n", encoding="utf-8")
            console.print(f"[green]updated[/green] {gi}")
    else:
        gi.write_text(f"{line}\n", encoding="utf-8")
        console.print(f"[green]created[/green] {gi}")
    console.print(f"[bold]devmemory ready[/bold] at {paths.home}")


@main.command("list-sessions")
@click.option("--repo", default=None)
@click.option("--fixtures/--no-fixtures", default=True)
@click.option("--claude/--no-claude", default=True)
@click.option("--limit", default=30, show_default=True)
def list_sessions(repo: str | None, fixtures: bool, claude: bool, limit: int) -> None:
    """List discoverable sessions for a repo."""
    root = _repo_path(repo)
    rows: list[SessionRecord] = []
    if fixtures:
        rows.extend(FixtureSource(_fixtures_dir()).list_sessions(limit=limit))
    if claude:
        rows.extend(discover_claude_sessions(root, limit=limit))
    paths = DevMemoryPaths.for_repo(root)
    table = Table(title=f"Sessions for {root.name}")
    table.add_column("id")
    table.add_column("source")
    table.add_column("processed")
    table.add_column("preview")
    seen = set()
    for s in rows:
        if s.session_id in seen:
            continue
        seen.add(s.session_id)
        proc = "yes" if paths.is_processed(s.session_id) else "no"
        table.add_row(s.session_id[:40], s.source, proc, s.preview(60))
        if len(seen) >= limit:
            break
    console.print(table)


@main.command("status")
@click.option("--repo", default=None)
def status_cmd(repo: str | None) -> None:
    """Show processed sessions and recent runs."""
    root = _repo_path(repo)
    paths = DevMemoryPaths.for_repo(root)
    paths.ensure()
    state = paths.read_state()
    processed = state.get("processed_sessions") or {}
    runs = state.get("runs") or []
    console.print(f"[bold]repo[/bold] {root}")
    console.print(f"[bold]processed sessions[/bold] {len(processed)}")
    console.print(f"[bold]recent runs[/bold] {len(runs)}")
    for r in runs[-5:]:
        console.print(
            f"  - {r.get('run_id')} session={r.get('session_id')} units={r.get('units')} at={r.get('at')}"
        )


@main.command("extract")
@click.option("--repo", default=None, help="Target repository")
@click.option("--session", "session_id", default=None, help="Session id")
@click.option("--fixture", default=None, help="Fixture name or path")
@click.option("--text-file", type=click.Path(path_type=Path), default=None)
@click.option("--apply/--no-apply", default=False, help="Write DEV.md/USAGE.md")
@click.option("--offline/--live", default=False, help="Heuristic extract without Hermes")
@click.option("--force", is_flag=True, help="Re-process already processed session")
@click.option("--model", default=None, help="OpenRouter model id (default: opus-5)")
@click.option(
    "--showcase/--no-showcase",
    default=False,
    help="Write redacted docs/showcase package for README",
)
@click.option(
    "--showcase-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Custom showcase output directory",
)
def extract_cmd(
    repo: str | None,
    session_id: str | None,
    fixture: str | None,
    text_file: Path | None,
    apply: bool,
    offline: bool,
    force: bool,
    model: str | None,
    showcase: bool,
    showcase_dir: Path | None,
) -> None:
    """Extract durable knowledge from a session."""
    root = _repo_path(repo)
    session = _resolve_session(
        root, session_id=session_id, fixture=fixture, text_file=text_file
    )
    console.print(
        f"[bold]extract[/bold] session={session.session_id} source={session.source} "
        f"apply={apply} offline={offline}"
    )
    show: bool | Path | None = False
    if showcase_dir is not None:
        show = showcase_dir
    elif showcase:
        show = True
    try:
        outcome = extract_session(
            root,
            session,
            apply=apply,
            offline=offline,
            model=model,
            force=force,
            showcase=show,
        )
    except RuntimeError as e:
        raise click.ClickException(str(e)) from e

    console.print(f"[green]run[/green] {outcome.run_id}")
    console.print(f"  dir: {outcome.run_dir}")
    console.print(f"  model: {outcome.model} hermes_rc={outcome.hermes_rc}")
    console.print(f"  units: {len(outcome.result.units)}")
    console.print(f"  summary: {outcome.result.summary or '(none)'}")
    if outcome.timings:
        console.print(f"  timings: {outcome.timings}")
    for u in outcome.result.units:
        console.print(
            f"  - [{u.confidence}] {u.kind} path={u.path!r} section={u.section!r}"
        )
    if apply:
        console.print(f"[green]applied[/green] {len(outcome.changes)} file change(s)")
        for c in outcome.changes:
            try:
                rel = c.path.relative_to(root)
            except ValueError:
                rel = c.path
            console.print(f"  - {rel} ({c.kind}/{c.action})")
    if outcome.showcase_dir:
        console.print(f"[green]showcase[/green] {outcome.showcase_dir}")
    # machine-readable last line for scripts
    print(
        json.dumps(
            {
                "run_id": outcome.run_id,
                "run_dir": str(outcome.run_dir),
                "units": len(outcome.result.units),
                "changes": len(outcome.changes),
                "model": outcome.model,
                "hermes_rc": outcome.hermes_rc,
                "timings": outcome.timings,
                "showcase": str(outcome.showcase_dir) if outcome.showcase_dir else None,
            }
        )
    )


@main.command("apply")
@click.option("--repo", default=None)
@click.option("--run", "run_id", required=True, help="Run id under .devmemory/out/")
def apply_cmd(repo: str | None, run_id: str) -> None:
    """Apply units.json from a prior run."""
    root = _repo_path(repo)
    paths = DevMemoryPaths.for_repo(root)
    units_path = paths.out_dir / run_id / "units.json"
    if not units_path.exists():
        raise click.ClickException(f"Missing {units_path}")
    data = units_path.read_text(encoding="utf-8")
    result = normalize_extraction(data)
    # if already structured json dump of ExtractionResult
    try:
        parsed = json.loads(data)
        if "units" in parsed:
            from devmemory.schema import ExtractionResult

            result = ExtractionResult.model_validate(parsed)
    except Exception:
        pass
    changes = apply_result(root, result)
    console.print(f"[green]applied[/green] {len(changes)} change(s)")
    for c in changes:
        console.print(f"  - {c.path}")


@main.command("review")
@click.option("--repo", default=None)
def review_cmd(repo: str | None) -> None:
    """Show git status/diff for knowledge files."""
    root = _repo_path(repo)
    import subprocess

    files = list(root.rglob("DEV.md")) + list(root.rglob("USAGE.md"))
    rels = [str(p.relative_to(root)) for p in files if ".devmemory" not in p.parts]
    console.print("[bold]knowledge files[/bold]")
    for r in rels:
        console.print(f"  {r}")
    subprocess.run(["git", "status", "--short", "--", *rels], cwd=str(root))
    subprocess.run(["git", "diff", "--", *rels], cwd=str(root))


if __name__ == "__main__":
    main()
