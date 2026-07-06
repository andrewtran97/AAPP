"""AAPP action record construction and hashing."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .redaction import redact_text

SCHEMA_VERSION = "0.1.0"

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha384_hex(data: bytes) -> str:
    return hashlib.sha384(data).hexdigest()

def digest_payload(payload: Any) -> Optional[str]:
    if payload is None:
        return None
    if isinstance(payload, (dict, list, tuple)):
        text = canonical_json(payload)
    else:
        text = str(payload)
    return "sha384:" + sha384_hex(text.encode("utf-8"))

def _record_without_integrity_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in record.items() if k not in {"record_hash", "signature"}}

def compute_record_hash(record: Dict[str, Any]) -> str:
    unsigned = _record_without_integrity_fields(record)
    return "sha384:" + sha384_hex(canonical_json(unsigned).encode("utf-8"))

def create_record(
    *,
    session_id: str,
    parent_hash: Optional[str],
    actor_id: str,
    actor_type: str,
    tool_id: str,
    tool_type: str,
    scope_id: str,
    authorization_status: str,
    policy_id: str,
    decision: str,
    reason: str,
    input_payload: Any = None,
    output_payload: Any = None,
    artifact_payload: Any = None,
    approval_ref: Optional[str] = None,
    model_id: Optional[str] = None,
) -> Dict[str, Any]:
    safe_input, input_redacted = redact_text(input_payload)
    safe_output, output_redacted = redact_text(output_payload)
    safe_artifact, artifact_redacted = redact_text(artifact_payload)

    record: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_id": str(uuid.uuid4()),
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parent_hash": parent_hash,
        "actor": {
            "actor_id": actor_id,
            "actor_type": actor_type,
            "model_id": model_id,
        },
        "tool": {
            "tool_id": tool_id,
            "tool_type": tool_type,
        },
        "scope": {
            "scope_id": scope_id,
            "authorization_status": authorization_status,
        },
        "policy": {
            "policy_id": policy_id,
            "decision": decision,
            "reason": reason,
        },
        "approval_ref": approval_ref,
        "input_digest": digest_payload(safe_input) if input_payload is not None else None,
        "output_digest": digest_payload(safe_output) if output_payload is not None else None,
        "artifact_digest": digest_payload(safe_artifact) if artifact_payload is not None else None,
        "redaction": {
            "raw_secret_stored": False,
            "redaction_policy": "digest-only-redact-secret-like-values",
            "input_redacted": input_redacted,
            "output_redacted": output_redacted,
            "artifact_redacted": artifact_redacted,
        },
        "record_hash": "",
        "signature": {
            "signature_type": "none",
            "signature_value": "",
            "public_key_ref": None,
        },
    }

    record["record_hash"] = compute_record_hash(record)
    return record
