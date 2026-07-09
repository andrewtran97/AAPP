# B43 Tenant Boundary / Enterprise Data Isolation

## Purpose

B43 adds a local deterministic Tenant Boundary / Enterprise Data Isolation reference gate.

The gate evaluates whether a request respects tenant boundaries before evidence export, training use, report generation, or cross-tenant access.

## Scope

B43 is limited to a local deterministic reference implementation.

Expected files:

- `aapp/tenant_boundary.py`
- `docs/TENANT_BOUNDARY.md`
- `docs/phase-notes/B43_SCOPE.md`
- `tests/fixtures/tenant_boundary/sample_request.json`
- `tests/test_tenant_boundary.py`

## Non-goals

B43 does not implement:

- production tenant isolation
- production DLP
- external services
- network calls
- subprocess calls
- database-backed tenant storage
- runtime enforcement service
- scanner behavior changes
- policy engine behavior changes
- runtime execution behavior changes
- B44 implementation

## Control Laws

- No tenant -> no access.
- No source tenant -> no cross-tenant decision.
- No destination tenant -> no export decision.
- Tenant mismatch -> block unless explicit approved cross-tenant route exists.
- Cross-tenant export requires approval.
- Cross-tenant training is blocked by default.
- Evidence release across tenant boundary requires governance verdict.
- Tenant boundary verdict must preserve evidence digest.
- Raw tenant data must not be copied into cross-tenant evidence.

## Verdicts

- ALLOWED
- MALFORMED
- TENANT_BOUNDARY_VIOLATION
- CROSS_TENANT_EXPORT_NOT_ALLOWED
- CROSS_TENANT_TRAINING_NOT_ALLOWED
- APPROVAL_REQUIRED
- GOVERNANCE_VERDICT_REQUIRED

## Acceptance Criteria

- Expected B43 file manifest exists.
- Focused B43 unit tests pass.
- Full test suite passes.
- No network or subprocess dependency is introduced.
- Exact dirty and staged file guards pass.
