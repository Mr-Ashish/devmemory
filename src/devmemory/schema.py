"""Knowledge unit schema for extraction output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class KnowledgeUnit(BaseModel):
    """One durable knowledge write targeting a module directory."""

    kind: Literal["dev", "usage"]
    path: str = Field(
        ...,
        description="Repo-relative directory that owns DEV.md or USAGE.md",
    )
    action: Literal["create", "merge", "replace_section"] = "merge"
    section: str | None = Field(
        default=None,
        description="Optional H2 section title for section-aware merge",
    )
    content: str = Field(..., min_length=1)
    evidence: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "medium"

    @field_validator("path")
    @classmethod
    def normalize_path(cls, v: str) -> str:
        p = (v or ".").strip().replace("\\", "/")
        while p.startswith("./"):
            p = p[2:]
        p = p.strip("/")
        if ".." in p.split("/"):
            raise ValueError("path must not contain ..")
        return p or "."

    @field_validator("content")
    @classmethod
    def strip_content(cls, v: str) -> str:
        t = (v or "").strip()
        if not t:
            raise ValueError("content must be non-empty")
        return t


class ExtractionResult(BaseModel):
    """Normalized extraction payload."""

    units: list[KnowledgeUnit] = Field(default_factory=list)
    summary: str = ""
    session_ids: list[str] = Field(default_factory=list)
    model: str | None = None
    raw_path: str | None = None

    @property
    def high_signal_units(self) -> list[KnowledgeUnit]:
        return [u for u in self.units if u.confidence in ("high", "medium")]
