# B36 Crypto Migration Planner

## Summary

B36 adds a local deterministic Crypto Migration Planner reference path.

## Scope

B36 converts a crypto policy decision record into a deterministic migration plan.

The planner is local-only. It does not execute migration steps and does not mutate production systems.

## Required Files

- docs/phase-notes/B36_SCOPE.md
- docs/CRYPTO_MIGRATION_PLANNER.md
- tests/fixtures/crypto_migration_planner/sample_policy_decision.json
- aapp/crypto_migration_planner.py
- tests/test_crypto_migration_planner.py

## Implemented

- deterministic migration plan generation
- migration action classification
- evidence digest preservation
- malformed input handling
- unsupported schema handling
- unit test coverage

## Not Implemented

- production crypto migration
- production cryptographic compliance approval
- post-quantum readiness claim
- network calls
- subprocess calls
- scanner behavior changes
- policy engine behavior changes
- runtime execution behavior changes

## Control Laws

- No policy decision record -> no migration plan.
- No evidence digest -> malformed.
- Unsupported schema version -> unsupported.
- Migration plan generation must not execute migration.
- Migration plan generation must not call network services.
- Migration plan generation must not call subprocesses.
- Evidence digest must be preserved.
