# B30 External Witness Receipt

## 1. Phase Name & ID

B30 - External Witness Receipt.

## 2. Objective / Goal

Add a scoped external witness receipt boundary and local deterministic reference path without changing existing runtime trust semantics.

B30 defines how an evidence receipt can later be witnessed by an external authority or independent witness while preserving deterministic local validation.

## 3. Problem Statement

After B29A, the repository has architecture and tech stack documentation boundaries.

What is still missing is a scoped B30 boundary for external witness receipts that explains:

- what a witness receipt is
- what remains local-only in this phase
- what must not be claimed as externally witnessed
- what evidence fields must remain stable
- where deterministic authority remains

Without this boundary, future work can drift into unsupported external service claims, live network dependency, production signing authority, or compliance overclaim.

## 4. Scope

### In Scope

- B30 phase manifest.
- External witness receipt boundary documentation.
- Local deterministic witness receipt fixture.
- Local witness receipt generation module.
- Unit test for witness receipt output shape.
- No network dependency.
- No external service dependency.
- No production witness authority claim.

### Out of Scope / Non-Goals

- No live external witness service.
- No blockchain.
- No transparency log integration.
- No Sigstore/Rekor integration.
- No TUF integration.
- No production signing authority.
- No customer deployment.
- No compliance certification.
- No policy engine behavior change.
- No scanner behavior change.
- No runtime execution behavior change.
- No B31 tool data flow governance implementation.

## 5. Required Files

Expected B30 files:

- docs/phase-notes/B30_SCOPE.md
- docs/EXTERNAL_WITNESS_RECEIPT.md
- tests/fixtures/external_witness_receipt/sample_receipt_input.json
- tests/test_external_witness_receipt.py
- aapp/external_witness_receipt.py

If implementation scope changes, this manifest must be updated before adding code.

## 6. Receipt Boundary

A witness receipt is a local evidence-linked record that may later be submitted to an external witness system.

B30 may define fields such as:

- receipt_id
- evidence_digest
- witness_subject
- witness_method
- witness_status
- issued_at
- verifier_version
- reason_codes

B30 must not claim that a third party has witnessed the receipt unless a real external witness artifact exists.

## 7. Local-Only Rule

B30 local reference implementation must be deterministic.

Allowed:

- local fixture input
- local canonical JSON
- local digest calculation
- local receipt object
- local unit test

Not allowed:

- network call
- external API call
- blockchain transaction
- production signing
- external timestamp authority
- external witness service dependency

## 8. Authority Boundary

The witness receipt does not replace existing authority.

Authority remains:

- deterministic local validation
- CI
- policy gate
- human or configured merge authority
- post-merge validation

A witness receipt is evidence support, not final approval authority.

## 9. Claim Boundary

Allowed wording:

- local witness receipt reference
- external witness receipt boundary
- candidate future external witness integration
- deterministic local witness receipt
- evidence-linked receipt

Forbidden wording:

- external certification claim
- external validation claim
- legal-proof claim
- immutability claim
- tamper-impossibility claim
- production witness-service claim
- compliance-approved witness receipt

## 10. Validation Plan

Minimum validation:

- Required files exist.
- JSON fixtures parse.
- Witness receipt output shape is deterministic.
- Evidence digest is preserved.
- No network calls.
- No external service dependency.
- Full unittest suite passes.
- Dirty file guard permits only scoped B30 files.

## 11. Acceptance Criteria

B30 is accepted only if:

- B30 scope is documented.
- External witness receipt boundary is documented.
- Local deterministic witness receipt path exists.
- Unit tests cover output shape.
- Full test suite passes.
- No unsupported external witness claim exists.
- No network or external service dependency is added.
- PR CI passes.
- Post-merge validation passes on main.

## 12. Kill Conditions

Stop if:

- B30 performs a live external witness call.
- B30 adds blockchain or transparency log integration.
- B30 claims external certification or validation.
- B30 changes runtime execution behavior.
- B30 changes policy engine behavior.
- B30 changes scanner behavior.
- B30 introduces network dependency.
- B30 introduces production signing authority.
- B30 touches unrelated files.
- Tests fail.
- CI fails.

## 13. Security Boundary

B30 must not store raw secrets in witness receipts.

Witness receipt records should use digest references and reason codes rather than raw sensitive values.

## 14. Future Phases

Future phases may add:

- external transparency log adapter
- signing provider interface
- supply-chain provenance
- release signing
- witness service integration

Those are not part of B30 unless separately scoped.

## 15. Final Phase Record

B30 is complete only after PR merge, main sync, full post-merge validation, and issue closure.
