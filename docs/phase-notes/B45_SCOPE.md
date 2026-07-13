# B45 — TEE / Attestation Provider Adapter

## 1. Phase Name & ID

- Phase: `B45`
- Name: TEE / Attestation Provider Adapter
- Authorization issue: `#124`
- Starting commit: `eb9ae7854972059f89587322233adacf6260fcac`
- Status: `ACTIVE`
- Classification: `REFERENCE`

B45 defines one local deterministic provider-adapter contract.
It does not implement or claim live hardware attestation.

## 2. Objective / Goal

Convert one validated AAPP request and one provider-shaped evidence
record into a deterministic verdict while preserving identity,
artifact, runtime, policy, nonce, timestamp, provider and source
evidence digest bindings.

## 3. Problem Statement

AAPP has attestation-binding and workload-identity references, but
does not yet have a bounded provider-shaped adapter contract.

Without a fixed contract, later integrations could introduce
incompatible schemas, ambiguous mismatch handling, nondeterministic
time evaluation or unsupported hardware-security claims.

## 4. Scope

### In Scope

- Request and evidence schema validation.
- Provider types `local_static` and `tee_attestation_shape`.
- Canonical SHA-256 evidence digest verification.
- Deterministic binding comparison.
- Request-provided timestamp evaluation.
- Deterministic verdicts and reason codes.
- One fixture with both supported provider shapes.
- Focused unit tests and phase documentation.

Supported verdicts:

- `VERIFIED`
- `UNTRUSTED`
- `STALE`
- `NONCE_MISMATCH`
- `IDENTITY_MISMATCH`
- `DIGEST_MISMATCH`
- `MALFORMED`
- `UNSUPPORTED`

### Threat Model

B45 must reject or classify:

- Missing fields and invalid types.
- Unsupported schema or provider.
- Provider-type mismatch.
- False trust status.
- Stale or future-invalid timestamp.
- Nonce mismatch.
- Workload identity substitution.
- Artifact, runtime or policy substitution.
- Source evidence digest tampering.
- Fixture data represented as real hardware proof.

### Out of Scope / Non-Goals

- No live TEE.
- No TPM, SGX, SEV or Nitro provider call.
- No cloud-attestation call.
- No network.
- No subprocess.
- No external service.
- No KMS or HSM.
- No certificate-chain platform.
- No private key.
- No new dependency.
- No production trust or containment claim.
- No B46 provenance implementation.

### Future Considerations

A live adapter requires a separately authorized phase, pinned
provider schemas, scoped trust roots, replay controls and real
integration demand.

## 5. Metrics

### Completion Metrics / Definition of Done

- Exactly five authorized files.
- Both provider fixture cases covered.
- Every supported verdict has deterministic coverage.
- Focused and full tests pass.
- Repository guards, E2E, CI and post-merge validation pass.

### Quality & Safety Metrics

- No mismatch produces `VERIFIED`.
- Unsupported providers never produce success.
- Missing identity data never produces success.
- Source evidence digest is preserved.
- No network or subprocess import.

### Adoption / Usability Metrics

- One request shape.
- One evidence shape.
- One result shape.
- One documented Python call path.

### Performance / Scale Metrics

B45 evaluates one bounded in-memory request and evidence pair.
No production throughput or hardware-performance claim is made.

## 6. Deliverables

### Required Files

- `docs/phase-notes/B45_SCOPE.md`
- `docs/ATTESTATION_PROVIDER_ADAPTER.md`
- `aapp/attestation_provider_adapter.py`
- `tests/fixtures/attestation_provider_adapter/sample_attestation.json`
- `tests/test_attestation_provider_adapter.py`

No other repository file is authorized.

### Code Artifacts

The adapter module owns canonical encoding, digest calculation,
schema validation, timestamp parsing and deterministic evaluation.

### Documentation

The adapter document will define schemas, evaluation order,
verdict meanings, usage and claim boundaries.

### Machine-Readable Outputs

The result must contain request ID, provider type, workload identity,
artifact digest, runtime digest, policy version, nonce, attestation
timestamp, source evidence digest, verdict, reason codes and checks.

No implicit wall-clock timestamp or generated identifier is allowed.

## 7. Dependencies & Prerequisites

- B44B accepted on main.
- Issue `#124` open.
- Python standard library only.
- Existing B23 and B24 reference concepts.
- No new package or service dependency.

## 8. Key Design Decisions

1. Request and provider evidence remain separate objects.
2. Identical inputs produce identical output.
3. Time uses request-provided `evaluated_at`.
4. Evidence digest excludes the `evidence_digest` field itself.
5. Trust status must be an exact JSON boolean.
6. Boolean values are not accepted as integer limits.
7. Request and evidence provider types must match.
8. Evaluation is fail-closed.
9. Source evidence digest is preserved.
10. Fixture evidence is not hardware proof.

Evaluation order:

1. Object and schema validation.
2. Required-field and type validation.
3. Supported-provider validation.
4. Evidence digest validation.
5. Provider and trust checks.
6. Timestamp-window checks.
7. Nonce and identity checks.
8. Artifact, runtime and policy checks.
9. `VERIFIED` only after every check passes.

## 9. Validation Strategy

### Automated Validation

- Focused B45 unit tests.
- Full unit-test discovery.
- Baseline phase-manifest check.
- Claim-boundary check.
- Required-file check after all deliverables exist.
- Product E2E and tamper rejection.

### Manual Validation

- Confirm exactly five changed files.
- Confirm no new dependency.
- Confirm no network or subprocess import.
- Confirm no secret-like fixture material.
- Confirm no B46 content.

### Scenario Validation

- Valid `local_static`.
- Valid `tee_attestation_shape`.
- Malformed and unsupported input.
- False trust flag.
- Stale and future-invalid timestamps.
- Nonce, identity, artifact, runtime and policy mismatch.
- Evidence digest mismatch.
- Repeated deterministic result.

### Review Process

- Exact dirty-file guard.
- Focused and full validation.
- Exact staged-file guard.
- PR using `Refs #124`.
- CI, squash merge and post-merge validation.
- Acceptance record before issue closure.

## 10. Risks & Mitigations

- Fixture mistaken for hardware proof: enforce `REFERENCE` labeling.
- Nondeterministic time: require `evaluated_at` in the request.
- Recursive digest: exclude `evidence_digest` from digest input.
- Truthy-string bypass: require exact boolean type.
- Unsupported-provider success: use an explicit allowlist.

## 11. Kill Conditions

Stop when:

- A sixth file changes.
- A live provider or hardware call becomes necessary.
- Network, subprocess, external service or dependency appears.
- A mismatch can become `VERIFIED`.
- Source evidence digest is not preserved.
- Result depends on implicit wall-clock time.
- A required test or validation gate fails.
- B46 work enters the diff.

## 12. Success Criteria

B45 succeeds only after exactly five authorized files are accepted,
all deterministic scenarios pass, CI passes, the PR is squash-merged,
main is post-merge validated and issue `#124` closes with one
acceptance record.

## 13. Transition to Next Phase

B45 does not authorize B46.

A later phase requires a new issue, exact manifest and fresh
starting-main validation.

## 14. Timeline & Owner

- Owner: repository maintainer.
- Execution: one issue, one branch and one exact file manifest.
- Current next action: create the adapter documentation only after
  this scope file passes review.
