# Crypto Migration Dry-Run Gate

B37 is a local deterministic reference component that converts B36 crypto migration planner output into a dry-run/readiness verdict.

## Input

Expected input schema:

- `schema_version`
- `record_id`
- `evidence_digest`
- `planner_verdict`
- `reason_codes`
- `migration_steps`

Each migration step must include:

- `finding_id`
- `algorithm`
- `use`
- `risk_level`
- `decision`
- `action`
- `recommendation`

## Verdicts

- `READY`: no migration action is required or the dry-run has no blocking follow-up.
- `REQUIRES_APPROVAL`: supported migration steps exist, but they require review, rehearsal, or human approval.
- `BLOCKED`: the request attempts unsupported, destructive, production, or live execution.
- `MALFORMED`: required fields are missing or malformed.
- `UNSUPPORTED`: the input schema version is unsupported.

## Boundary

B37 does not:

- execute crypto migration
- rotate keys
- call subprocesses
- call network
- mutate production systems
- modify files outside returned data
- claim production migration safety
- claim compliance certification
- introduce external dependencies

## Evidence

B37 preserves `evidence_digest` from the B36 migration plan output.
