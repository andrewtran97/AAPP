# Public Release Readiness

This document defines the B27D public release readiness checklist.

B27D is documentation-only.

It does not change runtime behavior.

It does not change scanner behavior.

It does not change policy engine behavior.

It does not implement B28.

## 1. Repository Entry Points

Required public entry points:

- README.md
- docs/CLAIM_BOUNDARIES.md
- docs/PUBLIC_RELEASE_READINESS.md
- docs/EXTERNAL_REVIEWER_GUIDE.md
- docs/RELEASE_NOTES_DRAFT.md
- quickstart.sh
- examples/local-agent/README.md
- examples/github-action/README.md
- examples/mcp-tool-call/README.md

## 2. Local Run Path

A reviewer should be able to run:

bash quickstart.sh

Expected result:

- local-agent example runs
- github-action example runs
- mcp-tool-call example runs
- repository validators run when present
- no secrets are required
- no paid external service is required
- no browser is opened

## 3. Claim Boundary Check

Public docs must not claim:

- external approval
- agency endorsement
- complete prevention of every misuse path
- production deployment approval
- ownership of customer data
- certification status
- compliance guarantee

Public docs may claim:

- local evidence artifacts for review
- deterministic policy paths in accepted phases
- tamper-evident evidence artifacts
- scope-gated local examples
- workload identity binding patterns
- incident-ready casefile artifacts in accepted phases
- developer-runnable local reference path

## 4. Release Readiness Checklist

Before public release review:

- README has a local developer quickstart.
- Claim boundaries are documented.
- External reviewer guide exists.
- Release notes draft exists.
- B27D scope file exists.
- Existing unit tests pass.
- Public wording avoids overclaim.
- No runtime files are changed.
- No test files are changed.
- No test fixtures are changed.
- No B28 files are created.
- No .aapp runtime evidence is committed.
- No __pycache__ remains.

## 5. Validation Commands

Run:

bash quickstart.sh

Run:

PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_required_files.py

Run:

PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_phase_manifest.py

Run:

PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_claim_boundaries.py

Run:

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v

## 6. Kill Conditions

Do not merge B27D if:

- runtime behavior changes
- scanner behavior changes
- policy engine behavior changes
- B28 files appear
- secrets are required
- paid external services are required
- public wording implies external endorsement
- tests regress
- __pycache__ remains
