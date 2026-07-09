# Crypto Inventory Scanner

## Purpose

Crypto Inventory Scanner provides a local deterministic reference for identifying cryptographic indicators in local source/text inputs.

## Input Contract

Supported input:

- string source text

Unsupported input:

- bytes
- bytearray
- non-string objects

## Finding Categories

B34 may identify:

- hash_algorithm
- signature_or_public_key_algorithm
- symmetric_encryption_algorithm
- key_exchange_algorithm
- certificate_or_key_marker
- weak_or_deprecated_crypto

## Scanner Verdicts

The scanner returns:

- INVENTORIED
- UNSUPPORTED
- MALFORMED

## Reason Codes

Example reason codes:

- HASH_ALGORITHM_REFERENCE
- SIGNATURE_OR_PUBLIC_KEY_REFERENCE
- SYMMETRIC_ENCRYPTION_REFERENCE
- KEY_EXCHANGE_REFERENCE
- CERTIFICATE_OR_KEY_MARKER
- WEAK_OR_DEPRECATED_CRYPTO
- INPUT_NOT_STRING
- EMPTY_INPUT

## Boundary

This reference does not:

- run external scanners
- open network sockets
- call subprocesses
- scan third-party targets
- perform active scanning
- parse binary files
- certify cryptographic strength
- create a PQC migration plan

## Claim Boundary

This is a local deterministic reference only.
