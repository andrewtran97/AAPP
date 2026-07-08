# Agent Black Box Tech Stack

## 1. Purpose

This document defines the current reference stack and the future production target stack for Agent Black Box.

B29A is documentation-only.

This document does not add runtime code, services, adapters, scanners, or deployment infrastructure.

## 2. Current Reference Stack

The current repository uses:

- Python
- Bash
- GitHub Actions
- JSON / JSONL
- Markdown
- unittest

This stack is active today.

## 3. Current Repository Role

The current repository is a reference implementation for deterministic gates, evidence artifacts, phase validation, quickstart paths, and reviewer-facing documentation.

It is not a production control plane service split.

## 4. Future Production Target Stack

Future production target stack:

- Go control services
- Rust evidence and scanner core
- Python eval workers
- TypeScript UI, SDK, and VS Code extension
- OPA/Rego-compatible policy model
- gRPC / Protobuf service protocol
- NATS event bus first
- OpenTelemetry observability
- SLSA-style provenance later
- Sigstore / Rekor-style signing and transparency later
- TUF-style release safety later
- CycloneDX / SPDX BOM later
- Semgrep adapter later
- OSV-Scanner adapter later
- SPIFFE/SVID-compatible identity adapter later

These items are future targets unless implemented in a scoped later phase.

## 5. Stack Adoption Boundary

B29A must not implement the future production stack.

The future stack is phase-gated.

A future stack item becomes active only when a later phase adds implementation, tests, validation, and review.

## 6. Language Boundary

Python remains the current reference implementation language.

Bash remains the current local and CI script language.

Go may be used later for long-running control services and service boundaries.

Rust may be used later for evidence-critical, scanner-critical, or digest-critical components.

TypeScript may be used later for UI, SDK, and IDE surfaces.

B29A does not add Go, Rust, or TypeScript implementation.

## 7. Policy Boundary

The current repository has deterministic policy abstraction and deterministic risk signals.

Future production may use an OPA/Rego-compatible model.

B29A does not add an OPA adapter.

Policy output must remain structured and reviewable.

LLM output must not become policy authority.

## 8. Communication Boundary

The current repository does not require service-to-service protocol infrastructure.

Future production may use gRPC and Protobuf for service contracts.

Future production may use NATS as the first event bus.

B29A does not add gRPC, Protobuf, NATS, Kafka, Redis Pub/Sub, or service mesh infrastructure.

## 9. Identity Boundary

The current repository uses reference identity and evidence artifacts.

Future production may use a SPIFFE/SVID-compatible workload identity adapter.

B29A does not add workload identity infrastructure.

No identity claim should be treated as production identity unless a later scoped phase implements and validates it.

## 10. Observability Boundary

The current repository uses local test output and validation scripts.

Future production may use OpenTelemetry for traces, metrics, and logs.

B29A does not add telemetry pipelines, collectors, exporters, dashboards, or alerting.

## 11. Supply Chain Boundary

Future supply-chain work may include:

- provenance
- signing
- transparency log integration
- update safety
- SBOM / CBOM / AI-BOM export
- open source posture checks

B29A does not add supply-chain implementation.

Future supply-chain terms must not be presented as current compliance.

## 12. Scanner Boundary

Future scanner work may include:

- Semgrep adapter
- OSV-Scanner adapter
- scope-gated network or web scanner adapter
- crypto inventory scanner

B29A does not add scanner integration.

Scanner execution must remain scope-gated in later phases.

## 13. Deployment Boundary

The current repository does not require Kubernetes.

Future production may use containers and orchestration only after service split and deployment needs are proven.

B29A does not add Docker, Kubernetes, Helm, service mesh, cloud deployment, or secrets infrastructure.

## 14. Non-Goals

B29A does not add:

- Go implementation
- Rust implementation
- TypeScript implementation
- OPA adapter implementation
- gRPC service
- Protobuf schema implementation
- NATS service
- scanner adapter
- OpenTelemetry pipeline
- supply-chain signing
- BOM export
- Kubernetes deployment
- dashboard
- B30 external witness receipt implementation

## 15. Failure Modes

This tech stack plan fails when:

- future stack is described as active implementation
- stack preference replaces measured bottleneck data
- production services are added before the reference implementation requires them
- scanner adapters are added without scope gates
- LLM output becomes authority
- public docs claim unsupported compliance or unqualified security guarantees

## 16. Current Phase Boundary

B29A records tech stack boundaries only.

Implementation belongs to later scoped phases.
