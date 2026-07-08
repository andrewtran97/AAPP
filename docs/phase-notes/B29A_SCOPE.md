# B29A Architecture + Tech Stack Documentation Gate

## 1. Phase Name & ID

B29A — Architecture + Tech Stack Documentation Gate.

## 2. Objective / Goal

Document the Agent Black Box architecture and tech stack boundaries without changing runtime behavior.

B29A records how the current reference implementation relates to the future production control plane.

## 3. Problem Statement

After B29, the repository has developer distribution, public release readiness, deterministic policy abstraction, deterministic risk signals, and local evidence performance measurement.

What is still missing is a clear architecture and tech stack boundary document set that explains:

- what exists now
- what is future target architecture
- what must not be claimed as implemented
- where LLM review fits
- where deterministic authority remains

## 4. Scope

### In Scope

- B29A phase manifest.
- Architecture documentation.
- Tech stack documentation.
- Proprietary candidate technology boundary documentation.
- Judge Court Layer authority boundary documentation.
- Documentation-only validation.

### Out of Scope / Non-Goals

- No B30 external witness receipt implementation.
- No runtime behavior change.
- No policy engine behavior change.
- No benchmark behavior change.
- No scanner behavior change.
- No Go code.
- No Rust code.
- No TypeScript code.
- No gRPC service.
- No NATS service.
- No OPA adapter implementation.
- No Kubernetes.
- No dashboard.
- No certification claim.
- No unsupported production validation claim.

## 5. Required Files

B29A may add or modify only:

- docs/phase-notes/B29A_SCOPE.md
- docs/ARCHITECTURE.md
- docs/TECH_STACK.md
- docs/PROPRIETARY_TECHNOLOGY_BOUNDARY.md
- docs/JUDGE_COURT_LAYER.md

## 6. Architecture Terms

Agent Black Box means:

AI Agent Control + Evidence Plane

It is composed of:

- Scope Engine
- Orchestration Gateway
- Six Control Agents
- Runtime Evidence Pipeline
- Evidence Protocol
- Data Governance
- Product Surface
- Adversarial Systems Intelligence
- Release / Supply Chain Maturity Layer

## 7. Tech Stack Boundary

Current reference stack:

- Python
- Bash
- GitHub Actions
- JSON / JSONL
- Markdown
- unittest

Future production target stack:

- Go control services
- Rust evidence and scanner core
- Python eval workers
- TypeScript UI, SDK, and VS Code extension
- OPA/Rego-compatible policy model
- gRPC / Protobuf service protocol
- NATS event bus first
- OpenTelemetry observability
- SLSA / Sigstore / Rekor / TUF later
- CycloneDX / SPDX BOM later
- Semgrep / OSV-Scanner adapters later
- SPIFFE/SVID-compatible identity adapter later

## 8. Control Laws

- No architecture doc may describe LLM as final merge, deploy, allow, deny, or security authority.
- No future production stack may be described as current implementation.
- No future supply-chain stack may be described as current compliance.
- No architecture diagram may bypass scope, policy, identity, evidence, governance, or human/configured authority gates.
- No B30 implementation files in B29A.

## 9. Proprietary Boundary

B29A may describe proprietary candidate technology.

B29A must not claim legal exclusivity, patent protection, certification, or external validation unless those artifacts exist.

Acceptable wording:

- proprietary candidate technology
- candidate control pattern
- target architecture
- future production boundary

Forbidden wording:

- legally exclusive proprietary technology
- external security certification architecture
- unqualified evidence permanence claim
- unqualified tamper guarantee
- production validated

## 10. Judge Court Layer Boundary

The Judge Court Layer may review, rank, or recommend.

The Judge Court Layer must not be described as final authority for:

- merge
- deploy
- allow
- deny
- security-sensitive execution
- compliance acceptance

Final authority remains deterministic gates, CI, policy, and human/configured merge authority.

## 11. Validation

B29A must pass:

- required docs exist
- Markdown headings exist
- quickstart passes
- required files checker passes
- phase manifest checker passes
- claim boundary checker passes
- full unittest suite passes
- worktree clean after validation

## 12. Kill Conditions

Stop if B29A:

- touches aapp/*.py
- touches benchmarks/*.py
- touches tests/test_*
- touches tests/fixtures/*
- adds Go, Rust, or TypeScript implementation
- creates B30 implementation files
- claims certification or unsupported production security validation
- describes LLM as final authority

## 13. Expected PR Summary

B29A adds architecture and tech stack documentation boundaries for Agent Black Box.

This is documentation-only.

## 14. Expected Reviewer Result

A reviewer should be able to understand:

- the current reference stack
- the future production stack
- which stack is active now
- which stack is future-only
- where deterministic gates sit
- why LLM review is not authority

## 15. Final Phase Record

B29A is accepted only after merge to main and post-merge validation passes.
