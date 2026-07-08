# B27C Developer Distribution Gate

## 1. Phase Name & ID

B27C — Developer Distribution Gate.

## 2. Objective / Goal

Make the repo understandable and runnable by a new developer without changing runtime behavior.

## 3. Problem Statement

A new developer needs local setup instructions, example entry points, and claim boundaries without private conversation context.

## 4. Scope

### In Scope

- Developer quickstart.
- Claim boundary documentation.
- Local agent example.
- GitHub Action style example.
- MCP tool call style example.
- README developer quickstart section.

### Out of Scope / Non-Goals

- No B28 code.
- No runtime behavior change.
- No scanner behavior change.
- No policy engine behavior change.
- No orchestration engine.
- No learning pipeline.
- No dashboard.
- No paid external service dependency.
- Do not touch aapp/*.
- Do not touch tests/test_*.
- Do not touch tests/fixtures/*.
- Do not create aapp/policy_abstraction.py.
- Do not create aapp/deterministic_risk_signals.py.

### Future Considerations

B27D and B28 are future gates. They are not implemented in B27C.

## 5. Metrics

### Completion Metrics / Definition of Done

- Required B27C files exist.
- quickstart.sh runs locally.
- Three examples run locally.
- README contains developer quickstart.
- Existing tests pass.
- No runtime files changed.

### Quality & Safety Metrics

- No secrets required.
- No paid service required.
- No overbroad security language.
- No .aapp evidence committed.
- No __pycache__ remains.

### Adoption / Usability Metrics

- New developer can run one local quickstart.
- Examples are visible and documented.
- Claim boundaries are visible.

### Performance / Scale Metrics

- No runtime performance claim.
- No network dependency.
- Quickstart target: under 90 seconds.

## 6. Deliverables

### Required Files

- docs/phase-notes/B27C_SCOPE.md
- docs/CLAIM_BOUNDARIES.md
- quickstart.sh
- examples/local-agent/README.md
- examples/local-agent/run.sh
- examples/github-action/README.md
- examples/github-action/run.sh
- examples/mcp-tool-call/README.md
- examples/mcp-tool-call/run.sh
- README.md

### Code Artifacts

No runtime code artifacts.

### Documentation

Phase note, claim boundary doc, example READMEs, and README quickstart section.

### Machine-Readable Outputs

Example scripts may create temporary local JSON demo files only.

## 7. Dependencies & Prerequisites

- B27B accepted on main.
- Branch is b27c-developer-distribution-gate.
- Issue #75 is open.
- Bash and Python 3 are available.

## 8. Key Design Decisions

- Documentation and local examples only.
- No runtime modification.
- No B28 implementation.
- No external service dependency.

## 9. Validation Strategy

### Automated Validation

Run quickstart, repo validators, and existing unit tests.

### Manual Validation

Review changed file list and public wording.

### Scenario Validation

Run each example locally.

### Review Process

Open one PR for B27C only.

## 10. Risks & Mitigations

- Risk: scope creep into B28. Mitigation: forbidden file guard.
- Risk: unsupported claim language. Mitigation: claim boundary doc.
- Risk: runtime drift. Mitigation: diff guard.
- Risk: stale bytecode. Mitigation: cleanup command.

## 11. Kill Conditions

- Runtime behavior changes.
- Scanner behavior changes.
- Policy engine behavior changes.
- B28 files appear.
- Secrets are required.
- Paid services are required.
- Overbroad security language appears.
- Tests regress.
- __pycache__ remains.

## 12. Success Criteria

B27C succeeds when local validation, CI, merge, and post-merge validation all pass.

## 13. Transition to Next Phase

Do not start B28 until B27C is merged and post-merge validation passes.

## 14. Timeline & Owner

Owner: repository operator. One branch, one PR, one product gate.

## 15. Final Phase Record

Status: active implementation target. Acceptance requires merge to main and post-merge validation PASS.
