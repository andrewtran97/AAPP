# B39 Crypto Migration Apply Gate

B39 converts a B38 crypto migration receipt bundle into a deterministic apply-readiness verdict.

## Contract

Allowed path:

- request action is `apply_migration`
- environment is `production`
- B38 receipt bundle exists
- receipt digest is `sha256:*`
- migration plan reference exists
- dry-run verdict passed
- policy verdict allowed
- receipt is tamper-evident

## Non-goals

B39 does not execute migration, call subprocesses, write files, access network, rename prior files, or bypass B34-B38.

## Verdicts

- `APPLY_READY`: future production apply path may proceed to human confirmation.
- `BLOCKED`: one or more gate rules failed.
- `MALFORMED`: payload is not an object.

## Safety rule

`execution_performed` must always be `false`.
