from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAIMS_SCHEMA = "aapp.workload_identity_claims.v1"
REGISTRY_SCHEMA = "aapp.workload_identity_registry.v1"
BINDING_SCHEMA = "aapp.workload_identity_binding.v1"

VALID = "VALID"
INVALID = "INVALID"
MALFORMED = "MALFORMED"
UNSAFE = "UNSAFE"
UNSUPPORTED = "UNSUPPORTED"
EXPIRED_IDENTITY = "EXPIRED_IDENTITY"
IDENTITY_NOT_ACTIVE = "IDENTITY_NOT_ACTIVE"
SCOPE_MISMATCH = "SCOPE_MISMATCH"
POLICY_NOT_ALLOWED = "POLICY_NOT_ALLOWED"

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


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp_invalid")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp_missing_timezone")
    return parsed.astimezone(timezone.utc)


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def component_scan_roots(paths: list[Path]) -> list[Path]:
    roots: list[Path] = []
    seen: set[str] = set()
    parent_counts: dict[str, int] = {}

    normalized = [Path(p) for p in paths]
    for path in normalized:
        if path.is_file():
            key = str(path.parent.resolve())
            parent_counts[key] = parent_counts.get(key, 0) + 1

    def add(candidate: Path) -> None:
        try:
            key = str(candidate.resolve() if candidate.exists() else candidate.absolute())
        except OSError:
            key = str(candidate.absolute())
        if key not in seen:
            seen.add(key)
            roots.append(candidate)

    for path in normalized:
        add(path)

    for path in normalized:
        if not path.is_file():
            continue
        parent = path.parent
        if parent_counts.get(str(parent.resolve()), 0) >= 2:
            add(parent)

    return roots


def unsafe_findings(paths: list[Path]) -> list[dict[str, Any]]:
    findings = []
    files = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend([p for p in path.rglob("*") if p.is_file()])

    for path in files:
        text = safe_text(path)

        if PRIVATE_KEY_RE.search(text):
            findings.append({
                "type": "private_key",
                "file_path": str(path),
                "reason": "private key marker detected",
            })

        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({
                    "type": "secret_pattern",
                    "file_path": str(path),
                    "reason": "secret-like token detected",
                })
                break

    return findings


def identity_digest(claims: dict[str, Any]) -> str:
    clean = dict(claims)
    clean.pop("identity_digest", None)
    return sha256_digest(clean)


def dev_signature(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(
        b"AAPP_DEV_WORKLOAD_IDENTITY_SIGNATURE_V1\x00" + canonical_json(payload)
    ).hexdigest()


def active_registry_entry(registry: dict[str, Any], workload_id: str) -> dict[str, Any] | None:
    entries = registry.get("active_identities", {})
    if not isinstance(entries, dict):
        return None
    entry = entries.get(workload_id)
    return entry if isinstance(entry, dict) else None


def verify_identity_claims(claims: dict[str, Any], registry: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    now = now or utc_now()
    checks = []

    if not isinstance(claims, dict):
        return {"verdict": MALFORMED, "reason": "identity_claims_not_object", "checks": checks}
    if claims.get("schema_version") != CLAIMS_SCHEMA:
        return {"verdict": UNSUPPORTED, "reason": "unsupported_identity_schema", "checks": checks}
    if not isinstance(registry, dict):
        return {"verdict": MALFORMED, "reason": "registry_not_object", "checks": checks}
    if registry.get("schema_version") != REGISTRY_SCHEMA:
        return {"verdict": UNSUPPORTED, "reason": "unsupported_registry_schema", "checks": checks}

    required = [
        "identity_id",
        "issuer",
        "subject",
        "trust_domain",
        "workload_id",
        "svid_type",
        "not_before",
        "not_after",
        "controller_id",
        "artifact_id",
        "allowed_policy_ids",
        "allowed_actions",
        "identity_digest",
    ]
    for key in required:
        if key not in claims:
            return {"verdict": MALFORMED, "reason": f"missing_identity_field:{key}", "checks": checks}

    actual_digest = identity_digest(claims)
    checks.append({
        "check": "identity_digest",
        "expected": claims.get("identity_digest"),
        "actual": actual_digest,
        "ok": claims.get("identity_digest") == actual_digest,
    })
    if claims.get("identity_digest") != actual_digest:
        return {"verdict": INVALID, "reason": "identity_digest_mismatch", "checks": checks}

    try:
        not_before = parse_time(claims["not_before"])
        not_after = parse_time(claims["not_after"])
    except Exception:
        return {"verdict": MALFORMED, "reason": "identity_time_invalid", "checks": checks}

    if now < not_before:
        return {"verdict": EXPIRED_IDENTITY, "reason": "identity_not_before_window", "checks": checks}
    if now >= not_after:
        return {"verdict": EXPIRED_IDENTITY, "reason": "identity_expired", "checks": checks}

    trust_domains = registry.get("trust_domains", [])
    if claims.get("trust_domain") not in trust_domains:
        return {"verdict": SCOPE_MISMATCH, "reason": "trust_domain_not_allowed", "checks": checks}

    entry = active_registry_entry(registry, str(claims["workload_id"]))
    if entry is None:
        return {"verdict": IDENTITY_NOT_ACTIVE, "reason": "workload_not_registered", "checks": checks}

    if entry.get("status") != "ACTIVE":
        return {"verdict": IDENTITY_NOT_ACTIVE, "reason": "identity_not_active", "checks": checks}

    for field in ["identity_id", "subject", "trust_domain", "identity_digest"]:
        expected = entry.get(field)
        actual = claims.get(field)
        checks.append({"check": f"registry_{field}", "expected": expected, "actual": actual, "ok": expected == actual})
        if expected != actual:
            return {"verdict": IDENTITY_NOT_ACTIVE, "reason": f"registry_{field}_mismatch", "checks": checks}

    return {"verdict": VALID, "reason": "identity_claims_valid", "checks": checks}


def build_identity_binding(claims: dict[str, Any], registry: dict[str, Any], attestation: dict[str, Any]) -> dict[str, Any]:
    binding_payload = {
        "schema_version": BINDING_SCHEMA,
        "binding_id": str(uuid.uuid4()),
        "created_at": iso_now(),
        "identity": {
            "identity_id": claims.get("identity_id"),
            "issuer": claims.get("issuer"),
            "subject": claims.get("subject"),
            "trust_domain": claims.get("trust_domain"),
            "workload_id": claims.get("workload_id"),
            "svid_type": claims.get("svid_type"),
            "identity_digest": claims.get("identity_digest"),
        },
        "attestation": {
            "binding_hash": attestation.get("binding_hash"),
            "controller_id": attestation.get("controller", {}).get("controller_id"),
            "artifact_id": attestation.get("artifact", {}).get("artifact_id"),
            "policy_id": attestation.get("policy", {}).get("policy_id"),
            "policy_version": attestation.get("policy", {}).get("policy_version"),
            "policy_decision": attestation.get("decision", {}).get("policy_decision"),
        },
        "registry": {
            "registry_digest": sha256_digest(registry),
        },
        "crypto": {
            "hash_alg": "SHA-256",
            "canonicalization": "python-json-sort-keys-separators-v1",
            "signature_alg": "DEV-SHA256-PAYLOAD-DIGEST",
        },
    }

    binding_hash = sha256_digest({
        "identity_digest": binding_payload["identity"]["identity_digest"],
        "attestation_binding_hash": binding_payload["attestation"]["binding_hash"],
        "controller_id": binding_payload["attestation"]["controller_id"],
        "artifact_id": binding_payload["attestation"]["artifact_id"],
        "policy_id": binding_payload["attestation"]["policy_id"],
        "policy_version": binding_payload["attestation"]["policy_version"],
        "registry_digest": binding_payload["registry"]["registry_digest"],
    })
    binding_payload["binding_hash"] = binding_hash
    binding_payload["dev_signature"] = dev_signature(binding_payload)
    return binding_payload


def verify_binding(
    claims: dict[str, Any],
    registry: dict[str, Any],
    attestation: dict[str, Any],
    binding: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    base = {
        "schema_version": "aapp.workload_identity_verdict.v1",
        "verdict": None,
        "reason": None,
        "checks": [],
        "unsafe_findings": [],
    }

    identity_result = verify_identity_claims(claims, registry, now=now)
    if identity_result["verdict"] != VALID:
        return {
            **base,
            "verdict": identity_result["verdict"],
            "reason": identity_result["reason"],
            "checks": identity_result.get("checks", []),
        }

    if not isinstance(attestation, dict):
        return {**base, "verdict": MALFORMED, "reason": "attestation_not_object"}
    if not attestation.get("binding_hash"):
        return {**base, "verdict": MALFORMED, "reason": "attestation_binding_hash_missing"}

    att_controller = attestation.get("controller", {}).get("controller_id")
    att_artifact = attestation.get("artifact", {}).get("artifact_id")
    att_policy_id = attestation.get("policy", {}).get("policy_id")
    att_decision = attestation.get("decision", {}).get("policy_decision")

    if claims.get("controller_id") != att_controller:
        return {**base, "verdict": SCOPE_MISMATCH, "reason": "controller_id_mismatch"}
    if claims.get("artifact_id") != att_artifact:
        return {**base, "verdict": SCOPE_MISMATCH, "reason": "artifact_id_mismatch"}

    allowed_policy_ids = claims.get("allowed_policy_ids")
    if not isinstance(allowed_policy_ids, list) or att_policy_id not in allowed_policy_ids:
        return {**base, "verdict": POLICY_NOT_ALLOWED, "reason": "policy_id_not_allowed"}

    allowed_actions = claims.get("allowed_actions")
    if not isinstance(allowed_actions, list) or att_decision not in allowed_actions:
        return {**base, "verdict": POLICY_NOT_ALLOWED, "reason": "policy_decision_not_allowed"}

    expected_binding = build_identity_binding(claims, registry, attestation)

    checks = identity_result.get("checks", [])
    if binding is not None:
        if not isinstance(binding, dict):
            return {**base, "verdict": MALFORMED, "reason": "identity_binding_not_object", "checks": checks}
        if binding.get("schema_version") != BINDING_SCHEMA:
            return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_identity_binding_schema", "checks": checks}

        for field in ["identity", "attestation", "registry", "binding_hash"]:
            ok = binding.get(field) == expected_binding.get(field)
            checks.append({"check": f"binding_{field}", "ok": ok})
            if not ok:
                return {**base, "verdict": INVALID, "reason": f"binding_{field}_mismatch", "checks": checks}

        sig_payload = dict(binding)
        stored_sig = sig_payload.pop("dev_signature", None)
        recomputed_sig = dev_signature(sig_payload)
        if stored_sig != recomputed_sig:
            return {**base, "verdict": INVALID, "reason": "binding_signature_mismatch", "checks": checks}

    return {
        **base,
        "verdict": VALID,
        "reason": "all_checks_passed",
        "checks": checks,
        "binding": expected_binding,
    }


def build_from_files(identity_path: str | Path, registry_path: str | Path, attestation_path: str | Path, out: str | Path) -> dict[str, Any]:
    paths = [Path(identity_path), Path(registry_path), Path(attestation_path)]
    unsafe = unsafe_findings(component_scan_roots(paths))

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    if unsafe:
        verdict = {
            "schema_version": "aapp.workload_identity_verdict.v1",
            "verdict": UNSAFE,
            "reason": "unsafe_content_detected",
            "checks": [],
            "unsafe_findings": unsafe,
        }
        write_json(out / "identity.verdict.json", verdict)
        (out / "identity.report.md").write_text("# Workload Identity Binding\n\nUNSAFE content detected.\n", encoding="utf-8")
        return {"binding": None, "verdict": verdict}

    claims = read_json(identity_path)
    registry = read_json(registry_path)
    attestation = read_json(attestation_path)

    verdict = verify_binding(claims, registry, attestation)
    binding = verdict.get("binding")
    if binding:
        write_json(out / "identity.binding.json", binding)

    clean_verdict = dict(verdict)
    clean_verdict.pop("binding", None)
    write_json(out / "identity.verdict.json", clean_verdict)

    report = [
        "# Workload Identity Binding",
        "",
        f"- Verdict: `{clean_verdict['verdict']}`",
        f"- Reason: `{clean_verdict['reason']}`",
        f"- Identity: `{claims.get('identity_id') if isinstance(claims, dict) else None}`",
        f"- Workload: `{claims.get('workload_id') if isinstance(claims, dict) else None}`",
        "",
    ]
    (out / "identity.report.md").write_text("\n".join(report), encoding="utf-8")
    return {"binding": binding, "verdict": clean_verdict}


def verify_from_files(
    identity_path: str | Path,
    registry_path: str | Path,
    attestation_path: str | Path,
    binding_path: str | Path,
    out: str | Path,
) -> dict[str, Any]:
    paths = [Path(identity_path), Path(registry_path), Path(attestation_path), Path(binding_path)]
    unsafe = unsafe_findings(component_scan_roots(paths))

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    if unsafe:
        verdict = {
            "schema_version": "aapp.workload_identity_verdict.v1",
            "verdict": UNSAFE,
            "reason": "unsafe_content_detected",
            "checks": [],
            "unsafe_findings": unsafe,
        }
    else:
        claims = read_json(identity_path)
        registry = read_json(registry_path)
        attestation = read_json(attestation_path)
        binding = read_json(binding_path)
        verdict = verify_binding(claims, registry, attestation, binding=binding)
        verdict.pop("binding", None)

    write_json(out / "identity.verdict.json", verdict)
    report = [
        "# Workload Identity Verification",
        "",
        f"- Verdict: `{verdict['verdict']}`",
        f"- Reason: `{verdict['reason']}`",
        f"- Checks: `{len(verdict.get('checks', []))}`",
        f"- Unsafe findings: `{len(verdict.get('unsafe_findings', []))}`",
        "",
    ]
    (out / "identity.report.md").write_text("\n".join(report), encoding="utf-8")
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or verify workload identity binding.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    bind = sub.add_parser("bind")
    bind.add_argument("--identity", required=True)
    bind.add_argument("--registry", required=True)
    bind.add_argument("--attestation", required=True)
    bind.add_argument("--out", required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--identity", required=True)
    verify.add_argument("--registry", required=True)
    verify.add_argument("--attestation", required=True)
    verify.add_argument("--binding", required=True)
    verify.add_argument("--out", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "bind":
        result = build_from_files(args.identity, args.registry, args.attestation, args.out)
        verdict = result["verdict"]
        print(f"AAPP workload identity bind complete: verdict={verdict['verdict']} reason={verdict['reason']} out={Path(args.out).resolve()}")
        return 0 if verdict["verdict"] == VALID else 1

    verdict = verify_from_files(args.identity, args.registry, args.attestation, args.binding, args.out)
    print(f"AAPP workload identity verify complete: verdict={verdict['verdict']} reason={verdict['reason']} out={Path(args.out).resolve()}")
    return 0 if verdict["verdict"] == VALID else 1


if __name__ == "__main__":
    raise SystemExit(main())
