# Crypto-Agility / PQ Readiness Planner

## Purpose

B44 adds a local deterministic Crypto-Agility / PQ Readiness Planner.

The planner evaluates crypto inventory and migration context to produce an advisory readiness plan for post-quantum transition planning.

## Boundary

B44 does not implement post-quantum cryptography.

B44 does not claim:

- post-quantum security
- FIPS validation
- FedRAMP readiness
- CISA approval
- production crypto migration

## Inputs

Required fields:

- `context_id`
- `owner`
- `evidence_digest`
- `crypto_inventory`
- `migration_paths`

Optional fields:

- `long_lived_confidentiality`

## Verdicts

- `READY`
- `NEEDS_INVENTORY`
- `INCOMPLETE`
- `PQ_MIGRATION_REQUIRED`
- `MIGRATION_GAP`
- `UNSUPPORTED_ALGORITHM`
- `MALFORMED`

## Control Laws

- No crypto inventory -> no readiness plan.
- No algorithm classification -> mark as incomplete.
- Classical asymmetric crypto with long-lived confidentiality -> PQ migration planning required.
- Unknown algorithm -> unsupported.
- No migration path -> migration gap.
- No owner -> malformed.
- No evidence digest -> malformed.
- Planner output is advisory evidence, not a post-quantum security claim.
