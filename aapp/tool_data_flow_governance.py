"""Local deterministic tool data flow governance reference for B31."""

REQUIRED_FIELDS = (
    "record_id",
    "actor",
    "tool",
    "action",
    "resource",
    "input_classification",
    "output_classification",
    "evidence_digest",
    "export_requested",
    "training_rights",
    "tenant_id",
    "target_tenant_id",
    "contains_raw_secret",
)


def govern_tool_data_flow(record):
    """Return a local governance verdict for one tool data flow record."""
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        return _decision(
            record,
            "MALFORMED",
            ["MALFORMED_RECORD"],
            export_allowed=False,
            training_allowed=False,
        )

    if record["tenant_id"] != record["target_tenant_id"]:
        return _decision(
            record,
            "TENANT_BOUNDARY_VIOLATION",
            ["TENANT_BOUNDARY_MISMATCH"],
            export_allowed=False,
            training_allowed=False,
        )

    if record.get("contains_raw_secret") is True:
        return _decision(
            record,
            "BLOCKED",
            ["RAW_SECRET_BLOCKED"],
            export_allowed=False,
            training_allowed=False,
        )

    if record.get("export_requested") is True and record.get("has_governance_verdict") is False:
        return _decision(
            record,
            "EXPORT_NOT_ALLOWED",
            ["EXPORT_REQUIRES_GOVERNANCE"],
            export_allowed=False,
            training_allowed=False,
        )

    if record.get("action") == "train" and record.get("training_rights") is not True:
        return _decision(
            record,
            "TRAINING_NOT_ALLOWED",
            ["TRAINING_REQUIRES_RIGHTS"],
            export_allowed=False,
            training_allowed=False,
        )

    if record.get("output_classification") == "SECRET_LIKE":
        return _decision(
            record,
            "REDACTED",
            ["OUTPUT_REDACTED"],
            export_allowed=bool(record.get("export_requested")),
            training_allowed=bool(record.get("training_rights")),
        )

    return _decision(
        record,
        "ALLOWED",
        ["INPUT_ALLOWED", "OUTPUT_ALLOWED"],
        export_allowed=bool(record.get("export_requested")),
        training_allowed=bool(record.get("training_rights")),
    )


def _decision(record, verdict, reason_codes, export_allowed, training_allowed):
    return {
        "record_id": record.get("record_id"),
        "governance_verdict": verdict,
        "reason_codes": reason_codes,
        "evidence_digest": record.get("evidence_digest"),
        "export_allowed": export_allowed,
        "training_allowed": training_allowed,
    }
