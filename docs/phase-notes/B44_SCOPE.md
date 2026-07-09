# B44 Crypto-Agility / PQ Readiness Planner

## Purpose

B44 adds a local deterministic Crypto-Agility / PQ Readiness Planner.

The planner evaluates crypto inventory and migration context to produce a deterministic readiness plan for post-quantum transition planning.

B44 uses NIST PQC standards as external design anchors only. It does not implement post-quantum cryptography and does not claim post-quantum security.

## Scope

B44 is limited to a local deterministic reference implementation.

Expected files:

- `aapp/pq_readiness_planner.py`
- `docs/PQ_READINESS_PLANNER.md`
- `docs/phase-notes/B44_SCOPE.md`
- `tests/fixtures/pq_readiness_planner/sample_crypto_context.json`
- `tests/test_pq_readiness_planner.py`

## Non-goals

B44 does not implement:

- post-quantum cryptographic algorithms
- FIPS validation
- FedRAMP readiness
- CISA approval
- production crypto migration
- production key rotation
- network calls
- subprocess calls
- external services
- scanner behavior changes
- crypto policy decision behavior changes
- migration apply behavior changes
- runtime execution behavior changes
- B45 implementation

## Control Laws

- No crypto inventory -> no readiness plan.
- No algorithm classification -> mark as incomplete.
- Classical asymmetric crypto with long-lived confidentiality -> PQ migration planning required.
- Unknown algorithm -> unsupported.
- No migration path -> migration gap.
- No owner -> readiness plan incomplete.
- No evidence digest -> malformed.
- Readiness planner must preserve evidence digest.
- Planner output is advisory evidence, not a post-quantum security claim.

## Verdicts

- READY
- NEEDS_INVENTORY
- INCOMPLETE
- PQ_MIGRATION_REQUIRED
- MIGRATION_GAP
- UNSUPPORTED_ALGORITHM
- MALFORMED

## Acceptance Criteria

- Expected B44 file manifest exists.
- Focused B44 unit tests pass.
- Full test suite passes.
- No network or subprocess dependency is introduced.
- Exact dirty and staged file guards pass.
