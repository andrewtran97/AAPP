from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

EVIDENCE_SCHEMA = "aapp.evidence_data.v1"
POLICY_SCHEMA = "aapp.evidence_governance_policy.v1"

ALLOWED = "ALLOWED"
REDACTED = "REDACTED"
BLOCKED = "BLOCKED"
MALFORMED = "MALFORMED"
UNSAFE = "UNSAFE"
UNSUPPORTED = "UNSUPPORTED"
RETENTION_VIOLATION = "RETENTION_VIOLATION"
EXPORT_NOT_ALLOWED = "EXPORT_NOT_ALLOWED"

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SECRET_VALUE_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
]
SECRET_KEY_RE = re.compile(r"(secret|token|api[_-]?key|password|credential)", re.IGNORECASE)

CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(obj)).hexdigest()


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def required_fields(obj: dict[str, Any], fields: list[str], prefix: str) -> str | None:
    for field in fields:
        if field not in obj:
            return f"missing_{prefix}_field:{field}"
    return None


def walk_values(obj: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    rows: list[tuple[tuple[str, ...], Any]] = []
    rows.append((path, obj))
    if isinstance(obj, dict):
        for key, value in obj.items():
            rows.extend(walk_values(value, path + (str(key),)))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            rows.extend(walk_values(value, path + (str(idx),)))
    return rows


def scan_content(obj: Any) -> dict[str, Any]:
    private_key_findings = []
    secret_findings = []
    pii_findings = []

    for path, value in walk_values(obj):
        path_str = ".".join(path) if path else "$"
        key = path[-1] if path else ""

        if isinstance(value, str):
            if PRIVATE_KEY_RE.search(value):
                private_key_findings.append({
                    "path": path_str,
                    "type": "private_key",
                    "reason": "private key marker detected",
                })

            if SECRET_KEY_RE.search(key) and value:
                secret_findings.append({
                    "path": path_str,
                    "type": "secret_key_name",
                    "reason": "secret-like field name with value",
                })

            for pattern in SECRET_VALUE_PATTERNS:
                if pattern.search(value):
                    secret_findings.append({
                        "path": path_str,
                        "type": "secret_value_pattern",
                        "reason": "secret-like value pattern detected",
                    })
                    break

            if EMAIL_RE.search(value):
                pii_findings.append({
                    "path": path_str,
                    "type": "email",
                    "reason": "email-like value detected",
                })

    return {
        "private_key_findings": private_key_findings,
        "secret_findings": secret_findings,
        "pii_findings": pii_findings,
    }


def redact_obj(obj: Any, path: tuple[str, ...] = ()) -> tuple[Any, bool]:
    changed = False

    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if SECRET_KEY_RE.search(str(key)) and isinstance(value, str) and value:
                out[key] = "[REDACTED]"
                changed = True
            else:
                redacted, child_changed = redact_obj(value, path + (str(key),))
                out[key] = redacted
                changed = changed or child_changed
        return out, changed

    if isinstance(obj, list):
        out_list = []
        for idx, value in enumerate(obj):
            redacted, child_changed = redact_obj(value, path + (str(idx),))
            out_list.append(redacted)
            changed = changed or child_changed
        return out_list, changed

    if isinstance(obj, str):
        redacted = obj
        for pattern in SECRET_VALUE_PATTERNS:
            redacted = pattern.sub("[REDACTED_SECRET]", redacted)
        if redacted != obj:
            changed = True
        return redacted, changed

    return obj, False


def governance_policy_limit(policy: dict[str, Any], classification: str) -> int | None:
    limits = policy.get("max_retention_days", {})
    if not isinstance(limits, dict):
        return None
    value = limits.get(classification)
    if value is None:
        return None
    return int(value)


def export_allowed(policy: dict[str, Any], classification: str) -> bool:
    table = policy.get("export_allowed", {})
    if not isinstance(table, dict):
        return False
    return bool(table.get(classification, False))


def evaluate_governance(evidence: dict[str, Any], policy: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    base = {
        "schema_version": "aapp.evidence_governance_verdict.v1",
        "verdict": None,
        "reason": None,
        "reason_codes": [],
        "governance": None,
        "evidence_digest_before": None,
        "evidence_digest_after": None,
        "redacted_output_written": False,
        "findings": {
            "private_key_findings": [],
            "secret_findings": [],
            "pii_findings": [],
        },
    }

    if not isinstance(evidence, dict):
        return {**base, "verdict": MALFORMED, "reason": "evidence_not_object"}, None
    if not isinstance(policy, dict):
        return {**base, "verdict": MALFORMED, "reason": "policy_not_object"}, None
    if evidence.get("schema_version") != EVIDENCE_SCHEMA:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_evidence_schema"}, None
    if policy.get("schema_version") != POLICY_SCHEMA:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_policy_schema"}, None

    evidence_required = [
        "evidence_id",
        "data_classification",
        "jurisdiction",
        "retention_days",
        "sharing_scope",
        "export_requested",
        "storage_requested",
        "payload",
    ]
    missing = required_fields(evidence, evidence_required, "evidence")
    if missing:
        return {**base, "verdict": MALFORMED, "reason": missing}, None

    policy_required = [
        "max_retention_days",
        "export_allowed",
        "redaction_mode",
        "default_retention_days",
    ]
    missing = required_fields(policy, policy_required, "policy")
    if missing:
        return {**base, "verdict": MALFORMED, "reason": missing}, None

    classification = str(evidence["data_classification"]).lower()
    if classification not in CLASSIFICATIONS:
        return {**base, "verdict": MALFORMED, "reason": "unknown_data_classification"}, None

    before_digest = sha256_digest(evidence)
    scan = scan_content(evidence)
    pii_present = bool(scan["pii_findings"])
    secret_present = bool(scan["secret_findings"])
    private_key_present = bool(scan["private_key_findings"])

    governance = {
        "schema_version": "aapp.evidence_governance.v1",
        "evidence_id": evidence["evidence_id"],
        "data_classification": classification,
        "pii_present": pii_present,
        "secret_present": secret_present,
        "private_key_present": private_key_present,
        "jurisdiction": evidence["jurisdiction"],
        "retention_days": int(evidence["retention_days"]),
        "redaction_policy_ref": policy.get("redaction_policy_ref", "default"),
        "sharing_scope": evidence["sharing_scope"],
        "export_allowed": False,
        "storage_allowed": bool(evidence["storage_requested"]),
        "reason_codes": [],
        "evidence_digest_before": before_digest,
        "evidence_digest_after": before_digest,
    }

    if private_key_present:
        governance["reason_codes"].append("PRIVATE_KEY_PRESENT")
        verdict = {
            **base,
            "verdict": UNSAFE,
            "reason": "private_key_present",
            "reason_codes": governance["reason_codes"],
            "governance": governance,
            "evidence_digest_before": before_digest,
            "evidence_digest_after": before_digest,
            "findings": scan,
        }
        return verdict, None

    limit = governance_policy_limit(policy, classification)
    if limit is None:
        return {**base, "verdict": MALFORMED, "reason": "retention_limit_missing"}, None

    if int(evidence["retention_days"]) > limit:
        governance["reason_codes"].append("RETENTION_EXCEEDS_POLICY")
        verdict = {
            **base,
            "verdict": RETENTION_VIOLATION,
            "reason": "retention_exceeds_policy",
            "reason_codes": governance["reason_codes"],
            "governance": governance,
            "evidence_digest_before": before_digest,
            "evidence_digest_after": before_digest,
            "findings": scan,
        }
        return verdict, None

    export_requested = bool(evidence["export_requested"])
    if export_requested and not export_allowed(policy, classification):
        governance["reason_codes"].append("EXPORT_NOT_ALLOWED_FOR_CLASSIFICATION")
        verdict = {
            **base,
            "verdict": EXPORT_NOT_ALLOWED,
            "reason": "export_not_allowed_for_classification",
            "reason_codes": governance["reason_codes"],
            "governance": governance,
            "evidence_digest_before": before_digest,
            "evidence_digest_after": before_digest,
            "findings": scan,
        }
        return verdict, None

    governance["export_allowed"] = (not export_requested) or export_allowed(policy, classification)

    if secret_present:
        mode = str(policy.get("redaction_mode", "redact")).lower()
        governance["reason_codes"].append("SECRET_REDACTED" if mode == "redact" else "SECRET_BLOCKED")
        if mode == "block":
            verdict = {
                **base,
                "verdict": BLOCKED,
                "reason": "secret_present_blocked_by_policy",
                "reason_codes": governance["reason_codes"],
                "governance": governance,
                "evidence_digest_before": before_digest,
                "evidence_digest_after": before_digest,
                "findings": scan,
            }
            return verdict, None

        redacted, changed = redact_obj(deepcopy(evidence))
        after_digest = sha256_digest(redacted)
        governance["evidence_digest_after"] = after_digest
        verdict = {
            **base,
            "verdict": REDACTED,
            "reason": "secret_present_redacted",
            "reason_codes": governance["reason_codes"],
            "governance": governance,
            "evidence_digest_before": before_digest,
            "evidence_digest_after": after_digest,
            "redacted_output_written": changed,
            "findings": scan,
        }
        return verdict, redacted

    if pii_present:
        governance["reason_codes"].append("PII_PRESENT")

    verdict = {
        **base,
        "verdict": ALLOWED,
        "reason": "governance_checks_passed",
        "reason_codes": governance["reason_codes"],
        "governance": governance,
        "evidence_digest_before": before_digest,
        "evidence_digest_after": before_digest,
        "findings": scan,
    }
    return verdict, None


def evaluate_from_files(evidence_path: str | Path, policy_path: str | Path, out: str | Path) -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    evidence = read_json(evidence_path)
    policy = read_json(policy_path)

    verdict, redacted = evaluate_governance(evidence, policy)

    write_json(out / "governance.verdict.json", verdict)
    if redacted is not None:
        write_json(out / "governance.redacted.json", redacted)

    report = [
        "# Evidence Data Governance",
        "",
        f"- Verdict: `{verdict['verdict']}`",
        f"- Reason: `{verdict['reason']}`",
        f"- Redacted output: `{'present' if redacted is not None else 'not_written'}`",
        f"- Reason codes: `{', '.join(verdict.get('reason_codes', []))}`",
        "",
    ]
    (out / "governance.report.md").write_text("\n".join(report), encoding="utf-8")
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify, redact, and govern Agent Black Box evidence data.")
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    verdict = evaluate_from_files(args.evidence, args.policy, args.out)
    print(f"AAPP evidence governance complete: verdict={verdict['verdict']} reason={verdict['reason']} out={Path(args.out).resolve()}")

    return 0 if verdict["verdict"] in {ALLOWED, REDACTED} else 1


if __name__ == "__main__":
    raise SystemExit(main())
