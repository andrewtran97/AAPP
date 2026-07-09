# Tenant Boundary / Enterprise Data Isolation

## Purpose

B43 adds a local deterministic tenant-boundary gate.

The gate evaluates whether a request respects tenant boundaries before evidence export, training use, report generation, or cross-tenant access.

## Inputs

Required fields:

- `request_id`
- `source_tenant`
- `destination_tenant`
- `action`
- `has_governance_verdict`
- `evidence_digest`

Optional fields:

- `approval_ref`

## Verdicts

- `ALLOWED`
- `MALFORMED`
- `TENANT_BOUNDARY_VIOLATION`
- `CROSS_TENANT_EXPORT_NOT_ALLOWED`
- `CROSS_TENANT_TRAINING_NOT_ALLOWED`
- `APPROVAL_REQUIRED`
- `GOVERNANCE_VERDICT_REQUIRED`

## Control Laws

- No tenant -> no access.
- No source tenant -> no cross-tenant decision.
- No destination tenant -> no export decision.
- Tenant mismatch -> block unless explicit approved cross-tenant route exists.
- Cross-tenant export requires approval.
- Cross-tenant training is blocked by default.
- Evidence release across tenant boundary requires governance verdict.
- Tenant boundary verdict must preserve evidence digest.

## Non-goals

B43 does not implement production tenant isolation, production DLP, network calls, subprocess calls, database-backed tenant storage, or runtime enforcement services.
