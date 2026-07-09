# Crypto Migration Receipt Bundle

B38 is a local deterministic reference component that converts B34 inventory, B35 crypto policy decision, B36 migration plan, and B37 dry-run verdict references into a tamper-evident receipt bundle.

## Guarantees

- Deterministic canonical JSON digest.
- Explicit source references for inventory, policy decision, migration plan, and dry-run verdict.
- Upstream evidence digest preservation.
- Rejection of missing source references.
- Rejection of mismatched subject, resource, or plan references.
- Rejection of blocked or unsupported dry-run verdicts.

## Non-goals

B38 does not execute crypto migration, rotate keys, call network services, call subprocesses, sign with real private keys, claim production migration safety, or claim compliance certification.

## Output

The bundle returns:

- `receipt_status`
- `source_refs`
- `upstream_evidence_digests`
- `bundle_digest`
- `reason_codes`
- `required_follow_up_actions`
- explicit `execution_allowed: false`
