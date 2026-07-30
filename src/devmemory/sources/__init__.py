"""Session sources for knowledge extraction."""

from .base import SessionRecord
from .claude import (
    ClaudeHistorySource,
    ClaudeProjectSource,
    discover_claude_sessions,
    pick_latest_unprocessed,
)
from .fixtures import FixtureSource

__all__ = [
    "SessionRecord",
    "ClaudeHistorySource",
    "ClaudeProjectSource",
    "FixtureSource",
    "discover_claude_sessions",
    "pick_latest_unprocessed",
]
