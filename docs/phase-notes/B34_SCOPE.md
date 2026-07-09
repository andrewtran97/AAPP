# B34 Crypto Inventory Scanner

## Purpose

B34 adds a local deterministic Crypto Inventory Scanner reference path.

It identifies cryptographic material and algorithm references in local text/source fixtures so later phases can make crypto policy and migration decisions.

## File Manifest

- docs/phase-notes/B34_SCOPE.md
- docs/CRYPTO_INVENTORY_SCANNER.md
- tests/fixtures/crypto_inventory_scanner/sample_source.py
- aapp/crypto_inventory_scanner.py
- tests/test_crypto_inventory_scanner.py

## Scope

B34 implements:

- local deterministic text/source scanning
- hash algorithm reference detection
- signature / public-key algorithm reference detection
- symmetric encryption algorithm reference detection
- key exchange algorithm reference detection
- certificate/private-key marker detection
- weak/deprecated cryptographic indicator detection
- deterministic malformed-input handling
- deterministic unsupported-input handling

## Non-Goals

B34 does not:

- run Semgrep
- run OSV-Scanner
- open network sockets
- call subprocesses
- scan third-party targets
- perform active scanning
- parse binary files
- validate cryptographic strength as a production claim
- create a PQC migration plan
- change scanner behavior outside B34
- change policy engine behavior
- change runtime execution behavior

## Acceptance

B34 is accepted only after:

- focused B34 unit tests pass
- full test suite passes locally
- exact dirty and staged file guards pass
- no network or subprocess dependency exists in the B34 module
- findings are deterministic and reason-coded
- unsupported input handling is deterministic
- malformed input handling is deterministic

## Claim Boundary

B34 is a local deterministic reference only.

It is a crypto inventory reference, not a production cryptographic assessment or PQC readiness claim.
