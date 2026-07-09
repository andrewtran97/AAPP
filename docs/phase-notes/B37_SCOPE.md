# B37 Crypto Migration Dry-Run Gate

## Scope

B37 converts B36 crypto migration plans into deterministic dry-run/readiness verdicts.

## Required behavior

- Read a migration plan shape derived from B36 output.
- Validate required plan fields.
- Reject unsupported migration steps.
- Reject destructive, production, and live key-rotation execution.
- Produce deterministic readiness verdicts.
- Preserve evidence digest references.
- Return reason codes and required follow-up actions.

## Out of scope

B37 must not:

- execute crypto migration
- rotate keys
- call subprocesses
- call network
- modify files outside returned data
- claim production migration safety
- claim compliance certification
- introduce external dependencies

## Expected files

- `aapp/crypto_migration_dry_run.py`
- `docs/CRYPTO_MIGRATION_DRY_RUN.md`
- `docs/phase-notes/B37_SCOPE.md`
- `tests/fixtures/crypto_migration_dry_run/sample_migration_plan.json`
- `tests/test_crypto_migration_dry_run.py`
