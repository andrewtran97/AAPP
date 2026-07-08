# Agent Black Box Architecture

Agent Black Box is a Zero Trust Control + Evidence Plane for CI/CD and agentic workflows.

It gives AI agent actions and automation actions a deterministic control layer, tamper-evident evidence trail, workload identity binding, policy-change ledger, data governance verdict, and incident-ready casefile without claiming certification or taking ownership of customer data.

## Canonical pipeline

scope
→ surface scan
→ posture scan
→ tool request
→ policy abstraction
→ deterministic policy decision
→ workload identity binding
→ policy registry binding
→ state ledger
→ reversal plan
→ evidence record
→ Merkle transparency receipt
→ verify pack
→ evidence data governance
→ incident casefile if failure
→ deterministic risk signal
→ audit/SIEM export later
→ compliance evidence map later

## Macro-agents

1. Discovery & Crypto Scanner Agent
2. Policy Engine Agent
3. Identity Service Agent
4. Audit & CDM Agent
5. State & Migration Service Agent
6. Governance & Compliance Evidence Agent

## Current control laws

- No scope → no active scan.
- No policy → default deny.
- No identity → no trusted execution.
- No evidence → no done.
- No verifier → no receipt.
- No approval → no destructive action.
- No reversal plan → no destructive production mutation.
- No governance verdict → no evidence export.
- No casefile → no trusted failure closure.
- No manifest → no phase complete.

## Runtime boundary

Agent Black Box does not need to own the planner.

Agent Black Box controls the planner’s authority boundary by converting requested tool/resource actions into deterministic policy decisions, evidence records, receipts, and casefiles.
