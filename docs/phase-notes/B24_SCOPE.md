# B24 - Workload Identity Binding

## 1. Phase Name & ID

**Phase ID:** B24
**Phase Name:** Workload Identity Binding
**Phase Type:** identity / implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #63
**Primary Issue:** #62

---

## 2. Objective / Goal

Bind governed actions to workload identity.

Business goal:
- Let reviewers verify which workload identity produced or executed a governed action.

Technical goal:
- Validate identity claim, registry status, scope, artifact, policy allowance, expiration, and digest integrity.

---

## 3. Problem Statement

This phase exists because:
- Artifact/policy binding lacks workload identity.
- Identity and scope failure must be distinct.

Without this phase:
- Reviewer cannot separate inactive identity from wrong scope.

---

## 4. Scope

### In Scope

- Valid identity binding.
- Expired identity rejection.
- Unregistered workload rejection.
- Scope mismatch checks.
- Policy not allowed.
- Tampered identity digest rejection.
- Malformed/unsupported/unsafe verdicts.

### Out of Scope / Non-Goals

- No SPIRE deployment.
- No public CA claim.
- No mTLS sidecar.
- No TPM/enclave binding.
- No cloud IAM federation.

### Future Considerations

- Policy change ledger.
- Workload provider adapter after B27.

---

## 5. Metrics

### Completion Metrics / Definition of Done

- Required files are tracked or explicitly marked as not applicable for this historical phase.
- Required output artifacts are documented.
- Validation commands are listed.
- Scope, non-goals, risks, kill conditions, and transition criteria are explicit.
- No unsupported product, security, or certification-style claim appears.

### Quality & Safety Metrics

- No raw secrets, private keys, access tokens, or unredacted customer data in tracked files.
- Unsafe input returns deterministic unsafe or blocked behavior where applicable.
- Malformed input returns deterministic malformed behavior where applicable.
- Unsupported schema returns deterministic unsupported behavior where applicable.
- Denied or destructive paths do not execute side effects unless explicitly scoped.
- Human-readable reports and machine-readable verdicts are stable where applicable.

### Adoption / Usability Metrics

- A new reviewer can understand the phase boundary from this file.
- Required outputs use stable filenames.
- CLI, script, or workflow usage is listed where applicable.
- Non-goals prevent over-reading the phase as a broader platform.

### Performance / Scale Metrics

- No unbounded directory scan unless explicitly scoped.
- No network call unless explicitly scoped.
- Runtime remains suitable for local CI validation.
- Runtime evidence stays outside tracked source.

---

## 6. Deliverables

### Required Files

Production files:
- `aapp/workload_identity.py`

Test files:
- `tests/test_workload_identity.py`

Fixture files:
- `tests/fixtures/workload_identity/*`

Documentation:
- `docs/phase-notes/B24_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `identity.binding.json`
- `identity.verdict.json`
- `identity.report.md`

### Code Artifacts

- Valid identity binding.
- Expired identity rejection.
- Unregistered workload rejection.
- Scope mismatch checks.
- Policy not allowed.
- Tampered identity digest rejection.
- Malformed/unsupported/unsafe verdicts.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B23 - Attestation Binding Policy Link

### Required Tools / Libraries

- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Registry-backed identity

Chosen:
- Validate claim against registry/scope.

Rejected:
- Trust claim alone.

Reason:
- Identity claims need registry context.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m py_compile aapp/workload_identity.py tests/test_workload_identity.py
- python3 -m pytest tests/test_workload_identity.py tests/test_attestation_binding.py tests/test_merkle_evidence.py tests/test_network_active_scan.py tests/test_agent_black_box_scan_action.py tests/test_verify_pack.py tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Valid -> VALID.
- Expired -> EXPIRED_IDENTITY.
- Registered wrong scope -> SCOPE_MISMATCH.
- Unregistered -> IDENTITY_NOT_ACTIVE.

### Validation Script

Use the validation commands listed above for the historical phase. This backfill branch itself performs docs-only validation.

### Review Process

Implementation role:
- Creates only scoped branch changes.

CI:
- Runs automated checks and regression tests.

Human maintainer:
- Reviews scope, files, outputs, non-goals, validation, and merge decision.

Main branch:
- Becomes the official record only after merge and post-merge validation.

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---:|---|
| Verdict precedence confusion | High | Use isolated fixtures. |
| Identity provider overclaim | Medium | No deployment claim. |

---

## 11. Kill Conditions

Abort or rollback this phase if:

- Any file outside the B0-B27 docs-only allowlist is changed.
- Any runtime code, test, README, CI workflow, release asset, issue metadata, or packaging file is changed.
- Any `.aapp/` runtime evidence is staged or committed.
- Any raw secret, private key, access token, or unredacted customer data appears.
- Any phase claims certification, absolute containment, absolute tamper resistance, or absolute bypass resistance.
- Any phase invents required files that do not exist or are not intentionally created by the scoped phase.
- Any phase after B27 is edited, generated, or implemented.

---

## 12. Success Criteria

When this phase is complete, we will have:

- Workload identity is part of trust chain.

Qualitative outcome:

- Reviewer separates identity failure from scope failure.

---

## 13. Transition to Next Phase

This phase may transition to the next phase only when:

- All required files are tracked or explicitly marked not applicable.
- All required outputs are documented.
- Unit tests pass where applicable.
- Regression tests pass where applicable.
- Non-goals were not violated.
- Post-merge validation passes on `main`.

Next phase:
- B25 - Policy Change Ledger Dual Control

The next phase depends on:
- identity.binding.json

---

## 14. Timeline & Owner

Owner:
- Human maintainer / repository owner

Implementation role:
- Branch implementer

Validation role:
- CI + regression tests + post-merge validation

Target timeline:
- Historical backfill; no runtime change.


---

## 15. Final Phase Record

Built in this phase:
- Valid identity binding.
- Expired identity rejection.
- Unregistered workload rejection.
- Scope mismatch checks.
- Policy not allowed.
- Tampered identity digest rejection.
- Malformed/unsupported/unsafe verdicts.

Deferred, not removed:
- Policy change ledger.
- Workload provider adapter after B27.

Final validation:
- python3 -m py_compile aapp/workload_identity.py tests/test_workload_identity.py
- python3 -m pytest tests/test_workload_identity.py tests/test_attestation_binding.py tests/test_merkle_evidence.py tests/test_network_active_scan.py tests/test_agent_black_box_scan_action.py tests/test_verify_pack.py tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

Final status:
- backfilled from merged historical phase
