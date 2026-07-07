# B17 - Deterministic MCP Firewall

## 1. Phase Name & ID

**Phase ID:** B17
**Phase Name:** Deterministic MCP Firewall
**Phase Type:** policy / implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #48
**Primary Issue:** #47

---

## 2. Objective / Goal

Enforce deterministic policy for MCP-style tool calls.

Business goal:
- Block unsafe actions before execution and record the decision trail.

Technical goal:
- Route tool calls through ALLOW, DENY, or REQUIRE_APPROVAL with trace and report outputs.

---

## 3. Problem Statement

This phase exists because:
- Tool calls need deterministic enforcement.
- Probabilistic allow/deny is not acceptable for control routing.

Without this phase:
- Tool calls execute without stable policy.
- Denied attempts may not be recorded.

---

## 4. Scope

### In Scope

- ALLOW fake executor path.
- DENY no execution.
- DENY records trace.
- REQUIRE_APPROVAL no execution without approval.
- Invalid/unknown default DENY.
- CLI trace/verdict/report.

### Out of Scope / Non-Goals

- No ML policy decision.
- No external policy backend.
- No real destructive execution.

### Future Considerations

- State ledger and reversal.
- Policy abstraction after B27.

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
- `aapp/deterministic_firewall.py`

Test files:
- `tests/test_deterministic_firewall.py`

Fixture files:
- `tests/fixtures/firewall_policy.json`
- `tests/fixtures/firewall_allowed_tools_call.json`
- `tests/fixtures/firewall_blocked_tools_call.json`

Documentation:
- `docs/phase-notes/B17_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `firewall.trace.jsonl`
- `firewall.verdict.json`
- `firewall.report.md`

### Code Artifacts

- ALLOW fake executor path.
- DENY no execution.
- DENY records trace.
- REQUIRE_APPROVAL no execution without approval.
- Invalid/unknown default DENY.
- CLI trace/verdict/report.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B15 - Surface Scan
- B16 - Posture Scan

### Required Tools / Libraries

- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Deterministic decision

Chosen:
- Rule-based ALLOW/DENY/REQUIRE_APPROVAL.

Rejected:
- Probabilistic decision.

Reason:
- Policy decisions must be reproducible.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m py_compile aapp/deterministic_firewall.py tests/test_deterministic_firewall.py
- python3 -m pytest tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Allowed request -> safe path.
- Blocked request -> no execution.
- Unknown tool -> DENY.

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
| Policy bypass | High | Deny by default. |
| Overbroad policy | Medium | Separate abstraction later. |

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

- Tool calls have a deterministic gate.

Qualitative outcome:

- Reviewer can explain allow/deny outcome.

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
- B18 - State Ledger + Reversal Plan

The next phase depends on:
- firewall.verdict.json

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
- ALLOW fake executor path.
- DENY no execution.
- DENY records trace.
- REQUIRE_APPROVAL no execution without approval.
- Invalid/unknown default DENY.
- CLI trace/verdict/report.

Deferred, not removed:
- State ledger and reversal.
- Policy abstraction after B27.

Final validation:
- python3 -m py_compile aapp/deterministic_firewall.py tests/test_deterministic_firewall.py
- python3 -m pytest tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

Final status:
- backfilled from merged historical phase
