"""Normalize Hermes output into ExtractionResult."""

from __future__ import annotations

import json
import re
from pathlib import Path

from devmemory.redaction import redact
from devmemory.schema import ExtractionResult, KnowledgeUnit

FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def _strip_outer_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```") and t.endswith("```"):
        lines = t.splitlines()
        if len(lines) >= 2:
            body = "\n".join(lines[1:-1])
            if body.lstrip().lower().startswith("json"):
                body = "\n".join(body.splitlines()[1:])
            return body.strip()
    return t


def _extract_json_object(text: str) -> dict | None:
    t = _strip_outer_fence(text)
    # direct parse
    try:
        obj = json.loads(t)
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, list):
            return {"units": obj}
    except json.JSONDecodeError:
        pass
    # fenced blocks
    for m in FENCE_RE.finditer(text):
        chunk = m.group(1).strip()
        try:
            obj = json.loads(chunk)
            if isinstance(obj, dict):
                return obj
            if isinstance(obj, list):
                return {"units": obj}
        except json.JSONDecodeError:
            continue
    # brace slice
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            obj = json.loads(text[start : end + 1])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    return None


def normalize_extraction(
    raw_text: str,
    *,
    session_ids: list[str] | None = None,
    model: str | None = None,
    raw_path: str | None = None,
) -> ExtractionResult:
    # Parse first (pre-parse redaction can break JSON). Redact string fields after.
    obj = _extract_json_object(raw_text or "")
    if not obj:
        return ExtractionResult(
            units=[],
            summary="Failed to parse JSON extraction payload",
            session_ids=session_ids or [],
            model=model,
            raw_path=raw_path,
        )

    units_raw = obj.get("units") or []
    units: list[KnowledgeUnit] = []
    for item in units_raw:
        if not isinstance(item, dict):
            continue
        try:
            if "content" in item and isinstance(item["content"], str):
                item = {**item, "content": redact(item["content"])}
            if "evidence" in item and isinstance(item["evidence"], list):
                item = {
                    **item,
                    "evidence": [redact(str(e)) for e in item["evidence"]],
                }
            units.append(KnowledgeUnit.model_validate(item))
        except Exception:
            continue

    summary = str(obj.get("summary") or "")
    return ExtractionResult(
        units=units,
        summary=redact(summary),
        session_ids=session_ids or list(obj.get("session_ids") or []),
        model=model,
        raw_path=raw_path,
    )


def write_units(result: ExtractionResult, path: Path) -> None:
    path.write_text(
        result.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
