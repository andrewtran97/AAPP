SUPPORTED_WITNESS_METHOD = "LOCAL_DETERMINISTIC"


def generate_witness_receipt(record):
    required = [
        "receipt_id",
        "evidence_digest",
        "witness_subject",
        "witness_method",
        "issued_at",
        "verifier_version",
    ]
    missing = [key for key in required if key not in record]

    if missing:
        return {
            "receipt_id": record.get("receipt_id", ""),
            "evidence_digest": record.get("evidence_digest", ""),
            "witness_subject": record.get("witness_subject", ""),
            "witness_method": record.get("witness_method", ""),
            "witness_status": "LOCAL_REJECTED",
            "issued_at": record.get("issued_at", ""),
            "verifier_version": record.get("verifier_version", ""),
            "reason_codes": ["MISSING_REQUIRED_FIELD"],
        }

    if record["witness_method"] != SUPPORTED_WITNESS_METHOD:
        return {
            "receipt_id": record["receipt_id"],
            "evidence_digest": record["evidence_digest"],
            "witness_subject": record["witness_subject"],
            "witness_method": record["witness_method"],
            "witness_status": "UNSUPPORTED",
            "issued_at": record["issued_at"],
            "verifier_version": record["verifier_version"],
            "reason_codes": [
                "UNSUPPORTED_WITNESS_METHOD",
                "NO_EXTERNAL_WITNESS",
            ],
        }

    return {
        "receipt_id": record["receipt_id"],
        "evidence_digest": record["evidence_digest"],
        "witness_subject": record["witness_subject"],
        "witness_method": record["witness_method"],
        "witness_status": "LOCAL_PREPARED",
        "issued_at": record["issued_at"],
        "verifier_version": record["verifier_version"],
        "reason_codes": [
            "LOCAL_REFERENCE_ONLY",
            "EVIDENCE_DIGEST_PRESERVED",
            "NO_EXTERNAL_WITNESS",
        ],
    }
