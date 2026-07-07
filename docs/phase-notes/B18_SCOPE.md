# B18 - State Ledger + Reversal Plan

## 1. Phase Name & ID

**Phase ID:** B18
**Phase Name:** State Ledger + Reversal Plan
**Phase Type:** ledger / implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #50
**Primary Issue:** #49

---

## 2. Objective / Goal

Record state-changing actions and planned reversals without performing rollback.

Business goal:
- Make state mutation risk reviewable before remediation action.

Technical goal:
- Create ledger entries, digests, hash-chain linkage, reversal candidates, and rollback-gap reports.

---

## 3. Problem Statement

This phase exists because:
- Policy decisions do not show state impact.
- State-changing actions need reversal awareness.

Without this phase:
- State mutations are untracked.
- Reviewer cannot tell whether reversal is possible.

---

## 4. Scope

### In Scope

- Ledger entry creation.
- Pre/post state digests.
- Hash-chain linkage.
- Known reversal candidates.
- Irreversible/manual review classification.
- Missing reversal findings.
- No external action execution.

### Out of Scope / Non-Goals

- No real rollback.
- No production mutation.
- No cloud state restore.
- No automation response system.

### Future Considerations

- Verify pack.
- Incident casefile.

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
- `aapp/state_ledger.py`

Test files:
- `tests/test_state_ledger.py`

Fixture files:
- `tests/fixtures/state_ledger_actions.json`

Documentation:
- `docs/phase-notes/B18_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `state.ledger.jsonl`
- `reversal.plan.json`
- `reversal.report.md`

### Code Artifacts

- Ledger entry creation.
- Pre/post state digests.
- Hash-chain linkage.
- Known reversal candidates.
- Irreversible/manual review classification.
- Missing reversal findings.
- No external action execution.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B17 - Deterministic MCP Firewall

### Required Tools / Libraries

- Python 3.10+

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Plan, not rollback

Chosen:
- Generate reversal plan.

Rejected:
- Execute rollback.

Reason:
- Execution is higher-risk and out of scope.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m py_compile aapp/state_ledger.py tests/test_state_ledger.py
- python3 -m pytest tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Stateful action -> ledger row.
- Known reversal -> candidate.
- No reversal -> gap.

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
| Fake rollback confidence | High | Call it reversal plan. |
| Ledger tamper | Medium | Hash-chain linkage. |

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

- State-changing actions are ledgered.

Qualitative outcome:

- Reviewer sees what would need reversal.

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
- B19 - Verify Pack

The next phase depends on:
- state.ledger.jsonl
- reversal.plan.json

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
- Ledger entry creation.
- Pre/post state digests.
- Hash-chain linkage.
- Known reversal candidates.
- Irreversible/manual review classification.
- Missing reversal findings.
- No external action execution.

Deferred, not removed:
- Verify pack.
- Incident casefile.

Final validation:
- python3 -m py_compile aapp/state_ledger.py tests/test_state_ledger.py
- python3 -m pytest tests/test_state_ledger.py tests/test_deterministic_firewall.py tests/test_posture_scan.py tests/test_surface_scan.py -q

Final status:
- backfilled from merged historical phase
