# External Reviewer Guide

This guide gives an external reviewer a safe review path for AAPP / Agent Black Box.

B27D is documentation-only.

It does not change runtime behavior.

It does not change scanner behavior.

It does not change policy engine behavior.

It does not implement B28.

## 1. First Files To Read

Read these files first:

- README.md
- docs/CLAIM_BOUNDARIES.md
- docs/PUBLIC_RELEASE_READINESS.md
- docs/phase-notes/B27D_SCOPE.md

## 2. Local Review Path

Run:

bash quickstart.sh

Then run the examples individually:

bash examples/local-agent/run.sh
bash examples/github-action/run.sh
bash examples/mcp-tool-call/run.sh

Expected result:

- examples run locally
- no secrets are requested
- no paid external service is required
- no browser is opened
- no runtime evidence is written into .aapp/

## 3. What To Inspect

Inspect:

- file manifest
- claim boundaries
- phase scope
- quickstart behavior
- example behavior
- test output
- public wording

## 4. What Not To Assume

Do not assume:

- external approval
- production deployment approval
- complete prevention of every misuse path
- customer data ownership
- certification status
- compliance guarantee

## 5. Runtime Boundary

B27D must not change:

- aapp/*
- tests/test_*
- tests/fixtures/*

B27D must not create:

- aapp/policy_abstraction.py
- aapp/deterministic_risk_signals.py

## 6. Reviewer Validation Commands

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

## 7. Review Stop Conditions

Stop review if:

- runtime files changed
- test files changed
- fixture files changed
- B28 files appear
- tests fail
- public docs overclaim readiness
- secrets are required
- paid services are required
- __pycache__ remains
