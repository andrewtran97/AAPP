# External Witness Receipt

## 1. Purpose

This document defines the B30 external witness receipt boundary.

B30 adds a local deterministic reference for evidence-linked witness receipts. It does not add a live external witness service, blockchain integration, transparency log integration, production signing authority, or compliance certification.

## 2. Definition

An external witness receipt is an evidence-linked record that can be prepared for future witnessing by an independent witness system.

In B30, the receipt remains local-only.

The receipt can describe:

- which evidence digest is being referenced
- which local witness method is being modeled
- which verifier version produced the receipt
- which reason codes explain the receipt state
- whether the receipt is locally prepared, rejected, or unsupported

## 3. Current Phase Boundary

B30 is a local deterministic reference phase.

Implemented in B30:

- local receipt input fixture
- local receipt output shape
- local digest preservation
- local reason codes
- local unit tests

Not implemented in B30:

- live external witness call
- third-party witness confirmation
- external timestamp authority
- blockchain transaction
- transparency log submission
- production signing service
- legal proof system
- compliance approval

## 4. Receipt Fields

A B30 witness receipt should use stable fields:

- receipt_id
- evidence_digest
- witness_subject
- witness_method
- witness_status
- issued_at
- verifier_version
- reason_codes

The receipt should reference evidence by digest rather than storing raw evidence content.

## 5. Witness Status Values

Allowed local status values:

- LOCAL_PREPARED
- LOCAL_REJECTED
- UNSUPPORTED

Meaning:

- LOCAL_PREPARED means the receipt object was generated locally from valid input.
- LOCAL_REJECTED means local validation rejected the input.
- UNSUPPORTED means the requested witness mode is outside B30 scope.

These values do not mean that an external witness has accepted or certified the receipt.

## 6. Deterministic Rules

B30 local generation must be deterministic.

Rules:

- same input produces same receipt_id
- same evidence_digest is preserved
- output keys are stable
- reason codes are deterministic
- no current wall-clock dependency in tests
- no random value dependency in tests
- no network dependency

## 7. Security Boundary

The witness receipt must not store raw secrets.

Allowed:

- digest reference
- resource identifier
- reason code
- verifier version
- local status

Not allowed:

- private key material
- token value
- raw secret-like value
- credential
- full sensitive payload

If sensitive data is required for future production use, it belongs behind a governance/redaction phase, not inside B30.

## 8. Authority Boundary

The witness receipt is evidence support only.

It does not replace:

- deterministic local validation
- policy gate
- CI
- human or configured merge authority
- post-merge validation

A B30 receipt cannot approve deployment, merge code, bypass policy, or certify security.

## 9. Claim Boundary

Allowed wording:

- local witness receipt
- evidence-linked witness receipt
- deterministic local witness receipt
- candidate future external witness integration
- external witness receipt boundary

Forbidden wording:

- external certification claim
- external validation claim
- legal-proof claim
- immutability claim
- tamper-impossibility claim
- production witness-service claim
- compliance-approval claim

## 10. Failure Modes

This design fails when:

- an external witness is claimed without an external artifact
- a local digest is presented as third-party verification
- receipt generation uses current time or randomness in tests
- raw secrets are copied into receipt output
- unsupported witness modes silently pass
- policy or CI authority is bypassed
- B30 is treated as B31 or later governance work

## 11. Non-Goals

B30 does not add:

- network calls
- external APIs
- blockchain
- transparency logs
- Sigstore/Rekor
- TUF
- production signing
- customer deployment
- compliance certification
- policy engine behavior changes
- scanner behavior changes
- runtime execution behavior changes

## 12. Validation

B30 validation should confirm:

- required files exist
- JSON fixture parses
- local receipt output shape is stable
- same input produces same output
- evidence_digest is preserved
- unsupported modes are rejected
- no network dependency exists
- full unittest suite passes

## 13. Future Work

Future phases may add real witness integrations.

Possible future work:

- external transparency log adapter
- signing provider interface
- release signing
- third-party witness submission
- witness verification pack
- governance export rules

Those future capabilities are not part of B30 unless separately scoped.

## 14. Current Implementation Boundary

B30 may implement a local reference module and tests only.

B30 must not claim external witness execution.

## 15. Final Phase Record

B30 is accepted only after PR merge, main sync, post-merge validation, and issue closure.
