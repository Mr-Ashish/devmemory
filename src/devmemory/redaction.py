"""Secret redaction for session text and knowledge output.

Patterns aligned with hermes-agent-self-evolution external_importers.
"""

from __future__ import annotations

import re

SECRET_PATTERNS = re.compile(
    r"("
    r"sk-ant-api[A-Za-z0-9_\-]+"
    r"|sk-or-v1-[A-Za-z0-9_\-]+"
    r"|sk-[A-Za-z0-9]{20,}"
    r"|ghp_[A-Za-z0-9_]+"
    r"|ghu_[A-Za-z0-9_]+"
    r"|gho_[A-Za-z0-9_]+"
    r"|github_pat_[A-Za-z0-9_]+"
    r"|xox[baprs]-[A-Za-z0-9\-]+"
    r"|xapp-[A-Za-z0-9\-]+"
    r"|ntn_[A-Za-z0-9_]+"
    r"|AKIA[0-9A-Z]{16}"
    r"|Bearer\s+[A-Za-z0-9._\-]{20,}"
    r"|-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----"
    r"|OPENROUTER_API_KEY\s*=\s*[A-Za-z0-9_\-]{8,}"
    r"|OPENAI_API_KEY\s*=\s*[A-Za-z0-9_\-]{8,}"
    r"|ANTHROPIC_API_KEY\s*=\s*[A-Za-z0-9_\-]{8,}"
    r")",
    re.IGNORECASE,
)

REDACTED = "[REDACTED]"


def contains_secret(text: str) -> bool:
    if not text:
        return False
    return bool(SECRET_PATTERNS.search(text))


def redact(text: str) -> str:
    if not text:
        return text
    return SECRET_PATTERNS.sub(REDACTED, text)
