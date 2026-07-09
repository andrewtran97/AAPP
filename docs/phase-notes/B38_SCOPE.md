# B38 Scope

B38 Crypto Migration Receipt Bundle is the receipt layer after B37 dry-run.

## In scope

- Read B37 dry-run/readiness result shape.
- Require B34/B35/B36/B37 source references.
- Preserve upstream evidence digest references.
- Generate deterministic canonical bundle output.
- Generate `bundle_digest`.
- Reject missing source references.
- Reject subject/resource/plan mismatches.
- Reject non-ready or blocked dry-run verdicts.
- Return receipt status, reason codes, source refs, bundle digest, and required follow-up actions.

## Out of scope

- No crypto migration execution.
- No key rotation.
- No network.
- No subprocess.
- No production safety claim.
- No compliance certification claim.
- No external dependencies.
- No scanner behavior changes.
- No policy engine behavior changes.
- No dry-run gate behavior changes.
