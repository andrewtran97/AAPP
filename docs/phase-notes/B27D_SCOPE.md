# B27D Public Release Readiness Gate

## 1. Phase Name & ID

B27D — Public Release Readiness Gate.

## 2. Objective / Goal

Prepare the repository for public release review without changing runtime behavior.

## 3. Problem Statement

After B27C, a new developer can run the project locally. B27D adds public release readiness material so an external reviewer can understand what to inspect, what is in scope, and what is not claimed.

## 4. Scope

### In Scope

- Public release readiness checklist.
- External reviewer guide.
- Release notes draft.
- README public review section if needed.
- Documentation-only release readiness cleanup.

### Out of Scope / Non-Goals

- No B28 code.
- No runtime behavior change.
- No scanner behavior change.
- No policy engine behavior change.
- No orchestration engine.
- No learning pipeline.
- No dashboard.
- No paid external service dependency.
- Do not touch aapp/*.
- Do not touch tests/test_*.
- Do not touch tests/fixtures/*.
- Do not create aapp/policy_abstraction.py.
- Do not create aapp/deterministic_risk_signals.py.

### Future Considerations

B28 remains the next implementation gate after B27D is accepted on main.

## 5. Metrics

### Completion Metrics / Definition of Done

- B27D scope file exists.
- Public release readiness document exists.
- External reviewer guide exists.
- Release notes draft exists.
- README public review section exists if needed.
- Existing tests pass.
- Changed files are limited to the B27D manifest.

### Quality & Safety Metrics

- No secrets required.
- No paid service required.
- No overbroad security language.
- No public language implying external endorsement.
- No .aapp evidence committed.
- No __pycache__ remains.

### Adoption / Usability Metrics

- External reviewer can find the quickstart.
- External reviewer can find claim boundaries.
- External reviewer can find release readiness checks.
- External reviewer can find release notes draft.

### Performance / Scale Metrics

- No runtime performance claim.
- No new runtime path.
- No network dependency.

## 6. Deliverables

### Required Files

- docs/phase-notes/B27D_SCOPE.md
- docs/PUBLIC_RELEASE_READINESS.md
- docs/EXTERNAL_REVIEWER_GUIDE.md
- docs/RELEASE_NOTES_DRAFT.md
- README.md

### Code Artifacts

No runtime code artifacts.

### Documentation

- Phase note.
- Public release readiness checklist.
- External reviewer guide.
- Release notes draft.
- README public review section if needed.

### Machine-Readable Outputs

No new machine-readable runtime outputs.

## 7. Dependencies & Prerequisites

- B27C accepted on main.
- PR #77 merged.
- Issue #75 closed.
- Issue #78 open.
- Branch is b27d-public-release-readiness-gate.

## 8. Key Design Decisions

- Documentation-only gate.
- Public review support without runtime changes.
- No B28 implementation.
- No external service dependency.
- No public overclaim.

## 9. Validation Strategy

### Automated Validation

Run quickstart, repo validators, and existing unit tests.

### Manual Validation

Review public wording, changed file list, and release-readiness scope.

### Scenario Validation

External reviewer can locate quickstart, claim boundaries, release notes draft, and review checklist.

### Review Process

One PR for B27D only.

## 10. Risks & Mitigations

- Risk: B28 scope leaks into B27D. Mitigation: forbidden file guard.
- Risk: public wording overclaims readiness. Mitigation: claim boundary review.
- Risk: runtime drift. Mitigation: diff guard.
- Risk: stale bytecode. Mitigation: cleanup command.

## 11. Kill Conditions

- Runtime behavior changes.
- Scanner behavior changes.
- Policy engine behavior changes.
- B28 files appear.
- Secrets are required.
- Paid services are required.
- Public wording implies external endorsement.
- Tests regress.
- __pycache__ remains.

## 12. Success Criteria

B27D succeeds when local validation, CI, merge, and post-merge validation all pass.

## 13. Transition to Next Phase

Do not start B28 until B27D is merged and post-merge validation passes.

## 14. Timeline & Owner

Owner: repository operator. One branch, one PR, one product gate.

## 15. Final Phase Record

Status: active implementation target. Acceptance requires merge to main and post-merge validation PASS.
