"""Development-only signing and verification for AAPP records."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any, Dict, Iterable, List, Tuple

from .record import compute_record_hash

SIGNATURE_TYPE = "HMAC-SHA384-DEV-ONLY"

def sign_hash(record_hash: str, key: bytes) -> str:
    return hmac.new(key, record_hash.encode("utf-8"), hashlib.sha384).hexdigest()

def attach_signature(record: Dict[str, Any], key: bytes, public_key_ref: str = "local-dev-key") -> Dict[str, Any]:
    signed = dict(record)
    signed["record_hash"] = compute_record_hash(signed)
    signed["signature"] = {
        "signature_type": SIGNATURE_TYPE,
        "signature_value": sign_hash(signed["record_hash"], key),
        "public_key_ref": public_key_ref,
    }
    return signed

def verify_record(record: Dict[str, Any], key: bytes, expected_parent_hash: str | None) -> Tuple[bool, str]:
    if record.get("parent_hash") != expected_parent_hash:
        return False, "parent_hash mismatch"

    expected_hash = compute_record_hash(record)
    actual_hash = record.get("record_hash", "")

    if not hmac.compare_digest(actual_hash, expected_hash):
        return False, "record_hash mismatch"

    signature = record.get("signature", {})
    if signature.get("signature_type") != SIGNATURE_TYPE:
        return False, "unsupported signature type"

    expected_sig = sign_hash(actual_hash, key)
    actual_sig = signature.get("signature_value", "")

    if not hmac.compare_digest(actual_sig, expected_sig):
        return False, "signature mismatch"

    return True, "ok"

def verify_chain(records: Iterable[Dict[str, Any]], key: bytes) -> Tuple[bool, List[str]]:
    messages: List[str] = []
    parent_hash = None

    for index, record in enumerate(records):
        ok, message = verify_record(record, key, parent_hash)
        if not ok:
            messages.append(f"record {index}: FAIL: {message}")
            return False, messages

        messages.append(f"record {index}: PASS")
        parent_hash = record["record_hash"]

    return True, messages
