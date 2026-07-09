# B42 Secret Evidence Training Gate

B42 adds a deterministic training gate for evidence records.

## Rule

Evidence records must not be used for training, model training, fine-tuning, or dataset construction when any of the following are true:

- `raw_secret_stored=true`
- secret-like payload values are present
- training is explicitly disallowed

## Allowed path

Sanitized metadata-only evidence may be allowed when no raw secret-like payload values are present.

## Verdicts

- `ALLOWED`
- `BLOCKED`
- `MALFORMED`

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_secret_evidence_training_gate -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
cat > docs/phase-notes/B42_SCOPE.md <<'MD'

B42 Scope

B42 adds the Secret Evidence Training Gate.

Objective

Prevent evidence records from entering training, fine-tuning, model-training, or dataset construction flows when the record contains raw secret flags or secret-like payload values.

In scope
Deterministic Python reference implementation
Secret-like value detection
Sanitized output envelope
Unit tests
Docs
Out of scope
Real model training
Network calls
External secret scanners
Background services
OPA/NATS/gRPC production implementation
