# B42 Secret Evidence Training Gate

## Purpose

B42 adds a local deterministic Secret Evidence Training Gate.

The gate blocks training, model-training, fine-tuning, and dataset-build flows when a record contains raw secret material, secret-like payload values, or explicit training disallow rules.

## Scope

B42 is limited to a local deterministic reference implementation.

Included files:

- `aapp/secret_evidence_training_gate.py`
- `docs/SECRET_EVIDENCE_TRAINING_GATE.md`
- `docs/phase-notes/B42_SCOPE.md`
- `tests/fixtures/secret_evidence_training_gate/sample_training_record.json`
- `tests/test_secret_evidence_training_gate.py`

## Non-goals

B42 does not implement:

- production DLP
- production tenant isolation
- external training platform integration
- model provider integration
- network calls
- subprocess calls
- scanner behavior changes
- policy engine behavior changes
- runtime execution behavior changes
- B43 implementation

## Control Laws

- No rights → no training use.
- Raw secret present → no training use.
- Secret-like payload value → no training use.
- Training explicitly disallowed → no training use.
- Sanitized metadata-only evidence may be allowed only when raw secret-like payload is absent.
- Evidence digest must be preserved.
- No raw secret payload may be exported into training data.

## Acceptance Criteria

- Expected B42 file manifest exists.
- Focused B42 unit test passes.
- Full test suite passes.
- No network or subprocess dependency is introduced.
- Exact dirty and staged file guards pass.
