# B27 Scope Lock — Incident Response Casefile

## Built in B27

- Incident casefile generator
- Incident timeline JSONL
- Incident closure receipt
- Machine-readable incident verdict
- Tests for:
  - firewall DENY opens case
  - verify FAILED opens case
  - governance UNSAFE opens case
  - policy violation opens case
  - low-risk ALLOWED returns CASE_NOT_REQUIRED
  - missing source returns MALFORMED
  - unsupported source schema returns UNSUPPORTED
  - private key/raw secret returns UNSAFE
  - closure without approval returns CLOSURE_REJECTED
  - closure with approval returns CASE_CLOSED

## Deferred, not removed

- Threat Detection Signals → B28
- Audit / SIEM Export → B29
- Policy Backend Adapter → B30
- Crypto Inventory Scanner → B31
- Crypto Policy Decision → B32
- Crypto Migration Planner → B33
- Compliance Evidence Mapping → B34
- Pipeline Orchestrator → B35
- Signing Provider Interface → B36
- Secret Evidence Boundary → B37
- Workload Identity Provider Adapter → B38
- Evidence Ownership & IP Rights Ledger → B39
- Tenant Boundary / Enterprise Data Isolation → B40
- Crypto-Agility / PQ Readiness Planner → B41

## Rule

Do not add SIEM, SOAR, notification, cloud containment, compliance certification, threat ML, or crypto inventory inside B27.

B27 converts existing failure states into structured incident casefiles only.
