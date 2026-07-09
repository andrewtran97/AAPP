# B40 Secret Evidence Boundary

## Scope

B40 defines and tests a Secret Evidence Boundary so evidence records can prove
secret handling decisions without exporting, logging, training on, or inlining
raw secret-like values.

## Deliverables

- `docs/phase-notes/B40_SCOPE.md`
- `docs/SECRET_EVIDENCE_BOUNDARY.md`
- `aapp/secret_evidence_boundary.py`
- `tests/fixtures/secret_evidence_boundary/sample_evidence_record.json`
- `tests/test_secret_evidence_boundary.py`

## Control law

No raw secret-like value may cross the evidence boundary.

## In scope

- Deterministic secret-like key detection.
- Deterministic secret-like value detection for common token/private-key shapes.
- Redacted evidence output.
- Original and sanitized digests.
- Verdicts: `ALLOWED`, `REDACTED`, `BLOCKED`, `MALFORMED`.
- Tests for redaction, digest preservation, training block, raw secret storage block, allowed clean records, and malformed input.

## Out of scope

- External secret manager integration.
- KMS/HSM/provider adapter.
- Production storage backend.
- B41 workload identity provider adapter.
- Scanner, policy, or orchestration refactor.
- Raw secret-like values in evidence output.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_secret_evidence_boundary.py' -v`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
