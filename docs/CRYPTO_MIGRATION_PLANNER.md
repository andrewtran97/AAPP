# Crypto Migration Planner

## Purpose

The Crypto Migration Planner is a local deterministic reference component.

It converts a crypto policy decision record into a migration plan that can be reviewed by a human or later orchestration layer.

## Inputs

The planner expects a JSON-compatible dictionary with:

- schema_version
- record_id
- evidence_digest
- policy_verdict
- findings

Each finding should contain:

- finding_id
- algorithm
- use
- risk_level
- decision
- recommendation

## Outputs

The planner returns a JSON-compatible dictionary with:

- schema_version
- record_id
- evidence_digest
- planner_verdict
- reason_codes
- migration_steps

## Planner Verdicts

- PLAN_REQUIRED
- NO_ACTION
- MALFORMED
- UNSUPPORTED

## Migration Step Actions

- REPLACE_ALGORITHM
- ROTATE_KEY
- REVIEW_USAGE
- DOCUMENT_EXCEPTION

## Boundaries

This component does not:

- execute migration
- mutate production systems
- call network services
- call subprocesses
- claim post-quantum readiness
- claim production cryptographic compliance
- change scanner behavior
- change policy engine behavior
- change runtime execution behavior

## Claim Boundary

Correct wording:

- local deterministic reference
- migration planning reference
- evidence-supporting plan
- no production claim
- no external service dependency

Forbidden wording categories:

- certification claim
- production compliance approval claim
- post-quantum readiness claim
- automatic migration safety claim
