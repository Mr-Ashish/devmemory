"""Orchestrate assemble → hermes extract → normalize → optional apply."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from devmemory.apply import ApplyChange, apply_result, plan_result
from devmemory.assemble import assemble
from devmemory.normalize import normalize_extraction, write_units
from devmemory.paths import infer_paths_from_text, list_repo_dirs
from devmemory.schema import ExtractionResult
from devmemory.sources.base import SessionRecord
from devmemory.state import DevMemoryPaths, RunContext, utc_now
from devmemory.trace import package_showcase

_CMD_LINE = re.compile(
    r"(?m)^\s*(?:[-*]\s*)?(?:`)?((?:pytest|pip|uv|npm|pnpm|yarn|cargo|go|make|docker|"
    r"uvicorn|python|hermes|devmemory|export|curl|gh|git)\b[^`\n]{0,120})(?:`)?"
)
_BULLET_OR_SENTENCE = re.compile(
    r"(?mi)^(?:[-*]\s+)?(.+?(?:decision|middleware|decorator|pattern|pitfall|"
    r"signed with|never commit|do not log|migrate to|pipeline consists).+)$"
)


@dataclass
class ExtractOutcome:
    run_id: str
    run_dir: Path
    result: ExtractionResult
    changes: list[ApplyChange]
    hermes_rc: int
    model: str
    timings: dict | None = None
    showcase_dir: Path | None = None


def package_root() -> Path:
    """devmemory repo root (contains agent/, scripts/)."""
    here = Path(__file__).resolve()
    candidate = here.parents[2]
    if (candidate / "agent" / "extract-prompt.md").exists():
        return candidate
    cwd = Path.cwd()
    if (cwd / "agent" / "extract-prompt.md").exists():
        return cwd
    return candidate


def load_prompt_template(pkg: Path | None = None) -> str:
    root = pkg or package_root()
    return (root / "agent" / "extract-prompt.md").read_text(encoding="utf-8")


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def ensure_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    env_file = os.environ.get("DEVMEMORY_ENV_FILE", "").strip()
    candidates: list[Path] = []
    if env_file:
        candidates.append(Path(env_file).expanduser())
    candidates.append(Path.cwd() / ".env")
    # Walk up from cwd looking for a sibling experiments env (optional convenience)
    for parent in [Path.cwd(), *Path.cwd().parents[:4]]:
        cand = parent / "experiments" / "pr-review-agent" / ".env"
        if cand.exists():
            candidates.append(cand)
            break
    for c in candidates:
        _load_env_file(c)
        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if key:
            return key
    raise RuntimeError(
        "OPENROUTER_API_KEY not set. Export it or set DEVMEMORY_ENV_FILE to a .env file."
    )


def seed_hermes_home(hermes_home: Path, pkg: Path) -> None:
    hermes_home.mkdir(parents=True, exist_ok=True)
    (hermes_home / "memories").mkdir(exist_ok=True)
    (hermes_home / "logs").mkdir(exist_ok=True)
    for name in ("config.yaml", "SOUL.md"):
        src = pkg / "agent" / name
        if src.exists():
            shutil.copy2(src, hermes_home / name)
    mem = hermes_home / "memories" / "MEMORY.md"
    if not mem.exists():
        seed = pkg / "agent" / "MEMORY.seed.md"
        if seed.exists():
            shutil.copy2(seed, mem)
        else:
            mem.write_text("# devmemory agent memory\n\n", encoding="utf-8")
    key = ensure_openrouter_key()
    env_path = hermes_home / ".env"
    env_path.write_text(f"OPENROUTER_API_KEY={key}\n", encoding="utf-8")
    try:
        os.chmod(env_path, 0o600)
    except OSError:
        pass


def find_hermes() -> str | None:
    found = shutil.which("hermes")
    if found:
        return found
    for cand in (
        Path.home() / ".local" / "bin" / "hermes",
        Path.home() / ".hermes" / "bin" / "hermes",
    ):
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    return None


def run_hermes_extract(
    *,
    prompt_path: Path,
    workspace: Path,
    hermes_home: Path,
    out_raw: Path,
    usage_file: Path,
    model: str,
    toolsets: str | None = None,
) -> int:
    hermes = find_hermes()
    if not hermes:
        raise RuntimeError("hermes CLI not found. Run scripts/ensure-hermes.sh first.")

    env = os.environ.copy()
    env["HERMES_HOME"] = str(hermes_home)
    env["OPENROUTER_API_KEY"] = ensure_openrouter_key()
    env["PYTHONUNBUFFERED"] = "1"
    # Verbose agent logging for dogfood traces
    env["HERMES_TUI_TOOL_PROGRESS"] = env.get("HERMES_TUI_TOOL_PROGRESS", "verbose")
    path_extra = f"{Path.home() / '.local' / 'bin'}:{Path.home() / '.hermes' / 'bin'}"
    env["PATH"] = f"{path_extra}:{env.get('PATH', '')}"

    prompt = prompt_path.read_text(encoding="utf-8")
    stderr_path = out_raw.with_suffix(".stderr")
    # Default: no toolsets — extraction is pure reasoning over assembled context.
    # Terminal tools slow runs and encourage wandering. Override with DEVMEMORY_TOOLSETS.
    if toolsets is None:
        toolsets = os.environ.get("DEVMEMORY_TOOLSETS", "").strip()

    cmd = [
        hermes,
        "-z",
        prompt,
        "--provider",
        "openrouter",
        "--model",
        model,
        "--usage-file",
        str(usage_file),
    ]
    if toolsets:
        cmd.extend(["-t", toolsets])

    timeout = int(os.environ.get("DEVMEMORY_HERMES_TIMEOUT", "600"))
    with out_raw.open("w", encoding="utf-8") as out, stderr_path.open(
        "w", encoding="utf-8"
    ) as err:
        proc = subprocess.run(
            cmd,
            cwd=str(workspace),
            env=env,
            stdout=out,
            stderr=err,
            text=True,
            timeout=timeout,
        )
    rc = proc.returncode
    if rc != 0 or not out_raw.stat().st_size:
        cmd2 = [
            hermes,
            "chat",
            "-q",
            prompt,
            "--provider",
            "openrouter",
            "--model",
            model,
        ]
        if toolsets:
            cmd2.extend(["-t", toolsets])
        with out_raw.open("w", encoding="utf-8") as out, stderr_path.open(
            "a", encoding="utf-8"
        ) as err:
            proc2 = subprocess.run(
                cmd2,
                cwd=str(workspace),
                env=env,
                stdout=out,
                stderr=err,
                text=True,
                timeout=timeout,
            )
        rc = proc2.returncode
    return rc


def offline_extract(session: SessionRecord, repo_root: Path) -> ExtractionResult:
    """Deterministic heuristic extract — useful for CI and Hermes-down fallback."""
    text = session.text or ""
    dirs = list_repo_dirs(repo_root)
    paths = infer_paths_from_text(text, dirs)
    primary = paths[0] if paths else "."

    units: list[dict] = []
    dev_bullets: list[str] = []
    usage_bullets: list[str] = []

    for m in _BULLET_OR_SENTENCE.finditer(text):
        line = m.group(1).strip().rstrip(".")
        if len(line) < 20:
            continue
        bullet = f"- {line}."
        low = line.lower()
        if any(k in low for k in ("pytest", "uvicorn", "export ", "pip ", "command", "run ")):
            usage_bullets.append(bullet)
        else:
            dev_bullets.append(bullet)

    for m in _CMD_LINE.finditer(text):
        cmd = m.group(1).strip().strip("`")
        if len(cmd) < 4:
            continue
        usage_bullets.append(f"- `{cmd}`")

    # de-dupe preserve order
    def uniq(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for it in items:
            k = it.lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(it)
        return out[:8]

    dev_bullets = uniq(dev_bullets)
    usage_bullets = uniq(usage_bullets)

    if dev_bullets:
        units.append(
            {
                "kind": "dev",
                "path": primary,
                "action": "merge",
                "section": "Design decisions",
                "content": "\n".join(dev_bullets),
                "evidence": [session.session_id],
                "confidence": "medium",
            }
        )
    if usage_bullets:
        units.append(
            {
                "kind": "usage",
                "path": ".",
                "action": "merge",
                "section": "Common commands",
                "content": "\n".join(usage_bullets),
                "evidence": [session.session_id],
                "confidence": "medium",
            }
        )
    if not units:
        units.append(
            {
                "kind": "dev",
                "path": primary,
                "action": "merge",
                "section": "Architecture",
                "content": f"- Offline stub from session `{session.session_id}` (no durable patterns matched).",
                "evidence": [session.session_id],
                "confidence": "low",
            }
        )

    raw = json.dumps(
        {
            "summary": f"offline heuristic extract ({len(units)} units)",
            "units": units,
            "session_ids": [session.session_id],
        }
    )
    return normalize_extraction(raw, session_ids=[session.session_id], model="offline")


def extract_session(
    repo_root: Path,
    session: SessionRecord,
    *,
    apply: bool = False,
    offline: bool = False,
    model: str | None = None,
    skip_processed: bool = True,
    force: bool = False,
    showcase: bool | Path | None = None,
) -> ExtractOutcome:
    paths = DevMemoryPaths.for_repo(repo_root)
    paths.ensure()
    if skip_processed and not force and paths.is_processed(session.session_id):
        raise RuntimeError(
            f"session {session.session_id} already processed (use --force to re-run)"
        )

    t0 = time.perf_counter()
    timings: dict[str, float] = {}
    run_id = f"run-{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
    ctx = RunContext(paths=paths, run_id=run_id)
    pkg = package_root()
    prompt_template = load_prompt_template(pkg)

    t_a = time.perf_counter()
    prompt_path = assemble(ctx, session, prompt_template=prompt_template)
    timings["assemble_s"] = round(time.perf_counter() - t_a, 3)

    model = (
        model
        or os.environ.get("DEVMEMORY_MODEL")
        or "anthropic/claude-opus-5"
    )
    raw_path = ctx.run_dir / "extract.raw.md"
    usage_file = ctx.run_dir / "hermes-usage.json"
    units_path = ctx.run_dir / "units.json"
    hermes_rc = 0
    log_offset = 0

    if offline or os.environ.get("DEVMEMORY_OFFLINE") == "1":
        t_e = time.perf_counter()
        result = offline_extract(session, repo_root)
        raw_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        hermes_rc = 0
        model = "offline"
        timings["extract_s"] = round(time.perf_counter() - t_e, 3)
    else:
        seed_hermes_home(paths.hermes_home, pkg)
        log_file = paths.hermes_home / "logs" / "agent.log"
        if log_file.exists():
            log_offset = log_file.stat().st_size
        t_e = time.perf_counter()
        hermes_rc = run_hermes_extract(
            prompt_path=prompt_path,
            workspace=repo_root,
            hermes_home=paths.hermes_home,
            out_raw=raw_path,
            usage_file=usage_file,
            model=model,
        )
        timings["extract_s"] = round(time.perf_counter() - t_e, 3)
        raw_text = (
            raw_path.read_text(encoding="utf-8", errors="replace")
            if raw_path.exists()
            else ""
        )
        t_n = time.perf_counter()
        result = normalize_extraction(
            raw_text,
            session_ids=[session.session_id],
            model=model,
            raw_path=str(raw_path),
        )
        timings["normalize_s"] = round(time.perf_counter() - t_n, 3)
        # Fallback only when Hermes hard-failed or returned unparseable empty
        if not result.units:
            result = offline_extract(session, repo_root)
            model = f"{model}+offline-fallback"

    write_units(result, units_path)
    (ctx.run_dir / "summary.md").write_text(
        f"# Run {run_id}\n\n- session: `{session.session_id}`\n"
        f"- model: `{model}`\n- hermes_rc: {hermes_rc}\n"
        f"- units: {len(result.units)}\n- summary: {result.summary}\n"
        f"- at: {utc_now()}\n"
        f"- timings: {json.dumps(timings)}\n",
        encoding="utf-8",
    )

    # Always plan proposed knowledge paths; write only when --apply.
    t_p = time.perf_counter()
    if apply:
        changes = apply_result(repo_root, result)
    else:
        changes = plan_result(repo_root, result)
    timings["apply_s"] = round(time.perf_counter() - t_p, 3)
    (ctx.run_dir / ("apply.json" if apply else "plan.json")).write_text(
        json.dumps(
            [
                {
                    "path": str(c.path.relative_to(repo_root)),
                    "kind": c.kind,
                    "action": c.action,
                    "section": c.section,
                    "bytes": c.bytes_written,
                    "applied": c.applied,
                    "unit_path": c.unit_path,
                }
                for c in changes
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    timings["total_s"] = round(time.perf_counter() - t0, 3)
    (ctx.run_dir / "timings.json").write_text(
        json.dumps(timings, indent=2) + "\n", encoding="utf-8"
    )

    # Mark processed only after a successful apply with durable units.
    # Dry-run must leave the unprocessed cursor intact so re-extract works.
    if apply and result.units:
        paths.mark_processed(
            session.session_id,
            run_id=run_id,
            units=len(result.units),
            summary=result.summary,
        )

    showcase_dir: Path | None = None
    if showcase:
        if showcase is True:
            showcase_dir = (
                package_root()
                / "docs"
                / "showcase"
                / f"dogfood-{run_id}"
            )
        else:
            showcase_dir = Path(showcase)
        package_showcase(
            ctx.run_dir,
            showcase_dir,
            hermes_home=paths.hermes_home,
            log_offset=log_offset,
            model=model,
            hermes_rc=hermes_rc,
            units=len(result.units),
            summary=result.summary,
            timings=timings,
        )

    return ExtractOutcome(
        run_id=run_id,
        run_dir=ctx.run_dir,
        result=result,
        changes=changes,
        hermes_rc=hermes_rc,
        model=model,
        timings=timings,
        showcase_dir=showcase_dir,
    )
