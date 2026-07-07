# B16 - Agent Posture Scan

## 1. Phase Name & ID

**Phase ID:** B16
**Phase Name:** Agent Posture Scan
**Phase Type:** scanner / implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #46
**Primary Issue:** #45

---

## 2. Objective / Goal

Assess posture risks on discovered automation surfaces.

Business goal:
- Show which workflows/scripts have elevated permissions, secrets, stateful behavior, and rollback gaps.

Technical goal:
- Produce posture findings, stateful action list, rollback gaps, and report.

---

## 3. Problem Statement

This phase exists because:
- Surface map does not show posture risk.
- Stateful actions need rollback awareness.

Without this phase:
- Reviewer knows a workflow exists but not why it matters.
- Rollback gaps remain hidden.

---

## 4. Scope

### In Scope

- GitHub Actions permission risk detection.
- Secret/service-account references.
- CI runner agent path detection.
- Stateful command detection.
- Rollback gap detection.
- No external command execution.

### Out of Scope / Non-Goals

- No policy enforcement.
- No active network scan.
- No real rollback.
- No cloud IAM integration.

### Future Considerations

- Deterministic firewall.
- State ledger and reversal plan.

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
- `aapp/posture_scan.py`

Test files:
- `tests/test_posture_scan.py`

Fixture files:
- `tests/fixtures/posture_scan_repo/*`

Documentation:
- `docs/phase-notes/B16_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `posture.map.json`
- `posture.findings.json`
- `stateful_actions.json`
- `rollback_gaps.json`
- `posture.report.md`

### Code Artifacts

- GitHub Actions permission risk detection.
- Secret/service-account references.
- CI runner agent path detection.
- Stateful command detection.
- Rollback gap detection.
- No external command execution.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B15 - Agent Action Surface Scan

### Required Tools / Libraries

- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Static posture

Chosen:
- Analyze files statically.

Rejected:
- Run workflows to infer posture.

Reason:
- No side effects during posture analysis.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m py_compile aapp/posture_scan.py tests/test_posture_scan.py
- python3 -m pytest tests/test_posture_scan.py tests/test_surface_scan.py -q

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Elevated permission -> finding.
- Stateful command -> rollback gap.

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
| Static false positive | Medium | Use reason codes. |
| Scope drift into enforcement | Medium | Keep enforcement for later phase. |

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

- Posture risk is visible.

Qualitative outcome:

- Reviewer sees why a surface is risky.

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
- B17 - Deterministic MCP Firewall

The next phase depends on:
- posture.findings.json
- stateful_actions.json

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
- GitHub Actions permission risk detection.
- Secret/service-account references.
- CI runner agent path detection.
- Stateful command detection.
- Rollback gap detection.
- No external command execution.

Deferred, not removed:
- Deterministic firewall.
- State ledger and reversal plan.

Final validation:
- python3 -m py_compile aapp/posture_scan.py tests/test_posture_scan.py
- python3 -m pytest tests/test_posture_scan.py tests/test_surface_scan.py -q

Final status:
- backfilled from merged historical phase
