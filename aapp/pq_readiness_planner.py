"""Local deterministic Crypto-Agility / PQ Readiness Planner."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List


READY = "READY"
NEEDS_INVENTORY = "NEEDS_INVENTORY"
INCOMPLETE = "INCOMPLETE"
PQ_MIGRATION_REQUIRED = "PQ_MIGRATION_REQUIRED"
MIGRATION_GAP = "MIGRATION_GAP"
UNSUPPORTED_ALGORITHM = "UNSUPPORTED_ALGORITHM"
MALFORMED = "MALFORMED"

REQUIRED_FIELDS = {
    "context_id",
    "owner",
    "evidence_digest",
    "crypto_inventory",
    "migration_paths",
}

CLASSICAL_ASYMMETRIC = {
    "RSA",
    "DSA",
    "ECDSA",
    "ECDH",
    "DH",
    "DIFFIE_HELLMAN",
    "ED25519",
    "X25519",
}

PQ_READY = {
    "ML-KEM",
    "ML-DSA",
    "SLH-DSA",
}

SYMMETRIC_OR_HASH = {
    "AES-256",
    "AES-128",
    "SHA-256",
    "SHA-384",
    "SHA-512",
    "HMAC-SHA384",
}


def _stable_digest(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _algorithm_names(inventory: Iterable[Dict[str, Any]]) -> List[str]:
    names = []
    for item in inventory:
        if isinstance(item, dict):
            name = str(item.get("algorithm", "")).strip().upper()
            if name:
                names.append(name)
    return names


def plan_pq_readiness(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return a local deterministic PQ readiness planning verdict.

    This planner does not implement post-quantum cryptography, call networks,
    call subprocesses, or validate external compliance status.
    """

    if not isinstance(payload, dict):
        return {
            "verdict": MALFORMED,
            "reason_codes": ["PAYLOAD_NOT_OBJECT"],
            "evidence_digest": None,
        }

    missing = sorted(field for field in REQUIRED_FIELDS if field not in payload)
    if missing:
        return {
            "verdict": MALFORMED,
            "reason_codes": ["MISSING_REQUIRED_FIELD"],
            "missing_fields": missing,
            "evidence_digest": payload.get("evidence_digest"),
        }

    owner = str(payload.get("owner", "")).strip()
    evidence_digest = payload.get("evidence_digest")
    inventory = payload.get("crypto_inventory")
    migration_paths = payload.get("migration_paths")

    if not owner or not evidence_digest:
        return {
            "verdict": MALFORMED,
            "reason_codes": ["EMPTY_REQUIRED_FIELD"],
            "evidence_digest": evidence_digest,
        }

    if not isinstance(inventory, list):
        return {
            "verdict": MALFORMED,
            "reason_codes": ["CRYPTO_INVENTORY_NOT_LIST"],
            "evidence_digest": evidence_digest,
        }

    if not inventory:
        return {
            "verdict": NEEDS_INVENTORY,
            "reason_codes": ["CRYPTO_INVENTORY_REQUIRED"],
            "evidence_digest": evidence_digest,
        }

    if not isinstance(migration_paths, dict):
        return {
            "verdict": MALFORMED,
            "reason_codes": ["MIGRATION_PATHS_NOT_OBJECT"],
            "evidence_digest": evidence_digest,
        }

    algorithms = _algorithm_names(inventory)
    if not algorithms:
        return {
            "verdict": INCOMPLETE,
            "reason_codes": ["ALGORITHM_CLASSIFICATION_REQUIRED"],
            "evidence_digest": evidence_digest,
        }

    supported = CLASSICAL_ASYMMETRIC | PQ_READY | SYMMETRIC_OR_HASH
    unsupported = sorted({name for name in algorithms if name not in supported})
    if unsupported:
        return {
            "verdict": UNSUPPORTED_ALGORITHM,
            "reason_codes": ["UNSUPPORTED_ALGORITHM"],
            "unsupported_algorithms": unsupported,
            "evidence_digest": evidence_digest,
        }

    long_lived = bool(payload.get("long_lived_confidentiality"))
    classical_risks = sorted({name for name in algorithms if name in CLASSICAL_ASYMMETRIC})

    if classical_risks and long_lived:
        missing_paths = sorted(name for name in classical_risks if name not in migration_paths)
        if missing_paths:
            return {
                "verdict": MIGRATION_GAP,
                "reason_codes": ["NO_MIGRATION_PATH_FOR_CLASSICAL_ASYMMETRIC"],
                "algorithms": missing_paths,
                "evidence_digest": evidence_digest,
            }

        return {
            "verdict": PQ_MIGRATION_REQUIRED,
            "reason_codes": ["CLASSICAL_ASYMMETRIC_LONG_LIVED_CONFIDENTIALITY"],
            "algorithms": classical_risks,
            "planned_paths": {name: migration_paths[name] for name in classical_risks},
            "evidence_digest": evidence_digest,
        }

    return {
        "verdict": READY,
        "reason_codes": ["PQ_READINESS_PLAN_READY"],
        "request_digest": _stable_digest(payload),
        "evidence_digest": evidence_digest,
    }
