# B26 - Evidence Data Governance

## 1. Phase Name & ID

**Phase ID:** B26
**Phase Name:** Evidence Data Governance
**Phase Type:** data governance
**Status:** backfilled from merged historical phase
**Primary PR:** #67
**Primary Issue:** #66

---

## 2. Objective / Goal

Classify, redact, block, or reject evidence before storage/export/sharing.

Business goal:
- Prevent evidence trust from becoming data leakage risk.

Technical goal:
- Apply classification, retention, redaction, export rules, unsafe detection, and governance verdict output.

---

## 3. Problem Statement

This phase exists because:
- Evidence may contain sensitive or restricted data.
- Verification output can leak secrets.
- Retention/export boundaries must be explicit.

Without this phase:
- Evidence can be exported without governance.
- Secrets may leak through reports.

---

## 4. Scope

### In Scope

- Clean evidence ALLOWED.
- Secret evidence REDACTED/BLOCKED by policy.
- Private key evidence UNSAFE.
- Restricted export rejected.
- Retention violation verdict.
- Malformed/unsupported verdicts.

### Out of Scope / Non-Goals

- No DLP SaaS integration.
- No legal certification claim.
- No automatic deletion from external systems.
- No cloud KMS integration.
- No privacy-preserving ML.

### Future Considerations

- Incident response casefile.
- Tool data-flow governance after B27.

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
- `aapp/evidence_data_governance.py`

Test files:
- `tests/test_evidence_data_governance.py`

Fixture files:
- `tests/fixtures/evidence_data_governance/*`

Documentation:
- `docs/phase-notes/B26_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `governance.verdict.json`
- `governance.redacted.json`
- `governance.report.md`

### Code Artifacts

- Clean evidence ALLOWED.
- Secret evidence REDACTED/BLOCKED by policy.
- Private key evidence UNSAFE.
- Restricted export rejected.
- Retention violation verdict.
- Malformed/unsupported verdicts.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B25 - Policy Change Ledger Dual Control

### Required Tools / Libraries

- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Govern before export

Chosen:
- Classify/redact/block before sharing.

Rejected:
- Verify first and govern later.

Reason:
- Verification artifacts can leak data.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m py_compile aapp/evidence_data_governance.py tests/test_evidence_data_governance.py
- python3 -m pytest tests/test_evidence_data_governance.py tests/test_policy_change_ledger.py tests/test_workload_identity.py tests/test_attestation_binding.py tests/test_merkle_evidence.py tests/test_network_active_scan.py tests/test_agent_black_box_scan_action.py tests/test_verify_pack.py tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Public clean -> ALLOWED.
- Private key -> UNSAFE.
- Restricted export -> rejected.

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
| Evidence leakage | High | Redact/block governed outputs. |
| Compliance overclaim | High | Use bounded language. |

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

- Evidence gets a governance verdict.

Qualitative outcome:

- Reviewer sees exposure control, not only integrity.

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
- B27 - Incident Response Casefile

The next phase depends on:
- governance.verdict.json

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
- Clean evidence ALLOWED.
- Secret evidence REDACTED/BLOCKED by policy.
- Private key evidence UNSAFE.
- Restricted export rejected.
- Retention violation verdict.
- Malformed/unsupported verdicts.

Deferred, not removed:
- Incident response casefile.
- Tool data-flow governance after B27.

Final validation:
- python3 -m py_compile aapp/evidence_data_governance.py tests/test_evidence_data_governance.py
- python3 -m pytest tests/test_evidence_data_governance.py tests/test_policy_change_ledger.py tests/test_workload_identity.py tests/test_attestation_binding.py tests/test_merkle_evidence.py tests/test_network_active_scan.py tests/test_agent_black_box_scan_action.py tests/test_verify_pack.py tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

Final status:
- backfilled from merged historical phase
