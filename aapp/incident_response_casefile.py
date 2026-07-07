from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CASE_OPENED = "CASE_OPENED"
CASE_NOT_REQUIRED = "CASE_NOT_REQUIRED"
CASE_CLOSED = "CASE_CLOSED"
CLOSURE_REJECTED = "CLOSURE_REJECTED"
MALFORMED = "MALFORMED"
UNSAFE = "UNSAFE"
UNSUPPORTED = "UNSUPPORTED"

SUPPORTED_SOURCE_SCHEMAS = {
    "aapp.firewall.verdict.v1",
    "aapp.verify_pack.verdict.v1",
    "aapp.evidence_governance_verdict.v1",
    "aapp.policy_change_verdict.v1",
    "aapp.network_active_scan.verdict.v1",
    "aapp.attestation_binding_verdict.v1",
    "aapp.workload_identity_verdict.v1",
}

POLICY_SCHEMA = "aapp.incident_policy.v1"
CASEFILE_SCHEMA = "aapp.incident_casefile.v1"

OPEN_CASE_VERDICTS = {
    "DENY",
    "FAILED",
    "UNSAFE",
    "INVALID",
    "SCOPE_MISMATCH",
    "REJECTED",
    "POLICY_DOWNGRADE",
    "DIGEST_MISMATCH",
    "RETENTION_VIOLATION",
    "EXPORT_NOT_ALLOWED",
    "OUT_OF_SCOPE",
    "BLOCKED",
}

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
]


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(obj)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def walk_values(obj: Any, path: tuple[str, ...] = ()) -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = [(".".join(path) if path else "$", obj)]
    if isinstance(obj, dict):
        for key, value in obj.items():
            rows.extend(walk_values(value, path + (str(key),)))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            rows.extend(walk_values(value, path + (str(idx),)))
    return rows


def unsafe_findings(obj: Any) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path, value in walk_values(obj):
        if not isinstance(value, str):
            continue

        if PRIVATE_KEY_RE.search(value):
            findings.append({
                "type": "private_key",
                "path": path,
                "reason": "private key marker detected",
            })

        for pattern in SECRET_PATTERNS:
            if pattern.search(value):
                findings.append({
                    "type": "secret_pattern",
                    "path": path,
                    "reason": "secret-like token detected",
                })
                break

    return findings


def required_fields(obj: dict[str, Any], fields: list[str], prefix: str) -> str | None:
    for field in fields:
        if field not in obj:
            return f"missing_{prefix}_field:{field}"
        value = obj[field]
        if value is None:
            return f"missing_{prefix}_field:{field}"
        if isinstance(value, str) and not value.strip():
            return f"missing_{prefix}_field:{field}"
    return None


def normalize_source(source: dict[str, Any]) -> dict[str, Any]:
    source_verdict = source.get("source_verdict") or source.get("verdict") or source.get("decision")
    if source_verdict is not None:
        source_verdict = str(source_verdict)

    return {
        "schema_version": source.get("schema_version"),
        "source_type": source.get("source_type"),
        "source_verdict": source_verdict,
        "risk_class": str(source.get("risk_class", "UNKNOWN")).upper(),
        "reason_codes": source.get("reason_codes", []),
        "affected_evidence_refs": source.get("affected_evidence_refs", []),
        "affected_policy_refs": source.get("affected_policy_refs", []),
        "affected_identity_refs": source.get("affected_identity_refs", []),
    }


def list_or_empty(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def severity_for(normalized: dict[str, Any]) -> str:
    verdict = normalized["source_verdict"]
    risk = normalized["risk_class"]

    if risk in {"DESTRUCTIVE", "CRITICAL"}:
        return "CRITICAL"
    if verdict in {"UNSAFE", "OUT_OF_SCOPE"}:
        return "CRITICAL"
    if verdict in {"DENY", "FAILED", "INVALID", "SCOPE_MISMATCH", "POLICY_DOWNGRADE"}:
        return "HIGH"
    if verdict in {"RETENTION_VIOLATION", "EXPORT_NOT_ALLOWED", "REJECTED", "DIGEST_MISMATCH", "BLOCKED"}:
        return "HIGH"
    return "MEDIUM"


def containment_for(normalized: dict[str, Any]) -> str:
    verdict = normalized["source_verdict"]
    source_type = normalized["source_type"]

    if source_type == "firewall" and verdict == "DENY":
        return "keep_denied_do_not_retry_without_approval"
    if source_type == "verify" and verdict == "FAILED":
        return "quarantine_evidence_package"
    if verdict == "UNSAFE":
        return "block_export_and_quarantine_source"
    if verdict == "OUT_OF_SCOPE":
        return "stop_active_scan_and_review_scope"
    if source_type == "policy_change":
        return "block_policy_activation_until_review"
    return "manual_review_required"


def should_open_case(normalized: dict[str, Any]) -> bool:
    return normalized["source_verdict"] in OPEN_CASE_VERDICTS


def attach_digest(obj: dict[str, Any], field: str) -> dict[str, Any]:
    clean = dict(obj)
    clean.pop(field, None)
    clean[field] = sha256_digest(clean)
    return clean


def evaluate_source(source: dict[str, Any], policy: dict[str, Any], out: str | Path) -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    base = {
        "schema_version": "aapp.incident_verdict.v1",
        "verdict": None,
        "reason": None,
        "incident_id": None,
        "casefile_written": False,
        "timeline_written": False,
        "unsafe_findings": [],
    }

    unsafe = unsafe_findings(source)
    if unsafe:
        verdict = {
            **base,
            "verdict": UNSAFE,
            "reason": "unsafe_content_detected",
            "unsafe_findings": unsafe,
        }
        write_json(out / "incident.verdict.json", verdict)
        (out / "incident.report.md").write_text("# Incident Response Casefile\n\n- Verdict: `UNSAFE`\n- Reason: `unsafe_content_detected`\n", encoding="utf-8")
        return verdict

    if not isinstance(source, dict):
        verdict = {**base, "verdict": MALFORMED, "reason": "source_not_object"}
        write_json(out / "incident.verdict.json", verdict)
        return verdict

    if not isinstance(policy, dict):
        verdict = {**base, "verdict": MALFORMED, "reason": "policy_not_object"}
        write_json(out / "incident.verdict.json", verdict)
        return verdict

    if source.get("schema_version") not in SUPPORTED_SOURCE_SCHEMAS:
        verdict = {**base, "verdict": UNSUPPORTED, "reason": "unsupported_source_schema"}
        write_json(out / "incident.verdict.json", verdict)
        return verdict

    if policy.get("schema_version") != POLICY_SCHEMA:
        verdict = {**base, "verdict": UNSUPPORTED, "reason": "unsupported_incident_policy_schema"}
        write_json(out / "incident.verdict.json", verdict)
        return verdict

    normalized = normalize_source(source)
    missing = required_fields(normalized, ["source_type", "source_verdict"], "source")
    if missing:
        verdict = {**base, "verdict": MALFORMED, "reason": missing}
        write_json(out / "incident.verdict.json", verdict)
        return verdict

    if not should_open_case(normalized):
        verdict = {
            **base,
            "verdict": CASE_NOT_REQUIRED,
            "reason": "source_verdict_does_not_require_case",
        }
        write_json(out / "incident.verdict.json", verdict)
        (out / "incident.report.md").write_text("# Incident Response Casefile\n\n- Verdict: `CASE_NOT_REQUIRED`\n", encoding="utf-8")
        return verdict

    source_digest = sha256_digest(source)
    incident_id = "inc-" + hashlib.sha256(canonical_json({
        "source_digest": source_digest,
        "source_type": normalized["source_type"],
        "source_verdict": normalized["source_verdict"],
    })).hexdigest()[:16]

    casefile = {
        "schema_version": CASEFILE_SCHEMA,
        "incident_id": incident_id,
        "source_type": normalized["source_type"],
        "source_verdict": normalized["source_verdict"],
        "source_digest": source_digest,
        "severity": severity_for(normalized),
        "status": "OPEN",
        "opened_at": source.get("timestamp") or utc_now(),
        "affected_evidence_refs": list_or_empty(normalized["affected_evidence_refs"]),
        "affected_policy_refs": list_or_empty(normalized["affected_policy_refs"]),
        "affected_identity_refs": list_or_empty(normalized["affected_identity_refs"]),
        "containment_required": True,
        "containment_action": containment_for(normalized),
        "requires_human_approval": True,
        "owner": policy.get("default_owner", "security"),
        "reason_codes": list_or_empty(normalized["reason_codes"]),
        "casefile_digest": None,
    }
    casefile = attach_digest(casefile, "casefile_digest")

    timeline_entry = {
        "schema_version": "aapp.incident_timeline_event.v1",
        "incident_id": incident_id,
        "event_type": "CASE_OPENED",
        "event_at": casefile["opened_at"],
        "source_digest": source_digest,
        "casefile_digest": casefile["casefile_digest"],
    }

    verdict = {
        **base,
        "verdict": CASE_OPENED,
        "reason": "source_verdict_requires_incident_casefile",
        "incident_id": incident_id,
        "casefile_written": True,
        "timeline_written": True,
    }

    write_json(out / "incident.casefile.json", casefile)
    write_json(out / "incident.verdict.json", verdict)
    with (out / "incident.timeline.jsonl").open("w", encoding="utf-8") as f:
        f.write(json.dumps(timeline_entry, sort_keys=True) + "\n")

    report = [
        "# Incident Response Casefile",
        "",
        f"- Verdict: `{verdict['verdict']}`",
        f"- Incident: `{incident_id}`",
        f"- Source: `{casefile['source_type']}`",
        f"- Source verdict: `{casefile['source_verdict']}`",
        f"- Severity: `{casefile['severity']}`",
        f"- Containment: `{casefile['containment_action']}`",
        "",
    ]
    (out / "incident.report.md").write_text("\n".join(report), encoding="utf-8")
    return verdict


def evaluate_from_files(source_path: str | Path, policy_path: str | Path, out: str | Path) -> dict[str, Any]:
    return evaluate_source(read_json(source_path), read_json(policy_path), out)


def close_case(casefile: dict[str, Any], closure: dict[str, Any], out: str | Path) -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    base = {
        "schema_version": "aapp.incident_verdict.v1",
        "verdict": None,
        "reason": None,
        "incident_id": casefile.get("incident_id") if isinstance(casefile, dict) else None,
        "closure_receipt_written": False,
    }

    if not isinstance(casefile, dict) or casefile.get("schema_version") != CASEFILE_SCHEMA:
        verdict = {**base, "verdict": MALFORMED, "reason": "invalid_casefile"}
        write_json(out / "incident.verdict.json", verdict)
        return verdict

    if not isinstance(closure, dict):
        verdict = {**base, "verdict": MALFORMED, "reason": "closure_not_object"}
        write_json(out / "incident.verdict.json", verdict)
        return verdict

    missing = required_fields(closure, ["resolution", "approver_id", "approved_at"], "closure")
    if missing:
        verdict = {**base, "verdict": CLOSURE_REJECTED, "reason": missing}
        write_json(out / "incident.verdict.json", verdict)
        return verdict

    receipt = {
        "schema_version": "aapp.incident_closure_receipt.v1",
        "incident_id": casefile["incident_id"],
        "status": "CLOSED",
        "resolution": closure["resolution"],
        "approver_id": closure["approver_id"],
        "approved_at": closure["approved_at"],
        "closed_at": closure.get("closed_at") or utc_now(),
        "casefile_digest": casefile["casefile_digest"],
        "closure_digest": None,
    }
    receipt = attach_digest(receipt, "closure_digest")

    verdict = {
        **base,
        "verdict": CASE_CLOSED,
        "reason": "closure_approved",
        "closure_receipt_written": True,
    }

    write_json(out / "incident.closure.receipt.json", receipt)
    write_json(out / "incident.verdict.json", verdict)

    with (out / "incident.timeline.jsonl").open("w", encoding="utf-8") as f:
        f.write(json.dumps({
            "schema_version": "aapp.incident_timeline_event.v1",
            "incident_id": casefile["incident_id"],
            "event_type": "CASE_CLOSED",
            "event_at": receipt["closed_at"],
            "closure_digest": receipt["closure_digest"],
        }, sort_keys=True) + "\n")

    (out / "incident.report.md").write_text(
        "# Incident Response Casefile\n\n- Verdict: `CASE_CLOSED`\n- Reason: `closure_approved`\n",
        encoding="utf-8",
    )
    return verdict


def close_from_files(casefile_path: str | Path, closure_path: str | Path, out: str | Path) -> dict[str, Any]:
    return close_case(read_json(casefile_path), read_json(closure_path), out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create and close Agent Black Box incident casefiles.")
    sub = parser.add_subparsers(dest="command", required=True)

    open_parser = sub.add_parser("open")
    open_parser.add_argument("--source", required=True)
    open_parser.add_argument("--policy", required=True)
    open_parser.add_argument("--out", required=True)

    close_parser = sub.add_parser("close")
    close_parser.add_argument("--casefile", required=True)
    close_parser.add_argument("--closure", required=True)
    close_parser.add_argument("--out", required=True)

    args = parser.parse_args(argv)

    if args.command == "open":
        verdict = evaluate_from_files(args.source, args.policy, args.out)
    else:
        verdict = close_from_files(args.casefile, args.closure, args.out)

    print(f"AAPP incident response casefile complete: verdict={verdict['verdict']} reason={verdict['reason']} out={Path(args.out).resolve()}")
    return 0 if verdict["verdict"] in {CASE_OPENED, CASE_NOT_REQUIRED, CASE_CLOSED} else 1


if __name__ == "__main__":
    raise SystemExit(main())
