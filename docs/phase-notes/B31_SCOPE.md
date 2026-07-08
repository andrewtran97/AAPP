# B31 Tool Data Flow Governance

## 1. Phase Name & ID

B31 - Tool Data Flow Governance.

## 2. Objective / Goal

Add scoped tool data flow governance for tool-call records without changing runtime execution behavior.

B31 defines a local deterministic reference path for classifying tool-call inputs, outputs, derived fields, and evidence references into governance outcomes.

## 3. Problem Statement

After B30, the repository has deterministic evidence receipts and a local external witness receipt boundary.

What remains missing is a scoped governance layer for tool-call data flow that explains:

- what data may pass through
- what data must be redacted
- what data must be blocked
- what evidence references must be preserved
- what must not be exported without governance verdict
- what must not be used for training without rights

Without this boundary, future phases can drift into raw secret export, unclear training-use rights, tenant-boundary mistakes, or unsupported SIEM/export behavior.

## 4. Scope

### In Scope

- B31 phase manifest.
- Tool data flow governance boundary documentation.
- Local deterministic tool data flow governance module.
- JSON fixture coverage.
- Unit tests.
- Allowed / redacted / blocked data flow outcomes.
- Local-only execution.
- No external service dependency.
- No runtime execution behavior change.

### Out of Scope

- B32 Audit / SIEM Export.
- Network calls.
- Dashboard.
- Production service split.
- Go, Rust, or TypeScript implementation.
- OPA backend adapter.
- Secret storage.
- Training data pipeline.
- Policy engine behavior change.
- Scanner behavior change.

## 5. Required Files

B31 expected files:

- docs/phase-notes/B31_SCOPE.md
- docs/TOOL_DATA_FLOW_GOVERNANCE.md
- aapp/tool_data_flow_governance.py
- tests/fixtures/tool_data_flow_governance/sample_tool_flow.json
- tests/test_tool_data_flow_governance.py

## 6. Governance Outcomes

B31 local reference outcomes:

- ALLOWED
- REDACTED
- BLOCKED
- MALFORMED
- UNSUPPORTED
- EXPORT_NOT_ALLOWED
- TRAINING_NOT_ALLOWED
- TENANT_BOUNDARY_VIOLATION

## 7. Data Flow Fields

B31 must preserve structured fields for:

- record_id
- actor
- tool
- action
- resource
- input_classification
- output_classification
- governance_verdict
- reason_codes
- evidence_digest
- export_allowed
- training_allowed

## 8. Control Laws

B31 must preserve these control laws:

- No governance verdict -> no evidence export.
- No rights -> no training use.
- No tenant boundary -> no enterprise data isolation.
- Raw secrets must not be exported.
- Tool output must not bypass classification.
- Blocked data must not be converted into allowed output.

## 9. Implementation Boundary

B31 is a local deterministic reference.

It must not add:

- live export
- SIEM integration
- network calls
- cloud service calls
- production data pipeline
- runtime execution behavior changes
- policy engine behavior changes
- scanner behavior changes

## 10. Validation Plan

Run:

```bash
python3 -m py_compile aapp/tool_data_flow_governance.py tests/test_tool_data_flow_governance.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_tool_data_flow_governance -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
Also validate:

fixture JSON parses
focused B31 tests pass
full suite passes
no bytecode remains
only scoped B31 files are dirty/staged
no external service dependency is introduced
## 11. Non-Goals

B31 does not implement B32.

B31 does not export evidence to SIEM.

B31 does not add customer data training.

B31 does not add tenant runtime isolation.

B31 does not change existing policy decision behavior.

B31 does not change scanner behavior.

B31 does not change runtime execution behavior.

## 12. Kill Conditions

Stop if B31:

implements B32 Audit / SIEM Export
adds network calls
stores raw secrets
allows export without governance verdict
allows training use without rights
treats tenant boundary as optional
changes policy engine behavior
changes scanner behavior
changes runtime execution behavior
adds production service split
adds Go, Rust, or TypeScript implementation
## 13. Claim Boundary

B31 may claim:

local deterministic governance reference
tool data flow classification
allowed / redacted / blocked outcomes
evidence export gating model
training-use rights gating model

B31 must not claim:

production compliance-approval claim
live SIEM integration
external-auditor approval claim
complete tenant-isolation claim
complete DLP claim
certified privacy-compliance claim
data-leakage impossibility claim
## 14. Review Checklist

Before PR:

B31 issue is open.
B31 branch is active.
Required B31 files exist.
Focused B31 tests pass.
Full test suite passes.
No bytecode remains.
No unsupported claims are present.
No B32 behavior is implemented.
PR references issue #87.
## 15. Final Phase Record

B31 is accepted only after:

PR merged into main
post-merge validation passes on main
issue #87 is closed after validation
