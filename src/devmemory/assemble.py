"""Assemble bounded extraction context (no LLM)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from devmemory.paths import is_knowledge_blocked, list_repo_dirs
from devmemory.redaction import redact
from devmemory.sources.base import SessionRecord
from devmemory.state import RunContext, utc_now

MAX_SESSION_CHARS = int(os.environ.get("DEVMEMORY_MAX_SESSION_CHARS", "24000"))
MAX_DIFF_CHARS = int(os.environ.get("DEVMEMORY_MAX_DIFF_CHARS", "40000"))
MAX_TREE_LINES = int(os.environ.get("DEVMEMORY_MAX_TREE_LINES", "200"))
MAX_KNOWLEDGE_FILE_CHARS = int(os.environ.get("DEVMEMORY_MAX_KNOWLEDGE_CHARS", "1600"))


def _run(cmd: list[str], cwd: Path) -> str:
    try:
        r = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return (r.stdout or "") + (("\n" + r.stderr) if r.returncode and r.stderr else "")
    except Exception as e:
        return f"(command failed: {e})"


def collect_repo_context(repo_root: Path) -> dict[str, str]:
    status = _run(["git", "status", "--short"], repo_root)
    diff = _run(["git", "diff", "HEAD"], repo_root)
    if not diff.strip():
        diff = _run(["git", "diff"], repo_root)
    log = _run(["git", "log", "-5", "--oneline"], repo_root)
    # shallow tree of tracked + common dirs
    tree_lines: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        rel = Path(dirpath).relative_to(repo_root)
        parts = rel.parts
        if any(
            p.startswith(".") or p in {"node_modules", "venv", ".venv", "dist", "build", "__pycache__"}
            for p in parts
        ):
            dirnames.clear()
            continue
        if len(parts) > 3:
            dirnames.clear()
            continue
        for fn in sorted(filenames):
            if fn.startswith("."):
                continue
            tree_lines.append(str(rel / fn) if str(rel) != "." else fn)
            if len(tree_lines) >= MAX_TREE_LINES:
                break
        if len(tree_lines) >= MAX_TREE_LINES:
            break

    # existing knowledge — compact to cut restate thrash in the LLM
    knowledge: list[str] = []
    for name in ("DEV.md", "USAGE.md"):
        for p in repo_root.rglob(name):
            if any(part.startswith(".") for part in p.parts):
                continue
            rel = p.relative_to(repo_root)
            rel_s = str(rel.parent).replace("\\", "/") if rel.name else "."
            if rel_s == ".":
                owner = "."
            else:
                owner = str(rel.parent).replace("\\", "/")
            if is_knowledge_blocked(owner if owner != "." else str(rel).split("/")[0] if "/" in str(rel) else "."):
                # skip knowledge under blocked trees if any slipped in
                if owner != "." and is_knowledge_blocked(owner):
                    continue
            try:
                body = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            knowledge.append(f"### {rel}\n\n{_compact_knowledge(body)}\n")

    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n… [diff truncated] …\n"

    dirs = [d for d in list_repo_dirs(repo_root) if d == "." or not is_knowledge_blocked(d)]
    dir_list = dirs[:80]

    return {
        "status": status.strip() or "(clean)",
        "diff": diff.strip() or "(no unstaged/uncommitted diff)",
        "log": log.strip() or "(no commits)",
        "tree": "\n".join(tree_lines) if tree_lines else "(empty)",
        "knowledge": "\n".join(knowledge) if knowledge else "(no DEV.md/USAGE.md yet)",
        "dirs": "\n".join(dir_list),
    }


def _compact_knowledge(body: str) -> str:
    """Keep H2 titles + up to 5 bullets per section (token thrift, anti-restate)."""
    import re

    parts: list[str] = []
    for m in re.finditer(r"(^##\s+[^\n]+)\n([\s\S]*?)(?=^##\s+|\Z)", body, re.M):
        title = m.group(1).strip()
        bullets = [
            ln.strip()
            for ln in m.group(2).splitlines()
            if ln.strip().startswith(("-", "*"))
        ][:5]
        if not bullets:
            continue
        parts.append(title + "\n" + "\n".join(bullets))
    text = "\n\n".join(parts) if parts else body[:MAX_KNOWLEDGE_FILE_CHARS]
    if len(text) > MAX_KNOWLEDGE_FILE_CHARS:
        text = text[:MAX_KNOWLEDGE_FILE_CHARS] + "\n… [truncated; do not restate] …"
    return text


def assemble(
    ctx: RunContext,
    session: SessionRecord,
    *,
    prompt_template: str,
) -> Path:
    """Write assemble artifacts into run dir; return path to prompt.md."""
    repo = ctx.paths.repo_root
    session_text = redact(session.text or "")
    if len(session_text) > MAX_SESSION_CHARS:
        session_text = session_text[:MAX_SESSION_CHARS] + "\n\n… [session truncated] …\n"

    repo_ctx = collect_repo_context(repo)

    session_md = f"""# Session

- **session_id:** `{session.session_id}`
- **source:** `{session.source}`
- **project:** `{session.project}`
- **timestamp:** `{session.timestamp}`

## Transcript / notes

{session_text}
"""
    repo_md = f"""# Repository context

- **root:** `{repo}`
- **assembled_at:** {utc_now()}

## git status

```
{repo_ctx['status']}
```

## recent log

```
{repo_ctx['log']}
```

## tree (sample)

```
{repo_ctx['tree']}
```

## git diff

```
{repo_ctx['diff']}
```

## existing knowledge files

{repo_ctx['knowledge']}
"""

    prompt = (
        prompt_template.replace("{{REPO_ROOT}}", str(repo))
        .replace("{{SESSION_ID}}", session.session_id)
        .replace("{{SESSION_SOURCE}}", session.source)
        .replace("{{SESSION_TEXT}}", session_text)
        .replace("{{GIT_STATUS}}", repo_ctx["status"])
        .replace("{{GIT_LOG}}", repo_ctx["log"])
        .replace("{{GIT_DIFF}}", repo_ctx["diff"])
        .replace("{{TREE}}", repo_ctx["tree"])
        .replace("{{EXISTING_KNOWLEDGE}}", repo_ctx["knowledge"])
        .replace("{{EXISTING_DIRS}}", repo_ctx.get("dirs", "."))
        .replace("{{RUN_DIR}}", str(ctx.run_dir))
    )

    (ctx.run_dir / "session.md").write_text(session_md, encoding="utf-8")
    (ctx.run_dir / "repo-context.md").write_text(repo_md, encoding="utf-8")
    prompt_path = ctx.run_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    meta = f"""RUN_ID={ctx.run_id}
SESSION_ID={session.session_id}
SESSION_SOURCE={session.source}
REPO_ROOT={repo}
ASSEMBLED_AT={utc_now()}
"""
    (ctx.run_dir / "meta.env").write_text(meta, encoding="utf-8")
    return prompt_path
