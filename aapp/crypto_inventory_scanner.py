"""Local deterministic Crypto Inventory Scanner reference for AAPP."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Pattern


PATTERNS = [
    {
        "category": "hash_algorithm",
        "reason_code": "HASH_ALGORITHM_REFERENCE",
        "algorithm": "SHA-256",
        "pattern": re.compile(r"\bsha[-_]?256\b|\bSHA256\b", re.IGNORECASE),
        "risk_class": "standard_reference",
    },
    {
        "category": "hash_algorithm",
        "reason_code": "WEAK_OR_DEPRECATED_CRYPTO",
        "algorithm": "MD5",
        "pattern": re.compile(r"\bmd5\b", re.IGNORECASE),
        "risk_class": "weak_or_deprecated",
    },
    {
        "category": "hash_algorithm",
        "reason_code": "WEAK_OR_DEPRECATED_CRYPTO",
        "algorithm": "SHA-1",
        "pattern": re.compile(r"\bsha[-_]?1\b|\bSHA1\b", re.IGNORECASE),
        "risk_class": "weak_or_deprecated",
    },
    {
        "category": "signature_or_public_key_algorithm",
        "reason_code": "SIGNATURE_OR_PUBLIC_KEY_REFERENCE",
        "algorithm": "RSA",
        "pattern": re.compile(r"\brsa\b|generate_private_key", re.IGNORECASE),
        "risk_class": "inventory_only",
    },
    {
        "category": "signature_or_public_key_algorithm",
        "reason_code": "SIGNATURE_OR_PUBLIC_KEY_REFERENCE",
        "algorithm": "ECDSA",
        "pattern": re.compile(r"\becdsa\b", re.IGNORECASE),
        "risk_class": "inventory_only",
    },
    {
        "category": "signature_or_public_key_algorithm",
        "reason_code": "SIGNATURE_OR_PUBLIC_KEY_REFERENCE",
        "algorithm": "Ed25519",
        "pattern": re.compile(r"\bed25519\b", re.IGNORECASE),
        "risk_class": "inventory_only",
    },
    {
        "category": "key_exchange_algorithm",
        "reason_code": "KEY_EXCHANGE_REFERENCE",
        "algorithm": "ECDH",
        "pattern": re.compile(r"\becdh\b", re.IGNORECASE),
        "risk_class": "inventory_only",
    },
    {
        "category": "symmetric_encryption_algorithm",
        "reason_code": "SYMMETRIC_ENCRYPTION_REFERENCE",
        "algorithm": "AES",
        "pattern": re.compile(r"\baes\b|AESGCM|AES-CBC|AES_GCM", re.IGNORECASE),
        "risk_class": "inventory_only",
    },
    {
        "category": "symmetric_encryption_algorithm",
        "reason_code": "WEAK_OR_DEPRECATED_CRYPTO",
        "algorithm": "DES",
        "pattern": re.compile(r"\bdes\b|\b3des\b|triple[-_ ]?des", re.IGNORECASE),
        "risk_class": "weak_or_deprecated",
    },
    {
        "category": "symmetric_encryption_algorithm",
        "reason_code": "WEAK_OR_DEPRECATED_CRYPTO",
        "algorithm": "RC4",
        "pattern": re.compile(r"\brc4\b", re.IGNORECASE),
        "risk_class": "weak_or_deprecated",
    },
    {
        "category": "certificate_or_key_marker",
        "reason_code": "CERTIFICATE_OR_KEY_MARKER",
        "algorithm": "PRIVATE_KEY_MARKER",
        "pattern": re.compile(r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY", re.IGNORECASE),
        "risk_class": "sensitive_marker",
    },
    {
        "category": "certificate_or_key_marker",
        "reason_code": "CERTIFICATE_OR_KEY_MARKER",
        "algorithm": "CERTIFICATE_MARKER",
        "pattern": re.compile(r"BEGIN CERTIFICATE", re.IGNORECASE),
        "risk_class": "inventory_only",
    },
]


def scan_crypto_inventory(source_text: Any, source_ref: str = "local") -> Dict[str, Any]:
    """Scan local source text for deterministic cryptographic inventory findings.

    This function performs no network calls and no subprocess calls.
    """

    if not isinstance(source_text, str):
        return {
            "scanner_verdict": "UNSUPPORTED",
            "source_ref": source_ref,
            "reason_codes": ["INPUT_NOT_STRING"],
            "findings": [],
            "finding_count": 0,
        }

    if source_text.strip() == "":
        return {
            "scanner_verdict": "MALFORMED",
            "source_ref": source_ref,
            "reason_codes": ["EMPTY_INPUT"],
            "findings": [],
            "finding_count": 0,
        }

    findings = _collect_findings(source_text, source_ref)
    reason_codes = sorted({finding["reason_code"] for finding in findings})

    return {
        "scanner_verdict": "INVENTORIED",
        "source_ref": source_ref,
        "reason_codes": reason_codes,
        "findings": findings,
        "finding_count": len(findings),
        "claim_boundary": "local_deterministic_reference",
    }


def _collect_findings(source_text: str, source_ref: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    for spec in PATTERNS:
        pattern: Pattern[str] = spec["pattern"]
        for match in pattern.finditer(source_text):
            line_number = source_text.count("\n", 0, match.start()) + 1
            findings.append(
                {
                    "source_ref": source_ref,
                    "category": spec["category"],
                    "algorithm": spec["algorithm"],
                    "reason_code": spec["reason_code"],
                    "risk_class": spec["risk_class"],
                    "line": line_number,
                    "matched_text": _safe_match_text(match.group(0)),
                }
            )

    findings.sort(
        key=lambda item: (
            item["line"],
            item["category"],
            item["algorithm"],
            item["matched_text"],
        )
    )
    return findings


def _safe_match_text(value: str) -> str:
    if "PRIVATE KEY" in value.upper():
        return "[KEY_MARKER]"
    return value
