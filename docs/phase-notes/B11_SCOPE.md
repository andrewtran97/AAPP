# B11 - Offline Review / Evidence Package QA

## 1. Phase Name & ID

**Phase ID:** B11
**Phase Name:** Offline Review / Evidence Package QA
**Phase Type:** review / QA
**Status:** backfilled from historical QA phase
**Primary PR:** #17
**Primary Issue:** Historical

---

## 2. Objective / Goal

Validate that offline evidence packages are navigable and bounded.

Business goal:
- Support review where installation is blocked.

Technical goal:
- Check offline entry points, evidence structure, and claim boundaries.

---

## 3. Problem Statement

This phase exists because:
- Install-blocked reviewers need an offline package.
- QA can be confused with independent validation.

Without this phase:
- Offline review friction stays high.
- Status language can mislead reviewers.

---

## 4. Scope

### In Scope

- Offline package QA.
- Reviewer entry point checks.
- Claim boundary review.
- Evidence navigation.

### Out of Scope / Non-Goals

- No independent validation claim.
- No certification claim.
- No runtime protocol change.
- No scanner behavior.

### Future Considerations

- README / contribution surface.
- License surface.

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
- No unique production source file for this phase.

Test files:
- `tests/test_public_demo_external_review.py`

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B11_SCOPE.md`

Scripts / Workflows:
- `scripts/build_public_demo.sh`

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `README-OFFLINE-REVIEW.txt`
- `PRODUCT_RUN_SUMMARY.txt`
- `session.report.md`
- `verification_result.md`

### Code Artifacts

- Offline package QA.
- Reviewer entry point checks.
- Claim boundary review.
- Evidence navigation.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B8 - E2E Product Run
- B9 - Release Candidate Pack
- B10 - Production Signing Interface

### Required Tools / Libraries

- Python 3.10+
- Bash

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: QA only

Chosen:
- State offline package QA.

Rejected:
- Claim independent validation.

Reason:
- Trust requires accurate status language.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m unittest tests.test_public_demo_external_review -v
- python3 -m unittest discover -s tests -v
- bash scripts/build_public_demo.sh evidence/public-demo

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Offline package -> contains review entry points.
- Claim scan -> bounded language.

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
| False validation claim | High | Use pending language. |
| Evidence leakage | High | Keep evidence ignored/redacted. |

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

- Offline package can be reviewed safely.

Qualitative outcome:

- Install-blocked reviewer can navigate without guessing.

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
- B12 - README / CONTRIBUTING Brand Surface

The next phase depends on:
- Offline package status
- Claim boundaries

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
- Offline package QA.
- Reviewer entry point checks.
- Claim boundary review.
- Evidence navigation.

Deferred, not removed:
- README / contribution surface.
- License surface.

Final validation:
- python3 -m unittest tests.test_public_demo_external_review -v
- python3 -m unittest discover -s tests -v
- bash scripts/build_public_demo.sh evidence/public-demo

Final status:
- backfilled from historical QA phase
