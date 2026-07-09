# B41 Scope

## Goal

Add a deterministic Secret Evidence Export Gate after B40.

B40 controls whether secret evidence is sanitized. B41 controls whether sanitized evidence is safe to export.

## Deliverables

- `aapp/secret_evidence_export_gate.py`
- `docs/SECRET_EVIDENCE_EXPORT_GATE.md`
- `docs/phase-notes/B41_SCOPE.md`
- `tests/fixtures/secret_evidence_export_gate/sample_export_record.json`
- `tests/test_secret_evidence_export_gate.py`

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_secret_evidence_export_gate.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## Issue

Refs #107
