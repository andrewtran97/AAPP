# Audit / SIEM Export

## Purpose

Audit / SIEM Export provides a local deterministic reference for converting AAPP evidence-shaped records into audit export records.

## Supported Local Output Shapes

B32 supports two local output shapes:

- ECS-shaped JSON record
- CEF-shaped text record

## Input Contract

Required input fields:

- schema_version
- record_id
- event_kind
- occurred_at
- actor
- action
- resource
- policy_verdict
- governance_verdict
- evidence_digest

Optional input fields:

- summary
- reason_codes

## Verdicts

The export function returns:

- EXPORTED
- REDACTED
- UNSUPPORTED
- MALFORMED

## Redaction Boundary

Secret-like summary values are not exported.

When a secret-like marker is detected in summary content:

- the exported summary becomes [REDACTED]
- SECRET_LIKE_VALUE_REDACTED is added to reason_codes
- the original evidence_digest is preserved

## Unsupported Format Boundary

Unsupported output formats return a deterministic UNSUPPORTED verdict.

## Non-Goals

This reference does not:

- send records to live SIEM systems
- open network sockets
- call subprocesses
- implement syslog transport
- implement vendor authentication
- export raw secret-like values
- change scanner behavior
- change policy engine behavior
- change runtime execution behavior

## Claim Boundary

This is a local deterministic reference only.
