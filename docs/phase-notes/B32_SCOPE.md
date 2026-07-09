# B32 Audit / SIEM Export

## Purpose

B32 adds a local deterministic Audit / SIEM Export reference path.

It converts AAPP evidence-shaped records into audit export records that can be inspected locally for downstream SIEM-style ingestion tests.

## File Manifest

- docs/phase-notes/B32_SCOPE.md
- docs/AUDIT_SIEM_EXPORT.md
- tests/fixtures/audit_siem_export/sample_evidence_event.json
- aapp/audit_siem_export.py
- tests/test_audit_siem_export.py

## Scope

B32 implements:

- ECS-shaped JSON export record
- CEF-shaped text export record
- deterministic unsupported-format verdict
- deterministic malformed-input verdict
- evidence digest preservation
- raw secret-like summary redaction

## Non-Goals

B32 does not:

- send records to live SIEM systems
- open network sockets
- call subprocesses
- implement syslog transport
- implement vendor authentication
- change scanner behavior
- change policy engine behavior
- change runtime execution behavior
- export raw secret-like values

## Acceptance

B32 is accepted only after:

- focused B32 unit tests pass
- full test suite passes locally
- exact dirty and staged file guards pass
- evidence digest is preserved
- raw secret-like values are not exported
- unsupported format handling is deterministic

## Claim Boundary

B32 is a local deterministic reference only.
