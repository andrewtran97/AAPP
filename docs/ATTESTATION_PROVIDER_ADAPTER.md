# B45 Attestation Provider Adapter

## Status

- Phase: `B45`
- Authorization: issue `#124`
- Classification: `REFERENCE`
- Runtime class: local deterministic Python contract

This document describes testable provider-shaped evidence contracts.
It does not describe or claim live hardware attestation.

## Purpose

The adapter accepts one request object and one provider evidence
object, validates their schemas and bindings, and returns one
deterministic verdict record.

The adapter performs no network, subprocess, hardware, certificate,
KMS, HSM or cloud-provider operation.

## Supported Provider Shapes

The only supported provider identifiers are:

- `local_static`
- `tee_attestation_shape`

`tee_attestation_shape` is a fixture-compatible input shape.
It is not evidence that a TEE, TPM, SGX, SEV, Nitro Enclave or
other hardware root of trust was contacted or verified.

Both provider types normalize into the same bounded evidence schema.

## Request Schema

Schema version:

`aapp.attestation_provider_request.v1`

Required fields:

| Field | Type | Rule |
| --- | --- | --- |
| `schema_version` | string | Must equal the request schema version. |
| `request_id` | string | Must be non-empty. |
| `provider_type` | string | Must be a supported provider. |
| `workload_identity_ref` | string | Must be non-empty. |
| `expected_artifact_digest` | string | Expected artifact binding. |
| `expected_runtime_digest` | string | Expected runtime binding. |
| `expected_policy_version` | string | Expected policy binding. |
| `expected_nonce` | string | Expected replay challenge. |
| `expected_evidence_digest` | string | Expected canonical evidence digest. |
| `evaluated_at` | string | UTC RFC 3339 timestamp ending in `Z`. |
| `max_age_seconds` | integer | Non-negative; boolean is invalid. |
| `max_future_skew_seconds` | integer | Non-negative; boolean is invalid. |

Additional fields do not grant authority and are not returned as
verified bindings.

## Provider Evidence Schema

Schema version:

`aapp.attestation_provider_evidence.v1`

Required fields:

| Field | Type | Rule |
| --- | --- | --- |
| `schema_version` | string | Must equal the evidence schema version. |
| `provider_type` | string | Must match the request provider. |
| `workload_identity_ref` | string | Must match the request expectation. |
| `artifact_digest` | string | Must match the expected artifact digest. |
| `runtime_digest` | string | Must match the expected runtime digest. |
| `policy_version` | string | Must match the expected policy version. |
| `nonce` | string | Must match the expected nonce. |
| `attestation_timestamp` | string | UTC RFC 3339 timestamp ending in `Z`. |
| `trusted` | boolean | Must be an exact JSON boolean. |
| `evidence_digest` | string | Digest of canonical evidence content. |

Raw quotes, certificate chains, endorsements, private keys, access
tokens and unrestricted provider payloads are outside this contract.

## Canonical Evidence Digest

Digest algorithm: SHA-256.

Digest representation:

`sha256:<64 lowercase hexadecimal characters>`

The digest input is the evidence object after removing the
`evidence_digest` field.

Canonical JSON rules:

- UTF-8 encoding.
- Object keys sorted lexicographically.
- Compact separators with no formatting whitespace.
- JSON string and scalar semantics preserved.
- No implicit timestamp or generated value.

The request field `expected_evidence_digest` and the evidence field
`evidence_digest` must both equal the calculated canonical digest.

## Result Schema

Schema version:

`aapp.attestation_provider_verdict.v1`

Result fields:

- `schema_version`
- `request_id`
- `provider_type`
- `workload_identity_ref`
- `artifact_digest`
- `runtime_digest`
- `policy_version`
- `nonce`
- `attestation_timestamp`
- `source_evidence_digest`
- `verdict`
- `reason_codes`
- `checks`

The result contains no wall-clock-generated identifier or timestamp.

## Deterministic Evaluation Order

Evaluation stops at the first failing boundary:

1. Request and evidence must be objects.
2. Required fields and field types must be valid.
3. Schema versions must be supported.
4. Provider types must be supported.
5. Canonical evidence digest must match both supplied digests.
6. Request and evidence provider types must match.
7. Evidence trust status must be true.
8. Timestamps must parse and pass age and future-skew limits.
9. Nonce must match.
10. Workload identity must match.
11. Artifact digest must match.
12. Runtime digest must match.
13. Policy version must match.
14. Only then may the result be `VERIFIED`.

Identical inputs must produce identical output.

## Verdicts

| Verdict | Meaning |
| --- | --- |
| `VERIFIED` | Every required validation and binding check passed. |
| `UNTRUSTED` | Evidence carries an exact boolean `false` trust value. |
| `STALE` | Evidence is too old or exceeds permitted future skew. |
| `NONCE_MISMATCH` | Replay challenge binding failed. |
| `IDENTITY_MISMATCH` | Workload identity binding failed. |
| `DIGEST_MISMATCH` | Evidence, artifact, runtime or policy binding failed. |
| `MALFORMED` | Object shape, field presence, type or timestamp is invalid. |
| `UNSUPPORTED` | Schema version or provider type is unsupported. |

Reason codes must identify the specific deterministic boundary.

Examples include:

- `REQUEST_NOT_OBJECT`
- `EVIDENCE_NOT_OBJECT`
- `MISSING_REQUIRED_FIELD`
- `INVALID_FIELD_TYPE`
- `UNSUPPORTED_SCHEMA_VERSION`
- `UNSUPPORTED_PROVIDER`
- `EVIDENCE_DIGEST_MISMATCH`
- `PROVIDER_TYPE_MISMATCH`
- `EVIDENCE_UNTRUSTED`
- `EVIDENCE_STALE`
- `EVIDENCE_FROM_FUTURE`
- `NONCE_MISMATCH`
- `WORKLOAD_IDENTITY_MISMATCH`
- `ARTIFACT_DIGEST_MISMATCH`
- `RUNTIME_DIGEST_MISMATCH`
- `POLICY_VERSION_MISMATCH`
- `ALL_CHECKS_PASSED`

## Checks Object

The `checks` object records bounded boolean outcomes for:

- `schema_valid`
- `provider_supported`
- `evidence_digest_valid`
- `provider_matches`
- `trusted`
- `timestamp_valid`
- `nonce_matches`
- `identity_matches`
- `artifact_matches`
- `runtime_matches`
- `policy_matches`

A check not reached after an earlier failure remains false.

## Local Usage Shape

The intended local Python call shape is:

```python
result = evaluate_attestation_provider(request, evidence)
```

The function returns a new dictionary and does not mutate either
input object.

## Failure Semantics

- Invalid input fails closed.
- Unsupported input never becomes success.
- A mismatch never becomes `VERIFIED`.
- Evidence digest mismatch is evaluated before binding comparisons.
- No exception text, secret or raw provider payload is copied into
  the result.

## Security and Claim Boundary

B45 is a local deterministic reference adapter.

It does not provide:

- live TEE or TPM verification;
- SGX, SEV, Nitro or confidential-computing verification;
- certificate-chain or endorsement validation;
- hardware-backed trust;
- production remote attestation;
- network transport security;
- production containment;
- certification or compliance status.

A `VERIFIED` verdict means only that the supplied local request and
provider-shaped evidence satisfy this versioned deterministic
contract.

## Non-Goals

- No network.
- No subprocess.
- No external service.
- No hardware API.
- No new dependency.
- No production trust claim.
- No B46 provenance implementation.
