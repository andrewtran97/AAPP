# Agent Black Box / AAPP — Canonical System V2

## 0. Status Vocabulary

- `IMPLEMENTED`: present and testable in the current Python-first repository.
- `REFERENCE`: deterministic local shape or contract; not production enforcement.
- `TARGET`: intended architecture that is not implemented in this repository.
- `RESEARCH`: hypothesis requiring a baseline, benchmark, and explicit future authorization.
- `OUT_OF_SCOPE`: prohibited or deliberately excluded from the current system boundary.

Status is attached to behavior, not branding. A target or research item must never be presented as implemented.

## 1. Unified Definition

Agent Black Box / AAPP is a **Capability-Bound Agentic Security Control + Evidence Plane**.

Public positioning:

> Flight recorder and capability-control layer for AI-agent actions.

Internal positioning:

> AAPP converts AI-agent authority into operations constrained by explicit scope, identity, capability, policy, approval, data rights, evidence, verification, provenance, and recovery.

Canonical system formula:

```text
Agent Black Box
= Deterministic Authority Kernel
+ Capability-Bound Agent Fabric
+ Agent Skill Infrastructure
+ Governed AI Services
+ Evidence & Data Governance Graph
+ Remediation & Recovery
+ Runtime Feedback & Evaluation
```

## 2. Current Repository Boundary

### IMPLEMENTED

The repository currently provides a Python-first deterministic reference layer including:

- local hook-event capture;
- MCP tool-call recording;
- Git/CI evidence capture;
- unified session bundles;
- local verification and report paths;
- deterministic reference gates for scope, policy, identity, evidence, governance, secrets, tenants, crypto migration, and PQ-readiness planning.

### REFERENCE

The deterministic gates demonstrate contracts, verdict shapes, and fail-closed behavior locally. They are not equivalent to production interception, production identity, production DLP, database-backed isolation, or hardened distributed enforcement.

### TARGET

The authority kernel, capability-bound fabric, skill execution substrate, production provenance adapters, durable recovery, and runtime learning loop are target architecture.

### RESEARCH

AntSwarm scheduling, device acceleration, multi-model councils, and broad agent-skill compatibility remain benchmark-gated research.

### OUT_OF_SCOPE

- unauthorized scanning or exploitation;
- self-directed offensive action;
- direct cyber-physical mutation;
- unrestricted shell, browser, cloud, or production authority;
- claims of certification, universal correctness, guaranteed containment, or post-quantum security.

## 3. Product Boundary

AAPP is Agent Action Control & Evidence Infrastructure. It is not an LLM, chatbot, general agent framework, SAST scanner, pentest bot, SIEM, observability dashboard, or security certification product.

The first product wedge is an AI coding-agent workflow:

```text
request -> exact repository scope -> capability/policy gate
        -> candidate change -> tests -> evidence -> verified receipt
```

## 4. Compatible Taxonomies

Seven structural layers describe topology:

1. Scope Engine
2. Orchestration Gateway
3. Six Control Agents
4. Runtime Evidence Pipeline
5. Evidence Protocol
6. Data Governance
7. Product Surface

Eight control planes describe cross-cutting responsibilities:

1. Agent Control
2. Capability & Identity
3. Evidence & Forensics
4. Data Governance
5. Code Safety & Patch Control
6. Supply Chain & Provenance
7. Authorized Exposure Remediation
8. Runtime Feedback & Incident Learning

Six control agents describe bounded services:

1. Discovery / Scanner
2. Policy Engine
3. Identity / Attestation
4. State / Migration
5. Audit / CDM / Incident
6. Governance / Data / Compliance

These are three views of one system. They do not create parallel products or additional control planes.

## 5. Deterministic Authority Kernel

### TARGET

The microkernel-inspired authority kernel owns only:

- schema validation;
- identity and capability validation;
- policy invocation and admission control;
- execution leases and revocation;
- tenant context and IPC-envelope validation;
- evidence sequence allocation;
- bounded service health.

The kernel does not contain LLM reasoning. AI recommendations cannot become kernel decisions without deterministic validation and configured authority.

Kernel laws:

- No identity -> no trusted IPC.
- No scope -> no action.
- No capability -> no dispatch.
- No policy -> default deny.
- No tenant context -> no governed data access.
- No execution lease -> no tool execution.
- No evidence sequence -> action does not start.
- Revoked capability -> terminate or quarantine.
- AI recommendation != kernel decision.

## 6. Capability-Bound Agent Fabric

### TARGET

The fabric is the only trusted route for service discovery, workload identity, authenticated IPC, capability delegation, policy-aware routing, data-locality routing, revocation propagation, replay protection, and evidence handoff.

Every fabric message must bind sender, recipient, action, scope, capability, policy decision, tenant, classification, payload digest, expiry, and replay nonce. Direct peer calls outside the fabric are prohibited by the target architecture.

## 7. Execution Lifecycle

```text
Mandate / Intent
-> Intent Canonicalization
-> Risk Class
-> Scope Contract
-> Identity
-> Capability Request
-> Policy Decision
-> Approval / Obligations
-> Tool or Skill Contract
-> Execution Lease
-> Pre-State Snapshot
-> Bounded Execution
-> Post-State Snapshot
-> Evidence Events
-> Governance Verdict
-> Verification
-> Provenance
-> Receipt
-> Recovery / Incident
-> Approved Learning Candidate
```

A denied action stops execution but still produces a denied-attempt event, reason codes, and a risk signal.

## 8. Evidence and System Graph

### IMPLEMENTED

The repository implements local evidence events, digests, bundles, manifests, verification results, and reports for its scoped reference workflows.

### REFERENCE

Canonical evidence chain:

```text
structured request -> canonical serialization -> input digest
-> authority references -> trace events -> previous-event digest
-> bundle -> manifest -> signature -> verification -> receipt
```

Evidence can show recorded bytes, sequence membership, signer-to-bytes binding, recorded policy/version references, and a verifier result. It does not establish objective correctness, absence of vulnerabilities, legal finality, signer trustworthiness, or universal immutability.

The system graph connects subjects, authority objects, assets, and security objects through typed evidence-bearing edges.

## 9. Data Governance

### REFERENCE

Classification levels:

- `PUBLIC`
- `INTERNAL`
- `CONFIDENTIAL`
- `RESTRICTED`

Every governed data object must bind classification, owner, tenant, purpose, rights reference, allowed and blocked flows, retention, legal hold, redaction requirement, and raw-secret presence.

Core laws:

- No classification -> no governed flow.
- No owner or purpose -> no processing.
- No tenant boundary -> no cross-tenant release.
- No governance verdict -> no export.
- No rights -> no training.
- Raw secret present -> no export, training, or public report.

Current gates are deterministic references, not production DLP or production tenant isolation.

## 10. Governed AI Services

### REFERENCE

Bounded advisory roles are Triage Agent, Patch Agent, Recovery Agent, and Explain Impact Agent. Their outputs are schema-bound proposals.

Authority chain:

```text
AI proposes -> schema validates -> deterministic gates decide
-> tests/verifier evaluate -> configured authority approves
-> evidence records
```

AI cannot create scope, capability, final policy allow, approval, evidence identity, receipt identity, signature, verified digest, merge decision, or deployment decision.

## 11. Agent Skill Infrastructure

### REFERENCE / TARGET

The governed skill substrate consists of Skill Registry, Skill Package Manager, Skill Contract, Capability Runtime, Durable Task Bus, and Evaluation Service.

The contract invariant is:

```text
observed_accesses subset_of granted_capabilities subset_of requested_permissions
observed_effects subset_of declared_effects
```

Detailed boundaries are defined in `docs/AGENT_SKILL_INFRASTRUCTURE.md`.

## 12. Recovery and Reliability Surfaces

### TARGET

State-changing actions use one recovery class: `REVERSE`, `COMPENSATE`, `MITIGATE`, `REVOKE`, `CONTAIN`, or `IRREVERSIBLE`.

Control laws:

- No pre-state -> no reversible claim.
- No recovery class -> no mutable action.
- No idempotency key -> no automatic retry.
- Irreversible external action -> explicit approval.
- Failed recovery -> incident casefile.

Agent Flow Capture, AgentCTS, Compensation & Recovery, and Open Skill Runtime are product surfaces under AAPP Core, not independent authority systems.

## 13. Open-Source Doctrine

### TARGET

`REUSE -> CONFIGURE -> WRAP -> EXTEND -> CONTRIBUTE UPSTREAM -> FORK -> REPLACE`

Dependencies require known source/version, license review, security owner, inventory, vulnerability review, reproducible baseline, benchmark, and rollback/replacement path. Detailed rules are in `docs/OPEN_SOURCE_STRATEGY.md`.

## 14. AntSwarm Boundary

### RESEARCH

AntSwarm may select among already eligible candidate workflows. It cannot grant authority, change policy, approve actions, validate its own work, or mutate reward signals directly. Details are in `docs/ANTSWARM_COORDINATION_PLANE.md`.

## 15. Implementation Discipline

- One gate -> one issue -> one branch -> one pull request -> one acceptance record.
- No exact manifest -> no commit.
- No CI -> no merge.
- No post-merge validation -> main not accepted.
- Target architecture is not implementation evidence.
- Documentation does not authorize runtime behavior.

## 16. Claim Boundary

Allowed descriptions include deterministic reference implementation, local-only reference behavior, tamper-evident where technically supported, reviewable evidence, bounded authority, capability-limited action, advisory AI, and governed data.

Do not claim external certification, regulatory authorization, universal safety, guaranteed containment, objective truth, legal finality, complete DLP, complete tenant isolation, production maturity, or post-quantum security unless independently established and explicitly authorized.

## 17. Final Canonical Line

> Agent Black Box is the capability-bound security, execution, and evidence operating layer for AI agents. It constrains requests, tool calls, skills, data flows, state changes, artifacts, recovery actions, and learning proposals through explicit scope, identity, capability, policy, governance, provenance, verification, and review.
