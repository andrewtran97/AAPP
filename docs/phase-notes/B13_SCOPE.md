# B13 - Apache-2.0 License

## 1. Phase Name & ID

**Phase ID:** B13
**Phase Name:** Apache-2.0 License
**Phase Type:** legal / documentation
**Status:** backfilled from merged historical phase
**Primary PR:** #41
**Primary Issue:** Historical

---

## 2. Objective / Goal

Make repository usage rights explicit.

Business goal:
- Support open adoption with clear licensing.

Technical goal:
- Add Apache License 2.0 and README license reference.

---

## 3. Problem Statement

This phase exists because:
- No explicit license blocks reuse.
- Reviewers need usage rights.

Without this phase:
- Usage rights remain unclear.
- Adoption friction remains high.

---

## 4. Scope

### In Scope

- Apache-2.0 license file.
- README license reference.

### Out of Scope / Non-Goals

- No protocol change.
- No runtime change.
- No certification claim.

### Future Considerations

- Release hygiene audit.

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
- `LICENSE`
- `README.md`
- `docs/phase-notes/B13_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `LICENSE`

### Code Artifacts

- Apache-2.0 license file.
- README license reference.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B12 - README / CONTRIBUTING Brand Surface

### Required Tools / Libraries

- Markdown

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Apache-2.0

Chosen:
- Use Apache License 2.0.

Rejected:
- Keep no explicit license.

Reason:
- Explicit reuse rights reduce adoption friction.

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

- License file present -> usage rights explicit.

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
| License mismatch | High | Use standard license file. |
| README inconsistency | Medium | Reference LICENSE. |

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

- Repo has explicit open-source license.

Qualitative outcome:

- Reviewer sees license immediately.

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
- B14 - Release Hygiene Audit

The next phase depends on:
- License file

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
- Apache-2.0 license file.
- README license reference.

Deferred, not removed:
- Release hygiene audit.

Final validation:
- python3 -m unittest discover -s tests -v
- bash scripts/run_agent_black_box_e2e.sh

Final status:
- backfilled from merged historical phase
