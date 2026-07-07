# B9 - Release Candidate Pack

## 1. Phase Name & ID

**Phase ID:** B9
**Phase Name:** Release Candidate Pack
**Phase Type:** release / review
**Status:** backfilled from historical release phase
**Primary PR:** Historical
**Primary Issue:** Historical

---

## 2. Objective / Goal

Create a bounded reviewable release candidate package.

Business goal:
- Support offline and install-blocked review without overclaiming validation.

Technical goal:
- Package E2E evidence and baseline markers for review navigation.

---

## 3. Problem Statement

This phase exists because:
- Reviewers may be install-blocked.
- Release language can overclaim readiness.

Without this phase:
- External review starts from unclear artifacts.
- Status language may be misleading.

---

## 4. Scope

### In Scope

- Release candidate tag.
- Offline evidence package.
- Reviewer navigation.
- Baseline marker.

### Out of Scope / Non-Goals

- No independent validation claim.
- No certification claim.
- No package-manager publication.

### Future Considerations

- Detached signing.
- Offline package QA.

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
- No unique tracked test file for this phase.

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B9_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `release candidate package`
- `baseline tag`
- `offline evidence package`

### Code Artifacts

- Release candidate tag.
- Offline evidence package.
- Reviewer navigation.
- Baseline marker.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B8 - E2E Product Run

### Required Tools / Libraries

- Git
- GitHub Releases if release assets are used

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Bounded status

Chosen:
- State package availability only.

Rejected:
- Claim independent validation.

Reason:
- Validation must not be claimed without evidence.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m unittest discover -s tests -v
- bash scripts/run_agent_black_box_e2e.sh

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Offline package -> reviewer has entry points.

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
| Overclaim | High | Use bounded status language. |
| Incomplete package | Medium | Use checklist. |

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

- Bounded release candidate exists.

Qualitative outcome:

- Reviewer knows what is available and what is pending.

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
- B10 - Production Signing Interface

The next phase depends on:
- Review package
- Baseline marker

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
- Release candidate tag.
- Offline evidence package.
- Reviewer navigation.
- Baseline marker.

Deferred, not removed:
- Detached signing.
- Offline package QA.

Final validation:
- python3 -m unittest discover -s tests -v
- bash scripts/run_agent_black_box_e2e.sh

Final status:
- backfilled from historical release phase
