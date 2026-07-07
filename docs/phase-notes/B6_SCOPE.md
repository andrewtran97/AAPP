# B6 - GitHub Action Verifier

## 1. Phase Name & ID

**Phase ID:** B6
**Phase Name:** GitHub Action Verifier
**Phase Type:** workflow adapter
**Status:** backfilled from merged historical phase
**Primary PR:** #33
**Primary Issue:** Historical

---

## 2. Objective / Goal

Allow CI to verify an Agent Black Box evidence bundle.

Business goal:
- Make evidence verification visible in pull-request workflows.

Technical goal:
- Provide a composite GitHub Action verifier for unified bundles.

---

## 3. Problem Statement

This phase exists because:
- Manual verification does not fit CI.
- Tampered bundle needs automated failure signal.

Without this phase:
- Bundle verification stays local only.
- CI cannot prove evidence validity.

---

## 4. Scope

### In Scope

- Composite verifier action.
- Bundle verify command.
- Tamper failure path.

### Out of Scope / Non-Goals

- No scan action.
- No artifact upload action.
- No marketplace publication.

### Future Considerations

- IDE panel.
- E2E run.
- Scan action later.

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
- `tests/test_github_action_verifier.py`

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B6_SCOPE.md`

Scripts / Workflows:
- `.github/actions/agent-black-box-verify/action.yml`

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `GitHub Action verification result`

### Code Artifacts

- Composite verifier action.
- Bundle verify command.
- Tamper failure path.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B5 - Unified Session Bundle

### Required Tools / Libraries

- GitHub Actions
- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Composite action first

Chosen:
- Use local composite action.

Rejected:
- Publish marketplace action immediately.

Reason:
- Keep interface reviewable before distribution.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m unittest tests.test_github_action_verifier -v
- python3 -m unittest discover -s tests -v

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Valid bundle -> action succeeds.
- Tampered bundle -> action fails.

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
| False pass | High | Tamper tests. |
| Packaging drift | Medium | Keep local until stable. |

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

- CI can verify bundles.

Qualitative outcome:

- Reviewer can see evidence verification as an automated check.

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
- B7 - VS Code / Cursor Evidence Panel

The next phase depends on:
- Bundle verifier action

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
- Composite verifier action.
- Bundle verify command.
- Tamper failure path.

Deferred, not removed:
- IDE panel.
- E2E run.
- Scan action later.

Final validation:
- python3 -m unittest tests.test_github_action_verifier -v
- python3 -m unittest discover -s tests -v

Final status:
- backfilled from merged historical phase
