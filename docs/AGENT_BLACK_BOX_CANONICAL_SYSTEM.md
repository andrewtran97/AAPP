# Agent Black Box / AAPP — Canonical Internal System Definition

## 0. Executive Verdict

Agent Black Box / AAPP = Capability-Bound Agentic Security Control + Evidence Plane.

AAPP is the control-and-evidence layer for AI agents acting on software, CI/CD, tools, data, secrets, dependencies, artifacts, infrastructure, and security workflows.

Short line:

Flight recorder + capability kernel for AI agent actions.

Internal line:

AAPP turns AI-agent authority into scoped, caveated, testable, auditable, and reversible security operations.

## 1. Current Implementation Boundary

Current AAPP is a local reference implementation for AI-agent action evidence.

Current repo boundary:

- hook capture
- MCP tool-call recording
- Git/CI evidence
- unified session bundles
- verification and review path
- local deterministic reference gates

AAPP is not currently:

- scanner product
- SIEM
- pentest bot
- dashboard product
- compliance certification system
- full agent containment guarantee
- post-quantum security claim
- autonomous red-team system

## 2. Unified System Definition

AAPP replaces these fragmented labels:

- AI Agent Control + Evidence Plane
- Authorized Exposure Remediation Graph
- Agentic Cyber-Physical Control & Evidence Plane
- Agent Capability & Evidence Kernel
- Agentic Security Control Plane

Canonical definition:

Capability-Bound Agentic Security Control + Evidence Plane.

## 3. Core Equation

AAPP =

Scope
+ Identity
+ Capability
+ Policy
+ Tool Boundary
+ State Boundary
+ Evidence
+ Governance
+ Provenance
+ Remediation
+ Runtime Feedback
+ Incident Learning

## 4. Execution Chain

Mandate
→ Scope Contract
→ Agent / Tool / Workload Identity
→ Capability Token
→ Policy Decision
→ Tool Firewall
→ Execution Boundary
→ State Snapshot
→ Evidence Event
→ Governance Verdict
→ Finding / Patch / Receipt
→ Provenance Update
→ Runtime Signal Correlation
→ Incident / Near-Miss Casefile
→ Closure Receipt

## 5. Eight Planes

### 5.1 Agent Control Plane

Controls agent intent, scope, identity, tool request, policy decision, approval, and execution boundary.

### 5.2 Capability & Identity Plane

Converts broad agent authority into small, scoped, time-bound capability objects with caveats, issuer, subject, action, resource, expiry, and revocation reference.

### 5.3 Evidence & Forensic Plane

Records requests, decisions, traces, state, evidence digests, redaction verdicts, receipts, signatures, verification results, and casefiles.

### 5.4 Data Governance & Policy-Carrying Data Plane

Prevents AI agents from leaking secrets, private data, regulated data, training-prohibited data, or tenant data through prompts, tools, logs, exports, reports, or model-training workflows.

### 5.5 Code Safety & Patch Control Plane

Allows AI agents to propose fixes without bypassing tests, invariants, rollback notes, CI, approval, and post-merge validation.

### 5.6 Supply Chain & Provenance Plane

Tracks where code, dependencies, artifacts, models, datasets, plugins, and build outputs came from.

### 5.7 Authorized Exposure Remediation Graph

Converts authorized security assessment into remediation, not just findings.

### 5.8 Runtime Feedback & Incident Learning Plane

Correlates runtime signals, CI failures, logs, honeynet observations, incident records, near-misses, and analyst feedback into future control improvements.

## 6. System Graph

AAPP is a graph, not a linear log.

Node types:

- Subject: human, agent, tool, CI job, workload, reviewer, approver
- Authority: mandate, scope, capability, policy decision, approval, revocation
- Asset: repo, branch, commit, file, package, API, container, cloud account, IAM role, secret reference, CI workflow, model, dataset, plugin, artifact, runtime service
- Security object: finding, evidence event, trace, receipt, casefile, patch PR, rollback note, SBOM, signature, provenance statement, runtime signal, disclosure case

Edge types:

- subject_requested_action
- capability_authorizes_action
- scope_allows_resource
- policy_decides_request
- tool_executes_action
- evidence_records_event
- finding_affects_asset
- patch_remediates_finding
- test_validates_patch
- rollback_reverses_patch
- artifact_built_from_commit
- sbom_describes_artifact
- signature_attests_artifact
- runtime_signal_correlates_with_asset
- casefile_closes_incident
- receipt_verifies_closure

If an action cannot be linked to scope, identity, capability, policy, evidence, governance, provenance, and outcome, it is not trusted.

## 7. Control Laws

- No scope → no action.
- No written authorization → no scan.
- No policy → default deny.
- No identity → no trusted execution.
- No capability → no tool access.
- No caveat → no elevated action.
- No expiry → no capability.
- No revocation path → no capability.
- No evidence → no done.
- No governance verdict → no export.
- No rights → no training use.
- No verifier → no receipt.
- No approval → no destructive action.
- No reversal plan → no production mutation.
- No test/invariant package → no patch execution.
- No provenance → no deployment trust.
- No runtime evidence → no runtime closure.
- No casefile → no trusted failure closure.
- No post-merge validation → main not accepted.
- No exact staged-file guard → no commit.
- No CI pass → no merge.
- No issue close before merge and post-merge validation.

## 8. Data Classification Plane

Classification levels:

- PUBLIC
- INTERNAL
- CONFIDENTIAL
- RESTRICTED

Core law:

No classification → no access, export, training, or evidence release.

Required classification envelope fields:

- data_id
- classification
- owner
- tenant
- source
- purpose
- allowed_flows
- blocked_flows
- retention
- redaction_required
- approval_required
- audit_required
- dlp_required
- raw_secret_present

Governance verdicts:

- ALLOWED
- REDACTED
- BLOCKED
- MALFORMED
- UNSAFE
- UNSUPPORTED
- RETENTION_VIOLATION
- EXPORT_NOT_ALLOWED
- TRAINING_NOT_ALLOWED
- TENANT_BOUNDARY_VIOLATION
- CLASSIFICATION_REQUIRED
- CLASSIFICATION_DOWNGRADE_BLOCKED
- APPROVAL_REQUIRED
- MULTI_APPROVAL_REQUIRED
- WATERMARK_REQUIRED
- DLP_REQUIRED
- LEGAL_HOLD_BLOCKED

Data classification laws:

- No owner → no access.
- No tenant → no cross-tenant flow.
- No purpose → no processing.
- No allowed flow → block.
- Blocked flow matched → block.
- No approval → no Confidential export.
- No multi-approval → no Restricted export.
- No audit → no Restricted access.
- No DLP/export gate → no Confidential or Restricted export.
- No redaction → no Restricted evidence release.
- No rights → no training use.
- No retention policy → no storage.
- Legal hold active → no deletion.
- Raw secret present → no export, no training, no public report.
- Classification downgrade without approval → block.

## 9. Business Metrics

AAPP optimizes for:

- agent_action_coverage
- deny_stop_rate
- evidence_verify_rate
- raw_secret_escape_rate
- policy_decision_latency_ms
- patch_PR_acceptance_rate
- false_positive_triage_rate
- mean_time_to_casefile
- mean_time_to_remediation
- post_merge_validation_pass_rate
- unsupported_claim_count

Targets:

- data_classification_coverage = 100%
- raw_secret_escape_rate = 0
- unsupported_claim_count = 0

## 10. Implementation Discipline

Current reference stack:

- Python 3.10+
- Bash
- unittest
- JSON / JSONL
- Markdown
- GitHub Actions
- Git
- OpenSSL / Ed25519 workflows
- HMAC-SHA384 internal verification

Current implementation discipline:

- one phase = one bounded control primitive
- one issue = one failure mode
- one branch = one product gate
- one PR = exact file manifest
- no runtime behavior change unless scoped
- no broad rewrite
- no Go/Rust/TypeScript production rewrite before schema freeze

Target architecture anchors:

- Go: control API, policy service, orchestration
- Rust: evidence engine, scanner core, CLI
- TypeScript: UI, SDK, VS Code/Cursor extension
- OPA/Rego: policy backend
- PostgreSQL: ledgers, state, casefiles
- Object store: evidence blobs/packages
- OpenTelemetry: traces, metrics, logs
- SPIFFE/SVID: workload identity
- SLSA/Sigstore/Rekor: supply-chain signing/provenance
- CycloneDX/SPDX: SBOM / AI-BOM / CBOM

These anchors are not current implementation-complete claims.

## 11. Claim Boundary

Do not claim:

- self-directed offensive-action claim
- unrestricted scanning claim
- zero-risk claim
- fault-free claim
- fraud-impossibility claim
- artifact-cleanliness claim
- containment-guarantee claim
- production-security-maturity claim
- compliance-certification claim
- FedRAMP-readiness claim
- FIPS-readiness claim
- CISA-approval claim
- defense-grade-security claim
- post-quantum-security claim
- automatic-merge claim
- production-self-repair claim
- legal-evidence-finality claim
- immutability claim
- tamper-impossibility claim
- leak-impossibility claim
- DLP-completeness claim
- tenant-isolation-completeness claim

Allowed wording:

- local reference implementation
- canonical internal system definition
- target architecture
- evidence-supporting
- tamper-evident
- scope-bound
- capability-bound
- policy-gated
- reviewable
- reversible
- classification-based control model
- redaction-aware
- export-gated
- training-gated
- tenant-aware
- designed to reduce data exposure risk
- designed to support future regulated-enterprise review

## 12. Final Internal Line

AAPP is the security operating layer for AI agents: every action, tool call, code change, data flow, artifact, runtime signal, and remediation path is constrained by scope, capability, policy, identity, evidence, governance, provenance, and review.

Anything else is either a log viewer, a scanner, or marketing noise.
