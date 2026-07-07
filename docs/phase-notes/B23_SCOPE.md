# B23 - Attestation Binding Policy Link

## 1. Phase Name & ID

**Phase ID:** B23
**Phase Name:** Attestation Binding Policy Link
**Phase Type:** identity / binding
**Status:** backfilled from merged historical phase plus hotfix
**Primary PR:** #60 / #61
**Primary Issue:** #59

---

## 2. Objective / Goal

Bind evidence to artifact, controller, runtime, and active policy.

Business goal:
- Let a reviewer verify which artifact and policy governed an action.

Technical goal:
- Create binding and verification logic for component digests, registry decision, and policy version.

---

## 3. Problem Statement

This phase exists because:
- Evidence alone does not prove what governed execution.
- Policy/runtime binding must be explicit.

Without this phase:
- Reviewer cannot connect evidence to artifact/runtime/policy.
- Stale policy may pass.

---

## 4. Scope

### In Scope

- Valid binding verification.
- Evidence/artifact/controller/runtime tamper rejection.
- Policy digest mismatch.
- Stale policy rejection.
- Malformed/unsupported verdicts.
- Scoped unsafe detection.

### Out of Scope / Non-Goals

- No public CA claim.
- No remote attestation.
- No TPM/enclave binding.
- No automatic policy mutation.

### Future Considerations

- Workload identity binding.
- TEE adapter after B27.

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
- `aapp/attestation_binding.py`

Test files:
- `tests/test_attestation_binding.py`

Fixture files:
- `tests/fixtures/attestation_binding/*`

Documentation:
- `docs/phase-notes/B23_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `attestation.binding.json`
- `attestation.verdict.json`
- `attestation.report.md`

### Code Artifacts

- Valid binding verification.
- Evidence/artifact/controller/runtime tamper rejection.
- Policy digest mismatch.
- Stale policy rejection.
- Malformed/unsupported verdicts.
- Scoped unsafe detection.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B22 - Merkle Evidence Transparency Receipt

### Required Tools / Libraries

- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Digest-bound components

Chosen:
- Bind by digest.

Rejected:
- Trust paths/names.

Reason:
- Paths can lie; digests are stronger.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m py_compile aapp/attestation_binding.py tests/test_attestation_binding.py
- python3 -m pytest tests/test_attestation_binding.py tests/test_merkle_evidence.py tests/test_network_active_scan.py tests/test_agent_black_box_scan_action.py tests/test_verify_pack.py tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Valid binding -> VALID.
- Tampered digest -> INVALID.
- Sibling unsafe package -> UNSAFE.

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
| Unsafe scan false positive | High | Scan explicit component files. |
| Stale policy accepted | High | Reject stale policy. |

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

- Evidence is tied to artifact/runtime/policy.

Qualitative outcome:

- Reviewer verifies governance context of evidence.

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
- B24 - Workload Identity Binding

The next phase depends on:
- attestation.binding.json

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
- Valid binding verification.
- Evidence/artifact/controller/runtime tamper rejection.
- Policy digest mismatch.
- Stale policy rejection.
- Malformed/unsupported verdicts.
- Scoped unsafe detection.

Deferred, not removed:
- Workload identity binding.
- TEE adapter after B27.

Final validation:
- python3 -m py_compile aapp/attestation_binding.py tests/test_attestation_binding.py
- python3 -m pytest tests/test_attestation_binding.py tests/test_merkle_evidence.py tests/test_network_active_scan.py tests/test_agent_black_box_scan_action.py tests/test_verify_pack.py tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

Final status:
- backfilled from merged historical phase plus hotfix
