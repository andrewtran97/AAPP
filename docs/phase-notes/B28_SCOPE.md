# B28 Policy Abstraction + Deterministic Risk Signals

## 1. Phase Name & ID

B28 — Policy Abstraction + Deterministic Risk Signals.

## 2. Objective / Goal

Add deterministic policy abstraction and deterministic risk signal generation for tool-call style records.

B28 converts raw tool-call inputs into structured policy abstraction fields and derives deterministic risk signals from explicit rules.

## 3. Problem Statement

Current policy-related records are too close to raw tool calls.

B28 adds a deterministic abstraction layer so later phases can reason over:

- subject
- action
- resource
- context
- risk_class
- obligations
- reason_codes

B28 also adds deterministic risk signals without ML, SIEM, SOAR, IDS, dashboard, network calls, or external command execution.

## 4. Scope

### In Scope

- Policy abstraction module.
- Deterministic risk signals module.
- Unit tests for policy abstraction.
- Unit tests for deterministic risk signals.
- JSON fixtures for policy abstraction.
- JSON fixtures for deterministic risk signals.
- B28 scope manifest.
- Deterministic rule evaluation only.

### Out of Scope / Non-Goals

- No ML.
- No SIEM.
- No SOAR.
- No IDS.
- No dashboard.
- No orchestration engine.
- No network call.
- No external command execution.
- No alerting platform.
- No containment automation.
- No runtime side effects beyond scoped test outputs.
- No ledger writes.
- No casefile writes.
- No governance record writes.
- No external exports.
- No B29 code.

### Future Considerations

B29 may address evidence performance after B28 is accepted on main.

B32 may address audit or SIEM export later.

B53 may address policy simulation or dry-run later.

## 5. Metrics

### Completion Metrics / Definition of Done

- `docs/phase-notes/B28_SCOPE.md` exists.
- `aapp/policy_abstraction.py` exists.
- `aapp/deterministic_risk_signals.py` exists.
- `tests/test_policy_abstraction.py` exists.
- `tests/test_deterministic_risk_signals.py` exists.
- Policy abstraction fixtures exist.
- Deterministic risk signal fixtures exist.
- Existing tests pass.
- New B28 tests pass.

### Quality & Safety Metrics

- No ML dependency.
- No probabilistic behavior.
- No network call.
- No external command execution.
- No runtime side effects outside tests.
- No unsupported public claim.
- No __pycache__ remains.

### Adoption / Usability Metrics

- A reviewer can inspect fixtures and understand expected deterministic outputs.
- Reason codes are explicit.
- Risk signals are explainable from rules.
- Inputs and outputs are JSON-compatible.

### Performance / Scale Metrics

- B28 adds no performance claim.
- B28 adds no concurrency requirement.
- B28 adds no external service dependency.

## 6. Deliverables

### Required Files

- `docs/phase-notes/B28_SCOPE.md`
- `aapp/policy_abstraction.py`
- `aapp/deterministic_risk_signals.py`
- `tests/test_policy_abstraction.py`
- `tests/test_deterministic_risk_signals.py`
- `tests/fixtures/policy_abstraction/allow_read.json`
- `tests/fixtures/policy_abstraction/destructive_write.json`
- `tests/fixtures/policy_abstraction/unknown_action.json`
- `tests/fixtures/deterministic_risk_signals/repeated_deny.json`
- `tests/fixtures/deterministic_risk_signals/risk_escalation.json`
- `tests/fixtures/deterministic_risk_signals/data_egress_risk.json`

### Code Artifacts

- Policy abstraction function.
- Deterministic risk signal function.
- Simple constants for risk classes, obligations, and reason codes if needed.

### Documentation

- B28 phase manifest.

### Machine-Readable Outputs

- `policy.abstract.verdict.json` shape in tests.
- `threat.signals.json` shape in tests.
- `policy.abstraction.report.md` may be deferred unless required by tests.

## 7. Dependencies & Prerequisites

- B27D accepted on main.
- PR #79 merged.
- Issue #78 closed.
- Issue #70 open.
- Branch is `b28-policy-abstraction-deterministic-risk-signals`.

## 8. Key Design Decisions

- Use deterministic pure functions.
- Keep inputs and outputs JSON-compatible.
- Do not call network.
- Do not execute external commands.
- Do not write ledgers, casefiles, governance records, or exports.
- Keep B28 small and test-driven.
- Implement only rules required by fixtures and tests.

## 9. Validation Strategy

### Automated Validation

Run B28 tests and full existing test suite.

### Manual Validation

Review changed file list and confirm scope stays within B28.

### Scenario Validation

Validate:

- unknown action
- unknown resource
- destructive action obligations
- repeated deny signal
- risk escalation signal
- restricted data to external sink signal
- policy degraded high-risk signal if implemented

### Review Process

One PR for B28 only.

## 10. Risks & Mitigations

- Risk: B28 becomes threat detection. Mitigation: deterministic risk signals only.
- Risk: scope expands into SIEM/SOAR. Mitigation: no export, no alerting, no orchestration.
- Risk: side effects enter detection path. Mitigation: pure functions and tests.
- Risk: fixtures overcomplicate implementation. Mitigation: minimum fixtures tied to explicit rules.
- Risk: runtime behavior changes. Mitigation: no integration into runtime path unless tests require it.

## 11. Kill Conditions

- ML dependency appears.
- Network call appears.
- External command execution appears.
- SIEM, SOAR, IDS, dashboard, or orchestration behavior appears.
- Detection path writes ledgers, casefiles, governance records, or external exports.
- Existing tests regress.
- New B28 tests fail.
- __pycache__ remains.
- Files outside B28 manifest are changed without explicit reason.

## 12. Success Criteria

B28 succeeds when:

- B28 manifest exists.
- Policy abstraction tests pass.
- Deterministic risk signal tests pass.
- Existing test suite passes.
- CI passes.
- PR merges.
- Post-merge validation passes on main.
- Issue #70 closes only after post-merge validation.

## 13. Transition to Next Phase

Do not start B29 until B28 is merged and post-merge validation passes.

## 14. Timeline & Owner

Owner: repository operator.

Timeline: one scoped PR.

Implementation rule: one branch equals one product gate; one PR equals one failure mode.

## 15. Final Phase Record

Status: active implementation target.

Final acceptance requires merge to main and post-merge validation PASS.
