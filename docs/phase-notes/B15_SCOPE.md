# B15 - Agent Action Surface Scan

## 1. Phase Name & ID

**Phase ID:** B15
**Phase Name:** Agent Action Surface Scan
**Phase Type:** scanner / implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #44
**Primary Issue:** #43

---

## 2. Objective / Goal

Find where agent or automation actions can occur in a repository.

Business goal:
- Give reviewers a map of risky action surfaces before deeper controls.

Technical goal:
- Scan workflows, scripts, and automation files and emit JSON, Markdown, metrics, and SARIF outputs.

---

## 3. Problem Statement

This phase exists because:
- Agent action surfaces are scattered.
- Reviewers need a map before posture/policy analysis.

Without this phase:
- Risky automation remains invisible.
- Next phases lack target inputs.

---

## 4. Scope

### In Scope

- Workflow detection.
- Script detection.
- Finding generation.
- JSON/Markdown/SARIF outputs.
- No external command execution.

### Out of Scope / Non-Goals

- No active network scan.
- No exploit testing.
- No posture enforcement.
- No runtime execution.

### Future Considerations

- Posture scan.
- Scoped active scan.

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
- `aapp/surface_scan.py`

Test files:
- `tests/test_surface_scan.py`

Fixture files:
- `tests/fixtures/surface_scan_repo/*`

Documentation:
- `docs/phase-notes/B15_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `surface.map.json`
- `risk_findings.json`
- `evidence_gap.json`
- `surface.metrics.json`
- `surface.report.md`
- `surface.sarif.json`

### Code Artifacts

- Workflow detection.
- Script detection.
- Finding generation.
- JSON/Markdown/SARIF outputs.
- No external command execution.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B14 - Release Hygiene Audit

### Required Tools / Libraries

- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Static discovery

Chosen:
- Use static scan.

Rejected:
- Run discovered scripts.

Reason:
- Discovery must be safe and local.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m py_compile aapp/surface_scan.py
- python3 -m pytest tests/test_surface_scan.py -q

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Fixture workflow -> detected.
- Risky script -> finding.
- No external execution.

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
| False coverage perception | Medium | Call it surface map. |
| Execution side effect | High | Never execute discovered scripts. |

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

- Action surfaces are mapped.

Qualitative outcome:

- Reviewer sees where agent actions may occur.

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
- B16 - Agent Posture Scan

The next phase depends on:
- surface.map.json
- risk_findings.json

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
- Workflow detection.
- Script detection.
- Finding generation.
- JSON/Markdown/SARIF outputs.
- No external command execution.

Deferred, not removed:
- Posture scan.
- Scoped active scan.

Final validation:
- python3 -m py_compile aapp/surface_scan.py
- python3 -m pytest tests/test_surface_scan.py -q

Final status:
- backfilled from merged historical phase
