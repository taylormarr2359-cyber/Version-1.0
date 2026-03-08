from __future__ import annotations

import re


_SECRET_PATTERNS = [
    re.compile(r"(sk-[A-Za-z0-9_\-]{12,})"),
    re.compile(r"(api[_-]?key\s*[:=]\s*)([^\s,;]+)", re.IGNORECASE),
    re.compile(r"(authorization\s*:\s*bearer\s+)([^\s]+)", re.IGNORECASE),
]


def redact_secrets(text: str) -> str:
    if not text:
        return text

    redacted = text
    redacted = _SECRET_PATTERNS[0].sub("sk-***REDACTED***", redacted)
    redacted = _SECRET_PATTERNS[1].sub(r"\1***REDACTED***", redacted)
    redacted = _SECRET_PATTERNS[2].sub(r"\1***REDACTED***", redacted)
    return redacted


def mask_value(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    return value[:keep] + "*" * (len(value) - keep)
