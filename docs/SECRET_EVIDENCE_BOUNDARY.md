# Secret Evidence Boundary

B40 defines a deterministic boundary for evidence records that may contain
secret-like fields.

## Contract

The boundary must prove how secret-like data was handled without exporting,
logging, training on, or inlining the raw value.

## Verdicts

- `ALLOWED`: no secret-like field was detected.
- `REDACTED`: secret-like fields were detected and safely replaced.
- `BLOCKED`: raw secret storage was declared, or secret-like data was requested for training.
- `MALFORMED`: input is not an evidence object.

## Evidence shape

Each boundary result includes:

- `schema_version`
- `purpose`
- `verdict`
- `reason_codes`
- `original_digest`
- `sanitized_digest`
- `redaction_count`
- `secret_paths`
- `sanitized_record`
- `boundary`

## Non-goals

B40 does not implement a secret manager, KMS, HSM, provider adapter, production
storage backend, or B41 workload identity behavior.
