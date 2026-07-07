# AAPP Phase Manifest Standard

Every AAPP phase from B0 onward must have a tracked phase manifest.

Required location:

`docs/phase-notes/Bxx_SCOPE.md`

This standard exists to prevent scope drift, missing files, stale roadmap language, unsupported claims, and phase handoff ambiguity.

## Required Template

Every phase manifest must include:

1. Phase Name & ID
2. Objective / Goal
3. Problem Statement
4. Scope
5. Metrics
6. Deliverables
7. Dependencies & Prerequisites
8. Key Design Decisions
9. Validation Strategy
10. Risks & Mitigations
11. Kill Conditions
12. Success Criteria
13. Transition to Next Phase
14. Timeline & Owner
15. Final Phase Record

## Global Rules

- No Phase Manifest -> No branch.
- No Required Files section -> No implementation.
- No Non-Goals section -> Scope unsafe.
- No Kill Conditions -> Phase not reviewable.
- No Transition Criteria -> Do not open the next phase.
- No post-merge validation -> main is not accepted as the official record.
- Runtime evidence under `.aapp/` must not be committed.
- Raw secrets, private keys, access tokens, and unredacted customer data must not be committed.
- Public language must describe evidence-supporting capability, not certification or absolute security.

## Scope of This Backfill

This backfill is docs-only for B0-B27.

It does not modify runtime code, tests, README, CI workflows, issue metadata, release assets, packaging, or any post-B27 phase.


## 13. Transition to Next Phase

Describe the criteria, artifacts, validation state, and handoff conditions required before the next phase can start.


## 14. Timeline & Owner

State the owner and expected execution window when useful. For solo execution, use: Owner: human executor. Timeline: single product-gate PR.
