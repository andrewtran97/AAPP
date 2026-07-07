# B10 - Production Signing Interface

## 1. Phase Name & ID

**Phase ID:** B10
**Phase Name:** Production Signing Interface
**Phase Type:** implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #36
**Primary Issue:** Historical

---

## 2. Objective / Goal

Add detached signing for pilot/review evidence bundles.

Business goal:
- Give review packages a stronger integrity signal.

Technical goal:
- Use detached Ed25519 signatures for bundle manifests without copying private keys into bundles.

---

## 3. Problem Statement

This phase exists because:
- Review packages need signature material.
- Private keys must not enter evidence bundles.

Without this phase:
- Bundle integrity relies only on local development signing.
- Pilot package has weaker integrity proof.

---

## 4. Scope

### In Scope

- OpenSSL Ed25519 keypair/sign/verify.
- Detached manifest signature.
- Public key/profile output.
- Tampered manifest rejection.

### Out of Scope / Non-Goals

- No cryptographic module validation claim.
- No HSM/KMS integration.
- No public CA.
- No long-term key management platform.

### Future Considerations

- Signing provider interface after B27.
- Key management adapter in a separate scoped phase.

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
- `aapp/production_signing.py`

Test files:
- `tests/test_production_signing.py`

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B10_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `manifest.ed25519.sig`
- `signature.profile.json`
- `ed25519_public.pem`

### Code Artifacts

- OpenSSL Ed25519 keypair/sign/verify.
- Detached manifest signature.
- Public key/profile output.
- Tampered manifest rejection.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B5 - Unified Session Bundle
- B9 - Release Candidate Pack

### Required Tools / Libraries

- Python 3.10+
- OpenSSL

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Detached signature

Chosen:
- Sign manifest externally.

Rejected:
- Embed private key material.

Reason:
- Private key must not enter evidence package.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m unittest tests.test_production_signing -v
- python3 -m unittest discover -s tests -v
- bash scripts/run_agent_black_box_e2e.sh

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Valid signature -> verifies.
- Tampered manifest -> rejected.
- Private key -> absent from bundle.

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
| Private key leakage | High | Test absence in bundle. |
| Crypto overclaim | High | Use bounded language. |

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

- Detached signing workflow exists.

Qualitative outcome:

- Reviewer can verify manifest integrity with public key material.

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
- B11 - Offline Review / Evidence Package QA

The next phase depends on:
- Signed manifest
- Signature profile

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
- OpenSSL Ed25519 keypair/sign/verify.
- Detached manifest signature.
- Public key/profile output.
- Tampered manifest rejection.

Deferred, not removed:
- Signing provider interface after B27.
- Key management adapter in a separate scoped phase.

Final validation:
- python3 -m unittest tests.test_production_signing -v
- python3 -m unittest discover -s tests -v
- bash scripts/run_agent_black_box_e2e.sh

Final status:
- backfilled from merged historical phase
