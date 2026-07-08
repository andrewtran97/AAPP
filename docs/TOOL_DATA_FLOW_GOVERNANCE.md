# Tool Data Flow Governance

## 1. Purpose

This document defines the B31 tool data flow governance boundary.

B31 adds a local deterministic reference model for classifying tool-call data flow.

B31 does not change runtime execution behavior, policy engine behavior, scanner behavior, export behavior, or training behavior.

## 2. Current Phase Boundary

B31 is a local reference phase.

B31 may define data flow fields, governance verdicts, reason codes, local fixture examples, and testable local behavior.

B31 must not implement B32 Audit / SIEM Export, live evidence export, network calls, customer training data pipeline, production tenant isolation, or production service split.

## 3. Tool Data Flow Model

A tool data flow record describes how one tool-call record is classified before any export or training use is allowed.

Canonical flow:

tool input -> input classification -> tool output -> output classification -> governance verdict -> reason codes -> export gate -> training-use gate -> evidence reference

## 4. Required Record Fields

A B31 tool data flow record should preserve these fields:

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

## 5. Governance Verdicts

B31 local reference verdicts:

- ALLOWED
- REDACTED
- BLOCKED
- MALFORMED
- UNSUPPORTED
- EXPORT_NOT_ALLOWED
- TRAINING_NOT_ALLOWED
- TENANT_BOUNDARY_VIOLATION

## 6. Allowed Data Flow

Allowed data flow means the record contains no raw secret, no restricted output, and no tenant-boundary conflict.

Allowed outcome requirements:

- governance_verdict is ALLOWED
- export_allowed is true
- training_allowed is true only when rights are explicit
- evidence_digest is preserved
- reason_codes explain why the flow is allowed

## 7. Redacted Data Flow

Redacted data flow means the record may continue only after sensitive value removal.

Redacted outcome requirements:

- governance_verdict is REDACTED
- raw secret-like values are not emitted
- evidence_digest is preserved
- reason_codes include the redaction reason
- export_allowed depends on the post-redaction classification
- training_allowed remains false unless rights are explicit

## 8. Blocked Data Flow

Blocked data flow means the record must not be exported or used for training.

Blocked outcome requirements:

- governance_verdict is BLOCKED, EXPORT_NOT_ALLOWED, TRAINING_NOT_ALLOWED, or TENANT_BOUNDARY_VIOLATION
- export_allowed is false
- training_allowed is false
- evidence_digest is preserved when present
- reason_codes explain the block

## 9. Evidence Reference Rule

B31 governs references to evidence. It does not rewrite evidence history.

Rules:

- preserve evidence_digest when present
- do not generate a new external receipt
- do not send evidence to an external service
- do not claim external witness status
- do not convert a blocked record into an allowed record

## 10. Export Gate

No governance verdict means no evidence export.

A local B31 record may mark export_allowed only after classification and verdict generation.

B31 does not perform live export.

## 11. Training-Use Gate

No rights means no training use.

A local B31 record may mark training_allowed only when the input declares explicit training rights and the governance verdict permits it.

B31 does not create a training data pipeline.

## 12. Tenant Boundary

No tenant boundary means no enterprise data isolation claim.

B31 may detect tenant-boundary mismatch in local records.

B31 does not implement production tenant isolation.

## 13. Reason Codes

Expected reason code categories:

- INPUT_ALLOWED
- OUTPUT_ALLOWED
- INPUT_REDACTED
- OUTPUT_REDACTED
- RAW_SECRET_BLOCKED
- EXPORT_REQUIRES_GOVERNANCE
- TRAINING_REQUIRES_RIGHTS
- TENANT_BOUNDARY_MISMATCH
- MALFORMED_RECORD
- UNSUPPORTED_DATA_FLOW

## 14. Non-Goals

B31 does not implement B32 Audit / SIEM Export.

B31 does not implement external export service, production DLP service, production tenant isolation, live compliance reporting, policy backend adapter, runtime behavior changes, or scanner behavior changes.

## 15. Failure Modes

This governance layer fails when:

- tool output bypasses classification
- raw secrets are exported
- training_allowed is true without rights
- export_allowed is true without governance verdict
- tenant-boundary mismatch is ignored
- blocked records are rewritten as allowed
- evidence_digest is dropped without reason code

## 16. Current Phase Boundary

B31 records local deterministic governance behavior only.

Implementation of audit export belongs to B32 or later.
