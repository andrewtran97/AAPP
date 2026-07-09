# B35 Crypto Policy Decision

## Purpose

B35 adds a local deterministic Crypto Policy Decision reference path.

It converts B34-style crypto inventory findings into deterministic policy decisions that later phases can use for migration planning.

## File Manifest

- docs/phase-notes/B35_SCOPE.md
- docs/CRYPTO_POLICY_DECISION.md
- tests/fixtures/crypto_policy_decision/sample_inventory.json
- aapp/crypto_policy_decision.py
- tests/test_crypto_policy_decision.py

## Scope

B35 implements:

- local deterministic crypto policy decisions
- B34-style inventory input handling
- approved algorithm decisions
- review-required algorithm decisions
- deprecated algorithm decisions
- migration-required algorithm decisions
- disallowed marker decisions
- deterministic malformed-input handling
- deterministic unsupported-input handling

## Decision Verdicts

B35 may return:

- APPROVED
- REVIEW_REQUIRED
- DEPRECATED
- DISALLOWED
- MIGRATION_REQUIRED
- MALFORMED
- UNSUPPORTED

## Non-Goals

B35 does not:

- create a PQC migration plan
- claim PQC readiness
- run Semgrep
- run OSV-Scanner
- open network sockets
- call subprocesses
- scan source files directly
- change B34 inventory behavior
- change policy engine behavior
- change runtime execution behavior

## Acceptance

B35 is accepted only after:

- focused B35 unit tests pass
- full test suite passes locally
- exact dirty and staged file guards pass
- no network or subprocess dependency exists in the B35 module
- B34-style findings map to deterministic verdicts
- weak or deprecated findings are reason-coded
- unsupported input handling is deterministic
- malformed input handling is deterministic

## Claim Boundary

B35 is a local deterministic reference only.

It is a crypto policy decision reference, not a certification, external assessment, or readiness claim.
