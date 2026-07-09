# B41 Secret Evidence Export Gate

B41 prevents evidence export paths from leaking raw secrets.

## Contract

Input record must include:

- `purpose`
- `original_digest`
- `boundary_verdict`
- `raw_secret_stored`
- `export_record`

Allowed purposes:

- `audit`
- `siem`
- `compliance`
- `incident_response`
- `security_review`

Blocked purposes:

- `train`
- `training`
- `model_training`
- `fine_tune`
- `fine-tune`
- `finetune`

## Verdicts

- `ALLOWED`: sanitized metadata can be exported.
- `BLOCKED`: export must not proceed.

## Non-goals

- No network transport.
- No SIEM client.
- No production storage.
- No model training pipeline.
