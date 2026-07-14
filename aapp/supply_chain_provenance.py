from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

REQUEST_SCHEMA = "aapp.supply_chain_provenance_request.v1"
BUILD_SCHEMA = "aapp.supply_chain_provenance_build.v1"
RESULT_SCHEMA = "aapp.supply_chain_provenance_result.v1"

VERIFIED = "VERIFIED"
INCOMPLETE = "INCOMPLETE"
DIGEST_MISMATCH = "DIGEST_MISMATCH"
SOURCE_MISMATCH = "SOURCE_MISMATCH"
BUILDER_UNTRUSTED = "BUILDER_UNTRUSTED"
MALFORMED = "MALFORMED"
UNSUPPORTED = "UNSUPPORTED"

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
UTC_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:[.][0-9]{1,6})?Z$"
)

CHECK_NAMES = (
    "schemas_supported",
    "provenance_digest_matches",
    "source_matches",
    "builder_trusted",
    "builder_matches",
    "workflow_matches",
    "timestamps_valid",
    "materials_match",
    "artifact_matches",
    "source_evidence_digest_matches",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def provenance_digest(build_record: dict[str, Any]) -> str:
    clean = dict(build_record)
    clean.pop("provenance_digest", None)
    return "sha256:" + hashlib.sha256(canonical_json(clean)).hexdigest()


def parse_utc_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or UTC_RE.fullmatch(value) is None:
        raise ValueError("timestamp_must_be_utc_rfc3339")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.tzinfo is None:
        raise ValueError("timestamp_timezone_missing")
    return parsed.astimezone(timezone.utc)


def _new_checks() -> dict[str, bool]:
    return {name: False for name in CHECK_NAMES}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and DIGEST_RE.fullmatch(value) is not None


def _result(
    request: Any,
    build_record: Any,
    *,
    verdict: str,
    reason_code: str,
    checks: dict[str, bool],
) -> dict[str, Any]:
    request_obj = request if isinstance(request, dict) else {}
    build_obj = build_record if isinstance(build_record, dict) else {}
    source = build_obj.get("source")
    builder = build_obj.get("builder")
    workflow = build_obj.get("workflow")
    materials = build_obj.get("materials")
    artifact = build_obj.get("artifact")
    source = source if isinstance(source, dict) else {}
    builder = builder if isinstance(builder, dict) else {}
    workflow = workflow if isinstance(workflow, dict) else {}
    artifact = artifact if isinstance(artifact, dict) else {}
    material_count = len(materials) if isinstance(materials, list) else 0
    return {
        "schema_version": RESULT_SCHEMA,
        "request_id": request_obj.get("request_id"),
        "verdict": verdict,
        "reason_codes": [reason_code],
        "source_repository": source.get("repository"),
        "source_commit": source.get("commit"),
        "builder_id": builder.get("id"),
        "workflow_id": workflow.get("id"),
        "material_count": material_count,
        "artifact_name": artifact.get("name"),
        "artifact_digest": artifact.get("digest"),
        "source_evidence_digest": build_obj.get("source_evidence_digest"),
        "checks": dict(checks),
    }


def _missing_field(
    value: dict[str, Any],
    required_fields: tuple[str, ...],
) -> str | None:
    for field in required_fields:
        if field not in value:
            return field
    return None


def _validate_named_digest(
    value: Any,
    *,
    path: str,
    name_field: str,
) -> tuple[str, str] | None:
    if not isinstance(value, dict):
        return MALFORMED, f"INVALID_FIELD_TYPE:{path}"
    missing = _missing_field(value, (name_field, "digest"))
    if missing is not None:
        return INCOMPLETE, f"MISSING_REQUIRED_FIELD:{path}.{missing}"
    if not _is_non_empty_string(value[name_field]):
        return MALFORMED, f"INVALID_FIELD_TYPE:{path}.{name_field}"
    if not _is_digest(value["digest"]):
        return MALFORMED, f"INVALID_DIGEST_FORMAT:{path}.digest"
    return None


def _validate_materials(
    value: Any,
    *,
    path: str,
) -> tuple[str, str] | None:
    if not isinstance(value, list):
        return MALFORMED, f"INVALID_FIELD_TYPE:{path}"
    if not value:
        return INCOMPLETE, f"EMPTY_REQUIRED_LIST:{path}"

    seen_pairs: set[tuple[str, str]] = set()
    seen_by_uri: dict[str, str] = {}
    for index, material in enumerate(value):
        item_path = f"{path}[{index}]"
        error = _validate_named_digest(
            material,
            path=item_path,
            name_field="uri",
        )
        if error is not None:
            return error
        pair = (material["uri"], material["digest"])
        if pair in seen_pairs:
            return MALFORMED, f"DUPLICATE_MATERIAL:{item_path}"
        previous_digest = seen_by_uri.get(material["uri"])
        if previous_digest is not None and previous_digest != material["digest"]:
            return DIGEST_MISMATCH, f"MATERIAL_DIGEST_CONFLICT:{item_path}"
        seen_pairs.add(pair)
        seen_by_uri[material["uri"]] = material["digest"]
    return None


REQUEST_REQUIRED_FIELDS = (
    "schema_version",
    "request_id",
    "expected_source",
    "expected_builder",
    "expected_workflow",
    "expected_materials",
    "expected_artifact",
    "expected_source_evidence_digest",
)

BUILD_REQUIRED_FIELDS = (
    "schema_version",
    "source",
    "builder",
    "workflow",
    "materials",
    "artifact",
    "started_at",
    "finished_at",
    "source_evidence_digest",
    "provenance_digest",
)


def _validate_request_shape(request: Any) -> tuple[str, str] | None:
    if not isinstance(request, dict):
        return MALFORMED, "REQUEST_NOT_OBJECT"

    missing = _missing_field(request, REQUEST_REQUIRED_FIELDS)
    if missing is not None:
        return INCOMPLETE, f"MISSING_REQUIRED_FIELD:request.{missing}"

    if not _is_non_empty_string(request["schema_version"]):
        return MALFORMED, "INVALID_FIELD_TYPE:request.schema_version"
    if request["schema_version"] != REQUEST_SCHEMA:
        return UNSUPPORTED, "UNSUPPORTED_SCHEMA_VERSION:request"
    if not _is_non_empty_string(request["request_id"]):
        return MALFORMED, "INVALID_FIELD_TYPE:request.request_id"

    source = request["expected_source"]
    if not isinstance(source, dict):
        return MALFORMED, "INVALID_FIELD_TYPE:request.expected_source"
    missing = _missing_field(source, ("repository", "commit"))
    if missing is not None:
        return INCOMPLETE, f"MISSING_REQUIRED_FIELD:request.expected_source.{missing}"
    for field in ("repository", "commit"):
        if not _is_non_empty_string(source[field]):
            return MALFORMED, f"INVALID_FIELD_TYPE:request.expected_source.{field}"

    builder = request["expected_builder"]
    if not isinstance(builder, dict):
        return MALFORMED, "INVALID_FIELD_TYPE:request.expected_builder"
    if "id" not in builder:
        return INCOMPLETE, "MISSING_REQUIRED_FIELD:request.expected_builder.id"
    if not _is_non_empty_string(builder["id"]):
        return MALFORMED, "INVALID_FIELD_TYPE:request.expected_builder.id"

    workflow = request["expected_workflow"]
    if not isinstance(workflow, dict):
        return MALFORMED, "INVALID_FIELD_TYPE:request.expected_workflow"
    if "id" not in workflow:
        return INCOMPLETE, "MISSING_REQUIRED_FIELD:request.expected_workflow.id"
    if not _is_non_empty_string(workflow["id"]):
        return MALFORMED, "INVALID_FIELD_TYPE:request.expected_workflow.id"

    materials_error = _validate_materials(
        request["expected_materials"],
        path="request.expected_materials",
    )
    if materials_error is not None:
        return materials_error

    artifact_error = _validate_named_digest(
        request["expected_artifact"],
        path="request.expected_artifact",
        name_field="name",
    )
    if artifact_error is not None:
        return artifact_error

    if not _is_digest(request["expected_source_evidence_digest"]):
        return (
            MALFORMED,
            "INVALID_DIGEST_FORMAT:request.expected_source_evidence_digest",
        )

    return None


def _validate_build_shape(build_record: Any) -> tuple[str, str] | None:
    if not isinstance(build_record, dict):
        return MALFORMED, "BUILD_RECORD_NOT_OBJECT"

    missing = _missing_field(build_record, BUILD_REQUIRED_FIELDS)
    if missing is not None:
        return INCOMPLETE, f"MISSING_REQUIRED_FIELD:build.{missing}"

    if not _is_non_empty_string(build_record["schema_version"]):
        return MALFORMED, "INVALID_FIELD_TYPE:build.schema_version"
    if build_record["schema_version"] != BUILD_SCHEMA:
        return UNSUPPORTED, "UNSUPPORTED_SCHEMA_VERSION:build"

    source = build_record["source"]
    if not isinstance(source, dict):
        return MALFORMED, "INVALID_FIELD_TYPE:build.source"
    missing = _missing_field(source, ("repository", "commit"))
    if missing is not None:
        return INCOMPLETE, f"MISSING_REQUIRED_FIELD:build.source.{missing}"
    for field in ("repository", "commit"):
        if not _is_non_empty_string(source[field]):
            return MALFORMED, f"INVALID_FIELD_TYPE:build.source.{field}"

    builder = build_record["builder"]
    if not isinstance(builder, dict):
        return MALFORMED, "INVALID_FIELD_TYPE:build.builder"
    missing = _missing_field(builder, ("id", "trusted"))
    if missing is not None:
        return INCOMPLETE, f"MISSING_REQUIRED_FIELD:build.builder.{missing}"
    if not _is_non_empty_string(builder["id"]):
        return MALFORMED, "INVALID_FIELD_TYPE:build.builder.id"
    if not isinstance(builder["trusted"], bool):
        return MALFORMED, "INVALID_FIELD_TYPE:build.builder.trusted"

    workflow = build_record["workflow"]
    if not isinstance(workflow, dict):
        return MALFORMED, "INVALID_FIELD_TYPE:build.workflow"
    if "id" not in workflow:
        return INCOMPLETE, "MISSING_REQUIRED_FIELD:build.workflow.id"
    if not _is_non_empty_string(workflow["id"]):
        return MALFORMED, "INVALID_FIELD_TYPE:build.workflow.id"

    materials_error = _validate_materials(
        build_record["materials"],
        path="build.materials",
    )
    if materials_error is not None:
        return materials_error

    artifact_error = _validate_named_digest(
        build_record["artifact"],
        path="build.artifact",
        name_field="name",
    )
    if artifact_error is not None:
        return artifact_error

    for field in ("started_at", "finished_at"):
        try:
            parse_utc_timestamp(build_record[field])
        except (TypeError, ValueError):
            return MALFORMED, f"INVALID_TIMESTAMP:build.{field}"

    if parse_utc_timestamp(build_record["started_at"]) > parse_utc_timestamp(
        build_record["finished_at"]
    ):
        return MALFORMED, "INVALID_TIMESTAMP_ORDER"

    if not _is_digest(build_record["source_evidence_digest"]):
        return MALFORMED, "INVALID_DIGEST_FORMAT:build.source_evidence_digest"
    if not _is_digest(build_record["provenance_digest"]):
        return MALFORMED, "INVALID_DIGEST_FORMAT:build.provenance_digest"

    return None


def _compare_materials(
    expected: list[dict[str, Any]],
    actual: list[dict[str, Any]],
) -> tuple[str, str] | None:
    if len(expected) != len(actual):
        return DIGEST_MISMATCH, "MATERIAL_COUNT_MISMATCH"
    for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
        if expected_item["uri"] != actual_item["uri"]:
            return DIGEST_MISMATCH, f"MATERIAL_URI_MISMATCH:{index}"
        if expected_item["digest"] != actual_item["digest"]:
            return DIGEST_MISMATCH, f"MATERIAL_DIGEST_CONFLICT:{index}"
    return None


def evaluate_supply_chain_provenance(
    request: Any,
    build_record: Any,
) -> dict[str, Any]:
    checks = _new_checks()

    request_error = _validate_request_shape(request)
    if request_error is not None:
        verdict, reason_code = request_error
        return _result(
            request,
            build_record,
            verdict=verdict,
            reason_code=reason_code,
            checks=checks,
        )

    build_error = _validate_build_shape(build_record)
    if build_error is not None:
        verdict, reason_code = build_error
        return _result(
            request,
            build_record,
            verdict=verdict,
            reason_code=reason_code,
            checks=checks,
        )

    checks["schemas_supported"] = True

    try:
        calculated_digest = provenance_digest(build_record)
    except (TypeError, ValueError, RecursionError):
        return _result(
            request,
            build_record,
            verdict=MALFORMED,
            reason_code="PROVENANCE_CANONICALIZATION_FAILED",
            checks=checks,
        )

    if calculated_digest != build_record["provenance_digest"]:
        return _result(
            request,
            build_record,
            verdict=DIGEST_MISMATCH,
            reason_code="PROVENANCE_DIGEST_MISMATCH",
            checks=checks,
        )

    checks["provenance_digest_matches"] = True

    expected_source = request["expected_source"]
    source = build_record["source"]
    if expected_source["repository"] != source["repository"]:
        return _result(
            request,
            build_record,
            verdict=SOURCE_MISMATCH,
            reason_code="SOURCE_REPOSITORY_MISMATCH",
            checks=checks,
        )
    if expected_source["commit"] != source["commit"]:
        return _result(
            request,
            build_record,
            verdict=SOURCE_MISMATCH,
            reason_code="SOURCE_COMMIT_MISMATCH",
            checks=checks,
        )

    checks["source_matches"] = True

    if not build_record["builder"]["trusted"]:
        return _result(
            request,
            build_record,
            verdict=BUILDER_UNTRUSTED,
            reason_code="BUILDER_UNTRUSTED",
            checks=checks,
        )

    checks["builder_trusted"] = True

    if request["expected_builder"]["id"] != build_record["builder"]["id"]:
        return _result(
            request,
            build_record,
            verdict=BUILDER_UNTRUSTED,
            reason_code="BUILDER_ID_MISMATCH",
            checks=checks,
        )

    checks["builder_matches"] = True

    if request["expected_workflow"]["id"] != build_record["workflow"]["id"]:
        return _result(
            request,
            build_record,
            verdict=DIGEST_MISMATCH,
            reason_code="WORKFLOW_ID_MISMATCH",
            checks=checks,
        )

    checks["workflow_matches"] = True
    checks["timestamps_valid"] = True

    materials_error = _compare_materials(
        request["expected_materials"],
        build_record["materials"],
    )
    if materials_error is not None:
        verdict, reason_code = materials_error
        return _result(
            request,
            build_record,
            verdict=verdict,
            reason_code=reason_code,
            checks=checks,
        )

    checks["materials_match"] = True

    expected_artifact = request["expected_artifact"]
    artifact = build_record["artifact"]
    if expected_artifact["name"] != artifact["name"]:
        return _result(
            request,
            build_record,
            verdict=DIGEST_MISMATCH,
            reason_code="ARTIFACT_NAME_MISMATCH",
            checks=checks,
        )
    if expected_artifact["digest"] != artifact["digest"]:
        return _result(
            request,
            build_record,
            verdict=DIGEST_MISMATCH,
            reason_code="ARTIFACT_DIGEST_MISMATCH",
            checks=checks,
        )

    checks["artifact_matches"] = True

    if (
        request["expected_source_evidence_digest"]
        != build_record["source_evidence_digest"]
    ):
        return _result(
            request,
            build_record,
            verdict=DIGEST_MISMATCH,
            reason_code="SOURCE_EVIDENCE_DIGEST_MISMATCH",
            checks=checks,
        )

    checks["source_evidence_digest_matches"] = True

    return _result(
        request,
        build_record,
        verdict=VERIFIED,
        reason_code="ALL_CHECKS_PASSED",
        checks=checks,
    )
