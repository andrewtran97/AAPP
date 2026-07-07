# B5 - Unified Session Bundle

## 1. Phase Name & ID

**Phase ID:** B5
**Phase Name:** Unified Session Bundle
**Phase Type:** implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #32
**Primary Issue:** Historical

---

## 2. Objective / Goal

Package hook, MCP, and Git/CI evidence into one verifiable bundle.

Business goal:
- Give reviewers one portable evidence package.

Technical goal:
- Combine traces, manifest, hashes, verification result, and report with tamper rejection.

---

## 3. Problem Statement

This phase exists because:
- Separate traces are hard to review.
- Evidence needs one portable package.
- Tampering must fail verification.

Without this phase:
- Reviewer manually correlates traces.
- Package-level verification is missing.

---

## 4. Scope

### In Scope

- Bundle creation.
- Manifest with digests.
- hashes.txt.
- Verification command.
- Session report.
- Tamper rejection.

### Out of Scope / Non-Goals

- No cloud evidence vault.
- No public transparency log.
- No compliance certification.
- No dashboard.

### Future Considerations

- GitHub Action verifier.
- IDE evidence panel.
- E2E run.

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
- `aapp/session_bundle.py`

Test files:
- `tests/test_session_bundle.py`

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B5_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `AGENT-BLACK-BOX-BUNDLE/manifest.json`
- `hashes.txt`
- `verification_result.md`
- `session.report.md`

### Code Artifacts

- Bundle creation.
- Manifest with digests.
- hashes.txt.
- Verification command.
- Session report.
- Tamper rejection.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B1 - Hook Gateway
- B3 - MCP Proxy Recorder
- B4 - Git / CI Evidence Adapter

### Required Tools / Libraries

- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Single bundle

Chosen:
- Create one bundle directory.

Rejected:
- Leave scattered traces.

Reason:
- Reviewers need portable verification.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m unittest tests.test_session_bundle -v
- python3 -m unittest discover -s tests -v

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Valid bundle -> verifies.
- Modified trace -> verification failure.

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
| Tampered trace accepted | High | Digest verification. |
| Report leaks secrets | High | Summarize without raw secret content. |

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

- One verifiable evidence bundle exists.
- Tamper rejection is tested.

Qualitative outcome:

- Reviewer can validate a session without manual reconstruction.

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
- B6 - GitHub Action Verifier

The next phase depends on:
- Unified bundle structure

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
- Bundle creation.
- Manifest with digests.
- hashes.txt.
- Verification command.
- Session report.
- Tamper rejection.

Deferred, not removed:
- GitHub Action verifier.
- IDE evidence panel.
- E2E run.

Final validation:
- python3 -m unittest tests.test_session_bundle -v
- python3 -m unittest discover -s tests -v

Final status:
- backfilled from merged historical phase
