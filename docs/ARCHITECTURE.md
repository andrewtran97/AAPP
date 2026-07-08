# Agent Black Box Architecture

## 1. Purpose

Agent Black Box is an AI Agent Control + Evidence Plane.

It controls agent, tool, CI, and reviewer actions through deterministic boundaries before execution and evidence generation.

This document describes target architecture and current repository boundaries. It does not claim that every target component is implemented today.

## 2. Current Implementation Boundary

The current repository is a reference implementation.

Current active stack:

- Python
- Bash
- GitHub Actions
- JSON / JSONL
- Markdown
- unittest

Current accepted gates:

- B27C Developer Distribution Gate
- B27D Public Release Readiness Gate
- B28 Policy Abstraction + Deterministic Risk Signals
- B29 Evidence Performance Plane
- B29A Architecture + Tech Stack Documentation Gate

## 3. Target System Context

Agent Black Box stands between user intent, agent tool calls, CI actions, and external resources.

It produces policy decisions, evidence artifacts, casefiles, and reviewer-facing reports.

## 4. Seven-Layer Architecture

The target system has seven layers:

- Scope Engine
- Orchestration Gateway
- Six Control Agents
- Runtime Evidence Pipeline
- Evidence Protocol
- Data Governance
- Product Surface

It also has two cross-cutting layers:

- Adversarial Systems Intelligence
- Release / Supply Chain Maturity Layer

## 5. Control Laws

- No scope -> no active scan.
- No policy -> default deny.
- No identity -> no trusted execution.
- No evidence -> no done.
- No verifier -> no receipt.
- No approval -> no destructive action.
- No reversal plan -> no destructive production mutation.
- No governance verdict -> no evidence export.
- No casefile -> no trusted failure closure.
- No manifest -> no phase complete.
- No rights -> no training use.
- No post-merge validation -> main is not accepted.

## 6. Scope Engine

The Scope Engine decides whether a request is inside an authorized boundary.

It classifies intent such as read, write, delete, deploy, scan, export, and policy_change.

Boundary:

- No active scan without scope.
- No privileged action without authorization.
- Ambiguous intent must not execute as privileged action.

## 7. Orchestration Gateway

The Orchestration Gateway routes intent into controlled execution.

It parses intent, selects tools, applies security gateway checks, routes human approval when required, and sends events to the evidence pipeline.

Boundary:

- No LLM output may bypass deterministic gates.
- No deploy path may bypass CI, policy, and human or configured authority.
- No denied action may disappear without evidence.

## 8. Six Control Agents

The Six Control Agents are:

1. Discovery & Scanner Agent.
2. Policy Engine Agent.
3. Identity & Attestation Agent.
4. State & Migration Agent.
5. Audit, CDM & Incident Agent.
6. Governance, Data & Compliance Agent.

## 9. Runtime Evidence Pipeline

A normal request follows this sequence:

1. User or agent submits intent.
2. Scope Engine validates scope and classifies intent.
3. Orchestration Gateway prepares the controlled route.
4. Policy Engine returns ALLOW, DENY, or REQUIRE_APPROVAL.
5. Identity & Attestation binds workload and digest context.
6. State & Migration records pre-state and reversal requirements when needed.
7. Executor runs only inside the permitted boundary.
8. Evidence Protocol records evidence and receipt material.
9. Governance reviews classification, redaction, retention, rights, and export boundary.
10. Incident path opens a casefile when unsafe, blocked, or failed.

## 10. Evidence-Control Protocol

The target evidence path is:

action -> canonical payload -> digest -> tamper check -> evidence record -> verify pack -> governance verdict -> receipt or casefile.

This document describes a tamper-evident target pattern.

It does not claim that evidence is impossible to alter.

## 11. Judge Court Layer Position

The Judge Court Layer may review, rank, or recommend candidate outputs.

It must not be final authority for:

- merge
- deploy
- allow
- deny
- security-sensitive execution
- compliance acceptance

Final authority remains deterministic gates, CI, policy, and human or configured merge authority.

## 12. Product Surface

Current repository surface:

- quickstart.sh
- README
- docs
- examples
- tests
- Python reference modules

Future product surface may include SDKs, IDE extension, dashboard, and production services.

Those future surfaces are not active implementation in B29A.

## 13. Architecture Boundary

B29A is documentation-only.

B29A must not add:

- Go implementation
- Rust implementation
- TypeScript implementation
- gRPC service
- NATS service
- OPA adapter implementation
- Kubernetes deployment
- B30 external witness receipt implementation

## 14. Architecture Failure Modes

This architecture fails when:

- scope checks are bypassed
- policy decisions are treated as optional
- identity is not bound to execution
- evidence is missing or unverifiable
- governance verdicts are skipped
- LLM review becomes final authority
- future production stack is described as current implementation
- public docs claim certification or unqualified security guarantees

## 15. Current Phase Boundary

B29A records architecture boundaries only.

Implementation of future external witness receipts belongs to B30 or later.
