# B20 - GitHub Action Scan + Artifact Upload

## 1. Phase Name & ID

**Phase ID:** B20
**Phase Name:** GitHub Action Scan + Artifact Upload
**Phase Type:** workflow adapter
**Status:** backfilled from merged historical phase
**Primary PR:** #54
**Primary Issue:** #53

---

## 2. Objective / Goal

Expose scan and verification entry points to GitHub Actions.

Business goal:
- Let CI users run AAPP scans and collect outputs as artifacts.

Technical goal:
- Create composite scan action with surface scan, posture scan, optional verify pack, and output contract.

---

## 3. Problem Statement

This phase exists because:
- Local scan does not fit CI.
- Outputs need stable artifact directories.

Without this phase:
- CI users cannot run AAPP scan path easily.
- Artifacts are not consistently named.

---

## 4. Scope

### In Scope

- Composite scan action metadata.
- Surface scan command.
- Posture scan command.
- Optional verify pack command.
- Fail-on-high input.
- Artifact-ready output directory.

### Out of Scope / Non-Goals

- No active network scan by default.
- No exploit testing.
- No SIEM export.
- No cloud backend.

### Future Considerations

- Scoped active scan.
- Audit export after B27.

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
- `tests/test_agent_black_box_scan_action.py`

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B20_SCOPE.md`

Scripts / Workflows:
- `.github/actions/agent-black-box-scan/action.yml`

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `surface scan outputs`
- `posture scan outputs`
- `optional verify pack outputs`
- `action summary JSON`

### Code Artifacts

- Composite scan action metadata.
- Surface scan command.
- Posture scan command.
- Optional verify pack command.
- Fail-on-high input.
- Artifact-ready output directory.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B15 - Surface Scan
- B16 - Posture Scan
- B19 - Verify Pack

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

### Decision 1: Artifact-ready outputs

Chosen:
- Write stable output directories.

Rejected:
- Print-only output.

Reason:
- Reviewers need downloadable artifacts.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m py_compile tests/test_agent_black_box_scan_action.py
- python3 -m pytest tests/test_agent_black_box_scan_action.py tests/test_verify_pack.py tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Action fixture -> surface/posture outputs.
- Fail-on-high input -> expected behavior.

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
| Action does too much | Medium | Keep active scan separate. |
| Artifact drift | Medium | Test output contract. |

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

- AAPP scan path is usable from GitHub Actions.

Qualitative outcome:

- CI reviewer can download scan artifacts.

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
- B21 - Scoped Network Active Scan

The next phase depends on:
- Action output contract

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
- Composite scan action metadata.
- Surface scan command.
- Posture scan command.
- Optional verify pack command.
- Fail-on-high input.
- Artifact-ready output directory.

Deferred, not removed:
- Scoped active scan.
- Audit export after B27.

Final validation:
- python3 -m py_compile tests/test_agent_black_box_scan_action.py
- python3 -m pytest tests/test_agent_black_box_scan_action.py tests/test_verify_pack.py tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

Final status:
- backfilled from merged historical phase
