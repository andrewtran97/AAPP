# Crypto Policy Decision

## Purpose

Crypto Policy Decision converts local crypto inventory findings into deterministic policy decisions.

B35 receives inventory-shaped records from B34-style output and assigns policy verdicts with reason codes.

## Input Contract

Supported input:

- object with a findings list
- each finding may contain algorithm, category, reason_code, and risk_class

Unsupported input:

- non-object input

Malformed input:

- missing findings field
- findings field is not a list
- finding item is not an object
- finding item missing algorithm

## Verdict Priority

When multiple findings exist, the aggregate verdict uses the strictest verdict:

1. DISALLOWED
2. MIGRATION_REQUIRED
3. DEPRECATED
4. REVIEW_REQUIRED
5. APPROVED

## Policy Mapping

Examples:

- SHA-256: APPROVED
- AES: APPROVED
- RSA: REVIEW_REQUIRED
- ECDSA: REVIEW_REQUIRED
- Ed25519: REVIEW_REQUIRED
- ECDH: REVIEW_REQUIRED
- MD5: DEPRECATED
- SHA-1: DEPRECATED
- DES: MIGRATION_REQUIRED
- 3DES: MIGRATION_REQUIRED
- RC4: MIGRATION_REQUIRED
- PRIVATE_KEY_MARKER: DISALLOWED

## Boundary

This reference does not:

- scan files directly
- call external tools
- open network sockets
- call subprocesses
- create a migration plan
- make readiness or certification claims

## Claim Boundary

This is a local deterministic reference only.
