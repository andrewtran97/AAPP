"""Redaction helpers for AAPP reports."""

from __future__ import annotations

import re
from typing import Tuple

_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[\"']?([A-Za-z0-9_\-./+=]{12,})[\"']?"),
    re.compile(r"(?i)\b(sk-[A-Za-z0-9]{20,})\b"),
    re.compile(r"(?i)\b(ghp_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+PRIVATE KEY-----"),
]

def redact_text(value: object) -> Tuple[str, bool]:
    text = "" if value is None else str(value)
    redacted = text
    changed = False

    for pattern in _SECRET_PATTERNS:
        if pattern.search(redacted):
            changed = True
            if pattern.groups >= 2:
                redacted = pattern.sub(lambda m: f"{m.group(1)}=<REDACTED>", redacted)
            else:
                redacted = pattern.sub("<REDACTED_SECRET>", redacted)

    return redacted, changed

def contains_secret_like_value(value: object) -> bool:
    text = "" if value is None else str(value)
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)
