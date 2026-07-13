# AAPP Open-Source Strategy

## Status

`TARGET`

This document defines adoption discipline. It does not add, upgrade, execute, or endorse a dependency in the current repository.

## Doctrine

> Open-Source-First, Adapter-First, Evidence-First, Fork-Last.

Required order:

```text
REUSE -> CONFIGURE -> WRAP -> EXTEND
-> CONTRIBUTE UPSTREAM -> FORK -> REPLACE
```

Skipping a step requires explicit phase authorization and recorded evidence.

## Admission Contract

No dependency is admitted without:

- exact source and version;
- code-license identification;
- model-weight license review when applicable;
- dataset and training-rights review when applicable;
- transitive dependency and license inventory;
- named security owner;
- known-vulnerability review;
- reproducible local baseline;
- workload-relevant benchmark;
- rollback or replacement path.

Unknown or incompatible rights block adoption. A source-code license does not automatically grant model-weight or dataset rights.

## Adapter Boundary

AAPP does not rewrite established scanners, policy engines, telemetry systems, sandbox runtimes, provenance systems, or signing systems merely to own the implementation.

AAPP adapters add the system-specific boundary:

- scope and identity binding;
- capability and policy references;
- data-governance verdicts;
- evidence sequencing and receipts;
- verification and recovery hooks;
- evaluation identity.

An adapter must preserve upstream semantics and expose unsupported behavior instead of silently emulating it.

## Candidate Map

The following are `TARGET` candidates, not current adoption claims:

| Need | Candidate family | AAPP boundary |
| --- | --- | --- |
| Static/code analysis | Semgrep | Authorized inputs and evidence-normalized findings |
| Container/IaC/secrets/SBOM | Trivy | Scope, redaction, and export governance |
| Vulnerability intelligence | OSV | Versioned intake and evidence references |
| Policy | OPA/Rego | Deterministic adapter and default-deny behavior |
| Workload identity | SPIFFE/SPIRE | Identity-bound capability and IPC |
| Telemetry | OpenTelemetry | Governed metadata and digest-first capture |
| Bounded execution | Wasmtime/WASI | Capability imports, limits, and recovery class |
| Supply-chain assurance | SLSA | Provenance inputs and verification references |
| Signing/transparency | Sigstore/Rekor | Signer binding and verifiable log references |
| BOM | CycloneDX/SPDX | Versioned software, crypto, model, and dataset inventory |

Classical ML, portable inference, local model runtimes, and high-throughput serving remain benchmark-gated `RESEARCH` or `TARGET` choices. No model runtime is admitted solely because it is popular.

## Package and Supply-Chain Flow

```text
resolve -> lock -> fetch -> digest verify -> signature verify
-> provenance verify -> dependency/license review
-> quarantine -> evaluate -> promote
```

Promotion requires a pinned artifact identity and a reproducible evaluation record. Signature or provenance establishes origin-related evidence; it does not establish harmless logic.

## Fork Policy

A fork requires:

- documented upstream gap;
- evidence that wrapping or upstream contribution is insufficient;
- patch-ingestion owner;
- upstream security monitoring;
- rebase-cost measurement;
- exit and replacement plan.

Fork maintenance must stop when patch lag or rebase cost exceeds the measured value of divergence.

## Selection Laws

- No license clearance -> no adoption.
- No security owner -> no adoption.
- No reproducible baseline -> no promotion.
- No benchmark -> no replacement.
- No rollback path -> no production promotion.
- No measurable benefit -> retain upstream or current default.
- No rights -> no model or dataset use.

## Evidence Requirements

An admitted dependency record should bind package identity, version, source, digest, license decisions, vulnerability snapshot, evaluation result, owner, approved profile, and replacement path.

This B44A document creates no machine-readable dependency record and performs no dependency mutation.

## Claim Boundary

Open-source availability, a signature, an SBOM, or provenance does not demonstrate that an artifact is correct, vulnerability-free, policy-compliant, or suitable for every environment.

## Non-Goals

- dependency installation or upgrade;
- a package registry service;
- a vulnerability scanner rewrite;
- a policy engine rewrite;
- a signing or transparency service;
- production Wasm execution;
- new network or subprocess behavior.
