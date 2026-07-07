# B8 - E2E Product Run

## 1. Phase Name & ID

**Phase ID:** B8
**Phase Name:** E2E Product Run
**Phase Type:** validation
**Status:** backfilled from merged historical phase
**Primary PR:** #35
**Primary Issue:** Historical

---

## 2. Objective / Goal

Connect the core product path into one repeatable local run.

Business goal:
- Give a reviewer one command to prove the core flow.

Technical goal:
- Run hook, MCP, Git/CI, bundle, report, verification, and tamper rejection together.

---

## 3. Problem Statement

This phase exists because:
- Modules can pass separately but fail together.
- Reviewers need a single smoke test.

Without this phase:
- Product behavior is hard to reproduce.
- Integration drift goes unnoticed.

---

## 4. Scope

### In Scope

- End-to-end product script.
- Hook/MCP/Git-CI trace creation.
- Bundle creation.
- Verification.
- Tamper rejection.
- Summary output.

### Out of Scope / Non-Goals

- No live target.
- No cloud service.
- No packaging publication.
- No performance benchmark.

### Future Considerations

- Release candidate package.
- Detached signing.

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
- `tests/test_e2e_product_run.py`

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B8_SCOPE.md`

Scripts / Workflows:
- `scripts/run_agent_black_box_e2e.sh`

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `PRODUCT_RUN_SUMMARY.txt`
- `github-action-style-report.md`
- `session-bundle/AGENT-BLACK-BOX-BUNDLE/*`

### Code Artifacts

- End-to-end product script.
- Hook/MCP/Git-CI trace creation.
- Bundle creation.
- Verification.
- Tamper rejection.
- Summary output.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B1 - Hook Gateway
- B3 - MCP Proxy Recorder
- B4 - Git / CI Evidence Adapter
- B5 - Unified Session Bundle
- B6 - GitHub Action Verifier

### Required Tools / Libraries

- Bash
- Python 3.10+
- Git

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Local E2E first

Chosen:
- Use local reproducible script.

Rejected:
- Require cloud setup.

Reason:
- Cold reviewers need low-friction validation.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- bash scripts/run_agent_black_box_e2e.sh
- python3 -m unittest tests.test_e2e_product_run -v
- python3 -m unittest discover -s tests -v

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Normal E2E -> PASS.
- Tampered bundle -> rejected.

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
| Integration drift | High | Run E2E after phase changes. |
| Runtime artifacts staged | High | Keep outputs ignored. |

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

- One repeatable proof path exists.

Qualitative outcome:

- Reviewer can understand product flow with one command.

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
- B9 - Release Candidate Pack

The next phase depends on:
- E2E output structure

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
- End-to-end product script.
- Hook/MCP/Git-CI trace creation.
- Bundle creation.
- Verification.
- Tamper rejection.
- Summary output.

Deferred, not removed:
- Release candidate package.
- Detached signing.

Final validation:
- bash scripts/run_agent_black_box_e2e.sh
- python3 -m unittest tests.test_e2e_product_run -v
- python3 -m unittest discover -s tests -v

Final status:
- backfilled from merged historical phase
