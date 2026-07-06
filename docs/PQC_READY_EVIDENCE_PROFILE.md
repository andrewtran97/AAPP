# PQC-Ready Evidence Profile

## Scope

This document defines cryptographic direction for evidence integrity and future post-quantum readiness.

It does not claim that AAPP is post-quantum secure today.

## Classical profile

Confidentiality:
- AES-256
- AES-256-GCM or ChaCha20-Poly1305

Hashing:
- SHA-384
- SHA-512

Signing:
- current implementation may use conventional local test keys for development

## Post-quantum ready profile

Future-compatible algorithms:

- ML-KEM, FIPS 203
- ML-DSA, FIPS 204
- SLH-DSA, FIPS 205

## Rules

Do not invent cryptography.

Do not use marketing claims such as military-grade, unbreakable, or world's strongest encryption.

Do not claim post-quantum secure before implementation, test vectors, interoperability checks, and external review.

Use PQC-ready wording until production implementation exists.
