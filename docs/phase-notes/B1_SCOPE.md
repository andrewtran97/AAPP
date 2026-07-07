# B1 - Hook Gateway

## 1. Phase Name & ID

**Phase ID:** B1
**Phase Name:** Hook Gateway
**Phase Type:** implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #29
**Primary Issue:** Historical

---

## 2. Objective / Goal

Introduce the first local agent-action control boundary.

Business goal:
- Give reviewers a concrete first proof point for allowed and denied agent actions.

Technical goal:
- Record local hook events, apply policy-before-execution, and verify trace integrity.

---

## 3. Problem Statement

This phase exists because:
- Agent tool use needs a first control boundary.
- Denied actions must be recorded without executing.
- Tampering with local traces must be detectable.

Without this phase:
- There is no first evidence point.
- Dangerous actions may be blocked informally without a record.

---

## 4. Scope

### In Scope

- Local hook gateway.
- Tool boundary event recording.
- Policy-before-execution deny path.
- Dev HMAC-SHA384 trace verification.
- Tamper and redaction tests.

### Out of Scope / Non-Goals

- No end-to-end containment claim.
- No cloud policy backend.
- No SIEM.
- No external target testing.

### Future Considerations

- MCP-style recorder.
- Git/CI evidence adapter.
- Unified session bundle.

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
- `aapp/agent_blackbox_hook.py`

Test files:
- `tests/test_agent_blackbox_hook.py`

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B1_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `session.trace.jsonl`

### Code Artifacts

- Local hook gateway.
- Tool boundary event recording.
- Policy-before-execution deny path.
- Dev HMAC-SHA384 trace verification.
- Tamper and redaction tests.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B0 product boundary

### Required Tools / Libraries

- Python 3.10+
- Git

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Policy before execution

Chosen:
- Evaluate before running the action.

Rejected:
- Execute first and explain later.

Reason:
- Denied actions must not create side effects.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m unittest tests.test_agent_blackbox_hook -v
- python3 -m unittest discover -s tests -v

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Denied destructive command -> denied and recorded.
- Modified trace -> verification failure.

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
| Hook bypass | High | Document as reference boundary. |
| Secret leakage | High | Redact secret-like values. |

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

- First local hook boundary exists.
- Denied action has a record.

Qualitative outcome:

- Reviewer understands the first agent-action boundary.

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
- B2 - Local Hook Install / Session Capture

The next phase depends on:
- Hook trace behavior

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
- Local hook gateway.
- Tool boundary event recording.
- Policy-before-execution deny path.
- Dev HMAC-SHA384 trace verification.
- Tamper and redaction tests.

Deferred, not removed:
- MCP-style recorder.
- Git/CI evidence adapter.
- Unified session bundle.

Final validation:
- python3 -m unittest tests.test_agent_blackbox_hook -v
- python3 -m unittest discover -s tests -v

Final status:
- backfilled from merged historical phase
