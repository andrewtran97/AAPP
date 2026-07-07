# B14 - Release Hygiene Audit

## 1. Phase Name & ID

**Phase ID:** B14
**Phase Name:** Release Hygiene Audit
**Phase Type:** audit / governance
**Status:** backfilled historical audit phase
**Primary PR:** Historical
**Primary Issue:** #42

---

## 2. Objective / Goal

Audit public release hygiene before expanding product surface.

Business goal:
- Reduce trust risk from stale release, claim, or packaging language.

Technical goal:
- Review repository status and release claims without adding runtime behavior.

---

## 3. Problem Statement

This phase exists because:
- Public artifacts drift.
- Claim hygiene needs a checkpoint.

Without this phase:
- Release may imply unsupported readiness.
- Reviewers see conflicting status.

---

## 4. Scope

### In Scope

- Release hygiene review.
- Claim boundary check.
- Issue/PR record review.

### Out of Scope / Non-Goals

- No production code.
- No new scanner.
- No certification claim.
- No package publication.

### Future Considerations

- Surface scan.

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
- `docs/phase-notes/B14_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `release hygiene audit record`

### Code Artifacts

- Release hygiene review.
- Claim boundary check.
- Issue/PR record review.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B13 - Apache-2.0 License

### Required Tools / Libraries

- GitHub issue/PR review
- Markdown

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Audit before expansion

Chosen:
- Review public hygiene before new scanner phases.

Rejected:
- Continue feature work without audit.

Reason:
- Stale claims compound as repo grows.

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

- Claim scan -> bounded status.
- Audit issue -> closed clean.

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
| Informal audit | Medium | Backfill this manifest. |
| Overclaim persists | High | Add later claim-boundary checks separately. |

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

- Release hygiene has a recorded gate.

Qualitative outcome:

- Maintainer can point to a hygiene checkpoint.

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
- B15 - Agent Action Surface Scan

The next phase depends on:
- Claim boundary record

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
- Release hygiene review.
- Claim boundary check.
- Issue/PR record review.

Deferred, not removed:
- Surface scan.

Final validation:
- python3 -m unittest discover -s tests -v
- bash scripts/run_agent_black_box_e2e.sh

Final status:
- backfilled historical audit phase
