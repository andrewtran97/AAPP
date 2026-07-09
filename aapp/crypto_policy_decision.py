"""Local deterministic Crypto Policy Decision reference for AAPP."""

from __future__ import annotations

from typing import Any, Dict, List


APPROVED_ALGORITHMS = {
    "SHA-256",
    "SHA-384",
    "SHA-512",
    "AES",
}

REVIEW_REQUIRED_ALGORITHMS = {
    "RSA",
    "ECDSA",
    "Ed25519",
    "ECDH",
}

DEPRECATED_ALGORITHMS = {
    "MD5",
    "SHA-1",
}

MIGRATION_REQUIRED_ALGORITHMS = {
    "DES",
    "3DES",
    "RC4",
}

DISALLOWED_ALGORITHMS = {
    "PRIVATE_KEY_MARKER",
}

VERDICT_PRIORITY = {
    "APPROVED": 10,
    "REVIEW_REQUIRED": 20,
    "DEPRECATED": 30,
    "MIGRATION_REQUIRED": 40,
    "DISALLOWED": 50,
}


def decide_crypto_policy(inventory: Any, source_ref: str = "local") -> Dict[str, Any]:
    """Convert B34-style inventory findings into deterministic policy decisions.

    This function performs no network calls and no subprocess calls.
    """

    if not isinstance(inventory, dict):
        return {
            "policy_verdict": "UNSUPPORTED",
            "source_ref": source_ref,
            "reason_codes": ["INPUT_NOT_OBJECT"],
            "decisions": [],
            "decision_count": 0,
        }

    findings = inventory.get("findings")
    if findings is None:
        return _malformed(source_ref, "MISSING_FINDINGS")
    if not isinstance(findings, list):
        return _malformed(source_ref, "FINDINGS_NOT_LIST")

    decisions: List[Dict[str, Any]] = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            return _malformed(source_ref, "FINDING_NOT_OBJECT")

        algorithm = finding.get("algorithm")
        if not isinstance(algorithm, str) or not algorithm.strip():
            return _malformed(source_ref, "FINDING_MISSING_ALGORITHM")

        decisions.append(_decide_finding(finding, index))

    aggregate = _aggregate_verdict(decisions)
    reason_codes = sorted({decision["reason_code"] for decision in decisions})

    return {
        "policy_verdict": aggregate,
        "source_ref": source_ref,
        "reason_codes": reason_codes,
        "decisions": decisions,
        "decision_count": len(decisions),
        "claim_boundary": "local_deterministic_reference",
    }


def _malformed(source_ref: str, reason_code: str) -> Dict[str, Any]:
    return {
        "policy_verdict": "MALFORMED",
        "source_ref": source_ref,
        "reason_codes": [reason_code],
        "decisions": [],
        "decision_count": 0,
    }


def _decide_finding(finding: Dict[str, Any], index: int) -> Dict[str, Any]:
    algorithm = finding["algorithm"]
    normalized = _normalize_algorithm(algorithm)
    risk_class = str(finding.get("risk_class", ""))

    if normalized in DISALLOWED_ALGORITHMS:
        verdict = "DISALLOWED"
        reason_code = "CRYPTO_MARKER_DISALLOWED"
    elif normalized in MIGRATION_REQUIRED_ALGORITHMS:
        verdict = "MIGRATION_REQUIRED"
        reason_code = "CRYPTO_MIGRATION_REQUIRED"
    elif normalized in DEPRECATED_ALGORITHMS or risk_class == "weak_or_deprecated":
        verdict = "DEPRECATED"
        reason_code = "CRYPTO_DEPRECATED"
    elif normalized in REVIEW_REQUIRED_ALGORITHMS:
        verdict = "REVIEW_REQUIRED"
        reason_code = "CRYPTO_REVIEW_REQUIRED"
    elif normalized in APPROVED_ALGORITHMS:
        verdict = "APPROVED"
        reason_code = "CRYPTO_APPROVED"
    else:
        verdict = "REVIEW_REQUIRED"
        reason_code = "CRYPTO_UNKNOWN_REVIEW_REQUIRED"

    return {
        "index": index,
        "algorithm": normalized,
        "category": finding.get("category", "unknown"),
        "policy_verdict": verdict,
        "reason_code": reason_code,
    }


def _normalize_algorithm(value: str) -> str:
    compact = value.strip()
    aliases = {
        "SHA256": "SHA-256",
        "SHA_256": "SHA-256",
        "SHA384": "SHA-384",
        "SHA_384": "SHA-384",
        "SHA512": "SHA-512",
        "SHA_512": "SHA-512",
        "SHA1": "SHA-1",
        "SHA_1": "SHA-1",
        "TRIPLEDES": "3DES",
        "TRIPLE_DES": "3DES",
        "TRIPLE-DES": "3DES",
    }
    upper = compact.upper()
    return aliases.get(upper, compact)


def _aggregate_verdict(decisions: List[Dict[str, Any]]) -> str:
    if not decisions:
        return "APPROVED"

    return max(
        (decision["policy_verdict"] for decision in decisions),
        key=lambda verdict: VERDICT_PRIORITY[verdict],
    )
