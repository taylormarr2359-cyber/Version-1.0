from __future__ import annotations

import re

# Pre-compiled at import time — never recompiled per call
_SECRET_PATTERNS = [
    # Anthropic keys: sk-ant-... and generic sk-...
    re.compile(r"sk-(?:ant-[A-Za-z0-9_\-]+|[A-Za-z0-9_\-]{12,})", re.IGNORECASE),
    # api_key = / api-key: / apikey= in any format, with optional quotes
    re.compile(r'(api[_-]?key\s*[:=]\s*["\']?)([^\s,;"\']+)', re.IGNORECASE),
    # Authorization: Bearer <token>
    re.compile(r"(authorization\s*:\s*bearer\s+)([^\s]+)", re.IGNORECASE),
    # Generic password/secret/token assignments
    re.compile(r'((?:password|secret|token)\s*[:=]\s*["\']?)([^\s,;"\']{6,})', re.IGNORECASE),
]


def redact_secrets(text: str) -> str:
    """Replace known secret patterns with redacted placeholders."""
    if not text:
        return text

    redacted = _SECRET_PATTERNS[0].sub("sk-***REDACTED***", text)
    redacted = _SECRET_PATTERNS[1].sub(r"\1***REDACTED***", redacted)
    redacted = _SECRET_PATTERNS[2].sub(r"\1***REDACTED***", redacted)
    redacted = _SECRET_PATTERNS[3].sub(r"\1***REDACTED***", redacted)
    return redacted


def mask_value(value: str, keep: int = 4) -> str:
    """Show only the first `keep` characters; mask the rest."""
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    return value[:keep] + "*" * (len(value) - keep)
