# AAPP Architecture

AAPP / Agent Black Box is an AI Agent Control + Evidence Plane.

It sits between user intent, CI/CD actions, AI agent tool calls, and workload execution. Its purpose is to enforce deterministic control, bind actions to identity and policy, record tamper-evident evidence, govern data exposure, and produce incident-ready casefiles.

## System Layers

1. Scope / Intent / Authorization Boundary
2. AI Agent Orchestration Gateway
3. Six Control Agents
4. Runtime / Evidence Pipeline
5. Evidence Protocol
6. Data Governance and Compliance Evidence
7. Product Surface

## Runtime Pipeline

```text
intent_or_action
→ scope_check
→ identity_binding
→ policy_abstraction
→ deterministic_policy_decision
→ approval_route_if_required
→ safe_execution_or_deny
→ state_ledger
→ evidence_record
→ merkle_receipt
→ verify_pack
→ governance_verdict
→ incident_casefile_if_needed
→ remediation_receipt
Six Control Agents
Discovery and Scanner Agent

Responsibilities:

Surface scan.
Posture scan.
Scoped network scan.
Crypto inventory.
Security finding ingest.
Static artifact trust boundary.
Policy Engine Agent

Responsibilities:

Policy abstraction.
Deterministic allow, deny, or approval decision.
Risk signals.
Vulnerability policy gate.
Claim-boundary gate.
Decision boundary ledger.
Identity and Attestation Agent

Responsibilities:

Workload identity binding.
Artifact digest binding.
Controller and runtime digest binding.
Policy registry binding.
Merkle evidence transparency.
State and Migration Agent

Responsibilities:

State ledger.
Reversal plan.
Crypto policy decision.
Crypto migration planning.
Readiness planning for future crypto transitions.
Audit, CDM, and Incident Agent

Responsibilities:

Evidence recording.
Verify pack.
CI artifact layer.
Incident response casefile.
Attack path hypothesis graph.
Authorized red-team evidence pack.
Governance, Data, and Compliance Evidence Agent

Responsibilities:

Evidence data governance.
Classification and redaction.
Evidence export gate.
Ownership and rights ledger.
Compliance evidence mapping.
Tenant boundary.
Control Laws
No scope -> no active scan.
No policy -> default deny.
No identity -> no trusted execution.
No evidence -> no done.
No verifier -> no receipt.
No approval -> no destructive action.
No reversal plan -> no destructive production mutation.
No governance verdict -> no evidence export.
No casefile -> no trusted failure closure.
No source receipt -> no outcome claim.
No manifest -> no phase complete.
No data rights -> no training use.
No exception expiry -> no exception accepted.
Non-Goals

AAPP is not a scanner clone, SIEM, IDS, SOAR, exploit toolkit, phishing toolkit, malware execution lab, or compliance-certification product.
