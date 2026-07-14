from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any

REQUEST_SCHEMA = "aapp.bom_export_request.v1"
RESULT_SCHEMA = "aapp.bom_export_result.v1"

CYCLONEDX_JSON = "CYCLONEDX_JSON"
SPDX_JSON = "SPDX_JSON"

EXPORTED = "EXPORTED"
INCOMPLETE = "INCOMPLETE"
LICENSE_UNKNOWN = "LICENSE_UNKNOWN"
PROVENANCE_MISSING = "PROVENANCE_MISSING"
MALFORMED = "MALFORMED"
UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")

OPTIONAL_OBJECT_COLLECTIONS = (
    "cryptographic_assets",
    "models",
    "datasets",
    "runtimes",
    "services",
)

CHECK_NAMES = (
    "schema_supported",
    "format_supported",
    "inventory_complete",
    "identities_valid",
    "dependencies_valid",
    "licenses_known",
    "provenance_present",
    "evidence_refs_valid",
    "bom_rendered",
    "bom_digest_created",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def bom_digest(bom: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(bom)).hexdigest()


def _checks() -> dict[str, bool]:
    return {name: False for name in CHECK_NAMES}


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _digest(value: Any) -> bool:
    return isinstance(value, str) and DIGEST_RE.fullmatch(value) is not None


def _identifier(value: Any) -> bool:
    return isinstance(value, str) and IDENTIFIER_RE.fullmatch(value) is not None


def _safe_refs(inventory: Any, name: str) -> list[str]:
    if not isinstance(inventory, dict):
        return []
    value = inventory.get(name)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _result(
    request: Any,
    verdict: str,
    reason_code: str,
    checks: dict[str, bool],
    *,
    bom: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request_obj = request if isinstance(request, dict) else {}
    inventory = request_obj.get("inventory")
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA,
        "request_id": request_obj.get("request_id"),
        "output_format": request_obj.get("output_format"),
        "verdict": verdict,
        "reason_codes": [reason_code],
        "checks": dict(checks),
        "source_evidence_digest": request_obj.get(
            "source_evidence_digest"
        ),
        "provenance_refs": _safe_refs(
            inventory,
            "provenance_refs",
        ),
        "evidence_refs": _safe_refs(
            inventory,
            "evidence_refs",
        ),
    }
    if verdict == EXPORTED and bom is not None:
        result["bom"] = bom
        result["bom_digest"] = bom_digest(bom)
    return result


def _validate_refs(
    value: Any,
    path: str,
    *,
    required: bool,
) -> tuple[str, str] | None:
    if value is None:
        if required:
            return (
                PROVENANCE_MISSING,
                f"MISSING_REQUIRED_FIELD:{path}",
            )
        return None

    if not isinstance(value, list):
        return MALFORMED, f"INVALID_FIELD_TYPE:{path}"

    if required and not value:
        return (
            PROVENANCE_MISSING,
            f"EMPTY_REQUIRED_LIST:{path}",
        )

    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not _string(item):
            return MALFORMED, f"INVALID_FIELD_TYPE:{item_path}"
        if item in seen:
            return MALFORMED, f"DUPLICATE_REFERENCE:{item_path}"
        seen.add(item)

    return None


def _validate_objects(
    value: Any,
    path: str,
    required_fields: tuple[str, ...],
    *,
    required: bool,
) -> tuple[str, str] | None:
    if value is None:
        if required:
            return INCOMPLETE, f"MISSING_REQUIRED_FIELD:{path}"
        return None

    if not isinstance(value, list):
        return MALFORMED, f"INVALID_FIELD_TYPE:{path}"

    if required and not value:
        return INCOMPLETE, f"EMPTY_REQUIRED_LIST:{path}"

    seen: set[str] = set()

    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"

        if not isinstance(item, dict):
            return MALFORMED, f"INVALID_FIELD_TYPE:{item_path}"

        for field in required_fields:
            if field not in item:
                if (
                    path == "inventory.components"
                    and field == "license"
                ):
                    return (
                        LICENSE_UNKNOWN,
                        f"LICENSE_UNKNOWN:{item_path}",
                    )
                return (
                    INCOMPLETE,
                    f"MISSING_REQUIRED_FIELD:{item_path}.{field}",
                )

            if not _string(item[field]):
                if (
                    path == "inventory.components"
                    and field == "license"
                ):
                    return (
                        LICENSE_UNKNOWN,
                        f"LICENSE_UNKNOWN:{item_path}",
                    )
                return (
                    MALFORMED,
                    f"INVALID_FIELD_TYPE:{item_path}.{field}",
                )

        if not _identifier(item["id"]):
            return MALFORMED, f"INVALID_IDENTIFIER:{item_path}.id"

        if item["id"] in seen:
            return MALFORMED, f"DUPLICATE_IDENTITY:{item_path}.id"

        seen.add(item["id"])

    return None


def _validate_request(request: Any) -> tuple[str, str] | None:
    if not isinstance(request, dict):
        return MALFORMED, "REQUEST_NOT_OBJECT"

    for field in (
        "schema_version",
        "request_id",
        "output_format",
        "inventory",
        "source_evidence_digest",
    ):
        if field not in request:
            return (
                INCOMPLETE,
                f"MISSING_REQUIRED_FIELD:request.{field}",
            )

    if request["schema_version"] != REQUEST_SCHEMA:
        return MALFORMED, "UNSUPPORTED_SCHEMA_VERSION:request"

    if not _identifier(request["request_id"]):
        return MALFORMED, "INVALID_IDENTIFIER:request.request_id"

    if not _string(request["output_format"]):
        return MALFORMED, "INVALID_FIELD_TYPE:request.output_format"

    if not isinstance(request["inventory"], dict):
        return MALFORMED, "INVALID_FIELD_TYPE:request.inventory"

    if not _digest(request["source_evidence_digest"]):
        return (
            MALFORMED,
            "INVALID_DIGEST_FORMAT:request.source_evidence_digest",
        )

    return None


def _validate_inventory(
    inventory: dict[str, Any],
) -> tuple[str, str] | None:
    component_error = _validate_objects(
        inventory.get("components"),
        "inventory.components",
        ("id", "name", "version", "type", "license"),
        required=True,
    )
    if component_error is not None:
        return component_error

    dependency_error = _validate_objects(
        inventory.get("dependencies"),
        "inventory.dependencies",
        ("id", "from", "to"),
        required=False,
    )
    if dependency_error is not None:
        return dependency_error

    for name in OPTIONAL_OBJECT_COLLECTIONS:
        error = _validate_objects(
            inventory.get(name),
            f"inventory.{name}",
            ("id",),
            required=False,
        )
        if error is not None:
            return error

    provenance_error = _validate_refs(
        inventory.get("provenance_refs"),
        "inventory.provenance_refs",
        required=True,
    )
    if provenance_error is not None:
        return provenance_error

    evidence_error = _validate_refs(
        inventory.get("evidence_refs"),
        "inventory.evidence_refs",
        required=False,
    )
    if evidence_error is not None:
        return evidence_error

    component_ids = {
        item["id"]
        for item in inventory["components"]
    }

    spdx_ids = [
        item["id"].replace(":", "-")
        for item in inventory["components"]
    ]
    if len(set(spdx_ids)) != len(spdx_ids):
        return MALFORMED, "SPDX_IDENTIFIER_COLLISION"

    for index, dependency in enumerate(
        inventory.get("dependencies", [])
    ):
        if dependency["from"] not in component_ids:
            return INCOMPLETE, f"UNKNOWN_DEPENDENCY_SOURCE:{index}"

        if dependency["to"] not in component_ids:
            return INCOMPLETE, f"UNKNOWN_DEPENDENCY_TARGET:{index}"

    for index, component in enumerate(
        inventory["components"]
    ):
        if component["license"].strip().upper() in {
            "UNKNOWN",
            "NOASSERTION",
            "NONE",
        }:
            return (
                LICENSE_UNKNOWN,
                f"LICENSE_UNKNOWN:inventory.components[{index}]",
            )

    return None


def _values(
    inventory: dict[str, Any],
    name: str,
) -> list[Any]:
    value = inventory.get(name, [])
    return copy.deepcopy(value) if isinstance(value, list) else []


def _cyclonedx(
    request_id: str,
    inventory: dict[str, Any],
) -> dict[str, Any]:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "bom-ref": request_id,
                "name": request_id,
            }
        },
        "components": [
            {
                "bom-ref": item["id"],
                "type": item["type"],
                "name": item["name"],
                "version": item["version"],
                "licenses": [
                    {
                        "license": {
                            "name": item["license"],
                        }
                    }
                ],
            }
            for item in inventory["components"]
        ],
        "dependencies": [
            {
                "ref": item["from"],
                "dependsOn": [item["to"]],
            }
            for item in inventory.get("dependencies", [])
        ],
        "services": [
            {
                "bom-ref": item["id"],
                **{
                    key: copy.deepcopy(value)
                    for key, value in item.items()
                    if key != "id"
                },
            }
            for item in inventory.get("services", [])
        ],
        "aapp": {
            name: _values(inventory, name)
            for name in (
                "cryptographic_assets",
                "models",
                "datasets",
                "runtimes",
                "provenance_refs",
                "evidence_refs",
            )
        },
    }


def _spdx(
    request_id: str,
    inventory: dict[str, Any],
) -> dict[str, Any]:
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": request_id,
        "documentNamespace": f"urn:aapp:bom:{request_id}",
        "creationInfo": {
            "creators": ["Tool: AAPP-B47"],
        },
        "packages": [
            {
                "SPDXID": (
                    "SPDXRef-"
                    + item["id"].replace(":", "-")
                ),
                "name": item["name"],
                "versionInfo": item["version"],
                "primaryPackagePurpose": item["type"].upper(),
                "licenseDeclared": item["license"],
                "licenseConcluded": item["license"],
            }
            for item in inventory["components"]
        ],
        "relationships": [
            {
                "spdxElementId": (
                    "SPDXRef-"
                    + item["from"].replace(":", "-")
                ),
                "relationshipType": "DEPENDS_ON",
                "relatedSpdxElement": (
                    "SPDXRef-"
                    + item["to"].replace(":", "-")
                ),
            }
            for item in inventory.get("dependencies", [])
        ],
        "externalDocumentRefs": [],
        "annotations": [],
        "aapp": {
            name: _values(inventory, name)
            for name in (
                "cryptographic_assets",
                "models",
                "datasets",
                "runtimes",
                "services",
                "provenance_refs",
                "evidence_refs",
            )
        },
    }


def evaluate_bom_export(request: Any) -> dict[str, Any]:
    checks = _checks()

    request_error = _validate_request(request)
    if request_error is not None:
        return _result(
            request,
            *request_error,
            checks,
        )

    checks["schema_supported"] = True

    output_format = request["output_format"]
    if output_format not in {
        CYCLONEDX_JSON,
        SPDX_JSON,
    }:
        return _result(
            request,
            UNSUPPORTED_FORMAT,
            "UNSUPPORTED_OUTPUT_FORMAT",
            checks,
        )

    checks["format_supported"] = True

    inventory = request["inventory"]
    inventory_error = _validate_inventory(inventory)
    if inventory_error is not None:
        return _result(
            request,
            *inventory_error,
            checks,
        )

    for name in (
        "inventory_complete",
        "identities_valid",
        "dependencies_valid",
        "licenses_known",
        "provenance_present",
        "evidence_refs_valid",
    ):
        checks[name] = True

    try:
        if output_format == CYCLONEDX_JSON:
            bom = _cyclonedx(
                request["request_id"],
                inventory,
            )
        else:
            bom = _spdx(
                request["request_id"],
                inventory,
            )

        checks["bom_rendered"] = True
        bom_digest(bom)
        checks["bom_digest_created"] = True
    except (
        KeyError,
        TypeError,
        ValueError,
        RecursionError,
    ):
        return _result(
            request,
            MALFORMED,
            "BOM_RENDER_FAILED",
            checks,
        )

    return _result(
        request,
        EXPORTED,
        "ALL_CHECKS_PASSED",
        checks,
        bom=bom,
    )
