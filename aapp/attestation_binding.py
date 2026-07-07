from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "aapp.attestation_binding.v1"

VALID = "VALID"
INVALID = "INVALID"
MALFORMED = "MALFORMED"
UNSAFE = "UNSAFE"
UNSUPPORTED = "UNSUPPORTED"
STALE_POLICY = "STALE_POLICY"
POLICY_MISMATCH = "POLICY_MISMATCH"

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


def dev_signature(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(b"AAPP_DEV_ATTESTATION_SIGNATURE_V1\x00" + canonical_json(payload)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


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


def component_scan_roots(paths: list[Path]) -> list[Path]:
    roots: list[Path] = []
    seen: set[str] = set()
    parent_counts: dict[str, int] = {}

    normalized: list[Path] = []
    for raw in paths:
        path = Path(raw)
        normalized.append(path)
        if path.is_file():
            parent_key = str(path.parent.resolve())
            parent_counts[parent_key] = parent_counts.get(parent_key, 0) + 1

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

    # Only scan a parent directory when it is clearly a component package
    # containing multiple provided component files. Do not scan broad parents
    # such as /tmp because a single tampered temp file lives there.
    for path in normalized:
        if not path.is_file():
            continue
        parent = path.parent
        parent_key = str(parent.resolve())
        if parent_counts.get(parent_key, 0) >= 2:
            add(parent)

    return roots

def require_dict(name: str, obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise ValueError(f"{name}_not_object")
    return obj


def component_digest(component: dict[str, Any]) -> str:
    return sha256_digest(component)


def build_binding_statement(
    evidence: dict[str, Any],
    artifact: dict[str, Any],
    controller: dict[str, Any],
    runtime: dict[str, Any],
    policy: dict[str, Any],
    registry: dict[str, Any],
    decision: dict[str, Any],
    binding_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    evidence = require_dict("evidence", evidence)
    artifact = require_dict("artifact", artifact)
    controller = require_dict("controller", controller)
    runtime = require_dict("runtime", runtime)
    policy = require_dict("policy", policy)
    registry = require_dict("registry", registry)
    decision = require_dict("decision", decision)

    policy_id = policy.get("policy_id")
    policy_version = policy.get("policy_version")
    if not policy_id or not policy_version:
        raise ValueError("policy_id_or_version_missing")

    evidence_digest = component_digest(evidence)
    artifact_digest = component_digest(artifact)
    controller_digest = component_digest(controller)
    runtime_digest = component_digest(runtime)
    policy_digest = component_digest(policy)

    statement = {
        "schema_version": SCHEMA_VERSION,
        "binding_id": binding_id or str(uuid.uuid4()),
        "created_at": created_at or utc_now(),
        "evidence": {
            "evidence_id": str(evidence.get("evidence_id", "")),
            "evidence_digest": evidence_digest,
            "merkle_root_hash": evidence.get("merkle_root_hash"),
        },
        "artifact": {
            "artifact_id": str(artifact.get("artifact_id", "")),
            "artifact_digest": artifact_digest,
            "git_commit": artifact.get("git_commit"),
        },
        "controller": {
            "controller_id": str(controller.get("controller_id", "")),
            "controller_config_digest": controller_digest,
        },
        "runtime": {
            "runtime_id": str(runtime.get("runtime_id", "")),
            "runtime_digest": runtime_digest,
        },
        "policy": {
            "policy_id": str(policy_id),
            "policy_version": str(policy_version),
            "policy_digest": policy_digest,
            "policy_signature_ref": str(policy.get("policy_signature_ref", "")),
        },
        "decision": {
            "policy_decision": str(decision.get("policy_decision", "")),
            "reason_code": str(decision.get("reason_code", "")),
        },
        "crypto": {
            "hash_alg": "SHA-256",
            "canonicalization": "python-json-sort-keys-separators-v1",
            "signature_alg": "DEV-SHA256-PAYLOAD-DIGEST",
        },
    }

    signed_payload = dict(statement)
    binding_hash = sha256_digest({
        "schema_version": statement["schema_version"],
        "evidence_digest": evidence_digest,
        "artifact_digest": artifact_digest,
        "controller_digest": controller_digest,
        "runtime_digest": runtime_digest,
        "policy_digest": policy_digest,
        "policy_version": policy_version,
        "decision": statement["decision"],
    })
    signed_payload["binding_hash"] = binding_hash
    signed_payload["dev_signature"] = dev_signature(signed_payload)
    return signed_payload


def active_policy_entry(registry: dict[str, Any], policy_id: str) -> dict[str, Any] | None:
    policies = registry.get("active_policies", {})
    if not isinstance(policies, dict):
        return None
    entry = policies.get(policy_id)
    return entry if isinstance(entry, dict) else None


def verify_binding_statement(
    binding: dict[str, Any],
    evidence: dict[str, Any],
    artifact: dict[str, Any],
    controller: dict[str, Any],
    runtime: dict[str, Any],
    policy: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "schema_version": "aapp.attestation_verdict.v1",
        "verdict": None,
        "reason": None,
        "checks": [],
        "unsafe_findings": [],
    }

    if not isinstance(binding, dict):
        return {**base, "verdict": MALFORMED, "reason": "binding_not_object"}
    if binding.get("schema_version") != SCHEMA_VERSION:
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_binding_schema"}

    required_top = [
        "binding_id",
        "created_at",
        "evidence",
        "artifact",
        "controller",
        "runtime",
        "policy",
        "decision",
        "crypto",
        "binding_hash",
        "dev_signature",
    ]
    for key in required_top:
        if key not in binding:
            return {**base, "verdict": MALFORMED, "reason": f"missing_field:{key}"}

    if binding.get("crypto", {}).get("hash_alg") != "SHA-256":
        return {**base, "verdict": UNSUPPORTED, "reason": "unsupported_hash_alg"}

    policy_block = binding.get("policy", {})
    policy_id = policy_block.get("policy_id")
    policy_version = policy_block.get("policy_version")
    if not policy_id or not policy_version:
        return {**base, "verdict": MALFORMED, "reason": "missing_policy_id_or_version"}

    evidence_digest = component_digest(evidence)
    artifact_digest = component_digest(artifact)
    controller_digest = component_digest(controller)
    runtime_digest = component_digest(runtime)
    policy_digest = component_digest(policy)

    checks = []
    digest_checks = [
        ("evidence_digest", binding["evidence"].get("evidence_digest"), evidence_digest, INVALID),
        ("artifact_digest", binding["artifact"].get("artifact_digest"), artifact_digest, INVALID),
        ("controller_digest", binding["controller"].get("controller_config_digest"), controller_digest, INVALID),
        ("runtime_digest", binding["runtime"].get("runtime_digest"), runtime_digest, INVALID),
        ("policy_digest", binding["policy"].get("policy_digest"), policy_digest, POLICY_MISMATCH),
    ]

    for name, expected, actual, verdict_on_fail in digest_checks:
        ok = expected == actual
        checks.append({"check": name, "expected": expected, "actual": actual, "ok": ok})
        if not ok:
            return {
                **base,
                "verdict": verdict_on_fail,
                "reason": f"{name}_mismatch",
                "checks": checks,
            }

    entry = active_policy_entry(registry, str(policy_id))
    if entry is None:
        return {**base, "verdict": STALE_POLICY, "reason": "policy_not_active", "checks": checks}

    active_version = entry.get("policy_version")
    active_digest = entry.get("policy_digest")
    if active_version != policy_version:
        return {**base, "verdict": STALE_POLICY, "reason": "policy_version_not_active", "checks": checks}
    if active_digest != policy_digest:
        return {**base, "verdict": POLICY_MISMATCH, "reason": "active_policy_digest_mismatch", "checks": checks}

    recomputed_hash = sha256_digest({
        "schema_version": binding["schema_version"],
        "evidence_digest": evidence_digest,
        "artifact_digest": artifact_digest,
        "controller_digest": controller_digest,
        "runtime_digest": runtime_digest,
        "policy_digest": policy_digest,
        "policy_version": policy_version,
        "decision": binding["decision"],
    })
    checks.append({"check": "binding_hash", "expected": binding["binding_hash"], "actual": recomputed_hash, "ok": binding["binding_hash"] == recomputed_hash})
    if binding["binding_hash"] != recomputed_hash:
        return {**base, "verdict": INVALID, "reason": "binding_hash_mismatch", "checks": checks}

    signature_payload = dict(binding)
    stored_sig = signature_payload.pop("dev_signature")
    recomputed_sig = dev_signature(signature_payload)
    checks.append({"check": "dev_signature", "expected": stored_sig, "actual": recomputed_sig, "ok": stored_sig == recomputed_sig})
    if stored_sig != recomputed_sig:
        return {**base, "verdict": INVALID, "reason": "dev_signature_mismatch", "checks": checks}

    return {**base, "verdict": VALID, "reason": "all_checks_passed", "checks": checks}


def build_from_files(
    evidence_path: str | Path,
    artifact_path: str | Path,
    controller_path: str | Path,
    runtime_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
    decision_path: str | Path,
    out: str | Path,
) -> dict[str, Any]:
    paths = [Path(p) for p in [evidence_path, artifact_path, controller_path, runtime_path, policy_path, registry_path, decision_path]]
    unsafe = unsafe_findings(component_scan_roots(paths))
    if unsafe:
        raise ValueError("unsafe_component_input")

    evidence = read_json(evidence_path)
    artifact = read_json(artifact_path)
    controller = read_json(controller_path)
    runtime = read_json(runtime_path)
    policy = read_json(policy_path)
    registry = read_json(registry_path)
    decision = read_json(decision_path)

    binding = build_binding_statement(evidence, artifact, controller, runtime, policy, registry, decision)

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "attestation.binding.json", binding)

    verdict = verify_binding_statement(binding, evidence, artifact, controller, runtime, policy, registry)
    write_json(out / "attestation.verdict.json", verdict)

    report = [
        "# Attestation Binding Policy Link",
        "",
        f"- Verdict: `{verdict['verdict']}`",
        f"- Reason: `{verdict['reason']}`",
        f"- Binding ID: `{binding['binding_id']}`",
        f"- Policy: `{binding['policy']['policy_id']}@{binding['policy']['policy_version']}`",
        "",
    ]
    (out / "attestation.report.md").write_text("\n".join(report), encoding="utf-8")
    return {"binding": binding, "verdict": verdict}


def verify_from_files(
    binding_path: str | Path,
    evidence_path: str | Path,
    artifact_path: str | Path,
    controller_path: str | Path,
    runtime_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
    out: str | Path,
) -> dict[str, Any]:
    paths = [Path(p) for p in [binding_path, evidence_path, artifact_path, controller_path, runtime_path, policy_path, registry_path]]
    unsafe = unsafe_findings(component_scan_roots(paths))

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    if unsafe:
        verdict = {
            "schema_version": "aapp.attestation_verdict.v1",
            "verdict": UNSAFE,
            "reason": "unsafe_content_detected",
            "checks": [],
            "unsafe_findings": unsafe,
        }
    else:
        binding = read_json(binding_path)
        evidence = read_json(evidence_path)
        artifact = read_json(artifact_path)
        controller = read_json(controller_path)
        runtime = read_json(runtime_path)
        policy = read_json(policy_path)
        registry = read_json(registry_path)
        verdict = verify_binding_statement(binding, evidence, artifact, controller, runtime, policy, registry)

    write_json(out / "attestation.verdict.json", verdict)
    report = [
        "# Attestation Binding Verification",
        "",
        f"- Verdict: `{verdict['verdict']}`",
        f"- Reason: `{verdict['reason']}`",
        f"- Checks: `{len(verdict.get('checks', []))}`",
        f"- Unsafe findings: `{len(verdict.get('unsafe_findings', []))}`",
        "",
    ]
    (out / "attestation.report.md").write_text("\n".join(report), encoding="utf-8")
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or verify Agent Black Box attestation binding.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    bind = sub.add_parser("bind")
    bind.add_argument("--evidence", required=True)
    bind.add_argument("--artifact", required=True)
    bind.add_argument("--controller", required=True)
    bind.add_argument("--runtime", required=True)
    bind.add_argument("--policy", required=True)
    bind.add_argument("--registry", required=True)
    bind.add_argument("--decision", required=True)
    bind.add_argument("--out", required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--binding", required=True)
    verify.add_argument("--evidence", required=True)
    verify.add_argument("--artifact", required=True)
    verify.add_argument("--controller", required=True)
    verify.add_argument("--runtime", required=True)
    verify.add_argument("--policy", required=True)
    verify.add_argument("--registry", required=True)
    verify.add_argument("--out", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "bind":
        result = build_from_files(
            args.evidence,
            args.artifact,
            args.controller,
            args.runtime,
            args.policy,
            args.registry,
            args.decision,
            args.out,
        )
        verdict = result["verdict"]
        print(f"AAPP attestation bind complete: verdict={verdict['verdict']} reason={verdict['reason']} out={Path(args.out).resolve()}")
        return 0 if verdict["verdict"] == VALID else 1

    verdict = verify_from_files(
        args.binding,
        args.evidence,
        args.artifact,
        args.controller,
        args.runtime,
        args.policy,
        args.registry,
        args.out,
    )
    print(f"AAPP attestation verify complete: verdict={verdict['verdict']} reason={verdict['reason']} out={Path(args.out).resolve()}")
    return 0 if verdict["verdict"] == VALID else 1


if __name__ == "__main__":
    raise SystemExit(main())
