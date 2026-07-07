# B0 - Repository Constitution / Product Boundary Gate

## 1. Phase Name & ID

**Phase ID:** B0
**Phase Name:** Repository Constitution / Product Boundary Gate
**Phase Type:** governance
**Status:** backfilled constitution record
**Primary PR:** Backfill branch
**Primary Issue:** None

---

## 2. Objective / Goal

Define the product boundary, language boundary, and repository operating rules before implementation phases.

Business goal:
- Make AAPP understandable as a controlled technology system, not a loose collection of scripts.

Technical goal:
- Create the canonical boundary for Agent Black Box as an AI Agent Control + Evidence Plane.

---

## 3. Problem Statement

This phase exists because:
- The repository needs one system definition before phase records can be trusted.
- Without B0, README, PRs, issues, and phase notes can drift into different product categories.
- Unsupported security or certification language creates trust and legal risk.

Without this phase:
- Future phases can use inconsistent names and claims.
- Reviewers cannot distinguish product boundary from future ambition.
- Scope creep becomes normal instead of exceptional.

---

## 4. Scope

### In Scope

- Define Agent Black Box as AI Agent Control + Evidence Plane.
- Define claim boundaries and forbidden product categories.
- Define phase manifest discipline for B1-B27 backfill.
- Define repository language rules for future phases.

### Out of Scope / Non-Goals

- No runtime code.
- No tests.
- No README update.
- No CI workflow change.
- No issue metadata change.
- No implementation after B27.

### Future Considerations

- Repo enforcement checks can be added in a separate scoped branch.
- README and architecture surface can be refreshed in a separate scoped branch.
- Post-B27 implementation remains out of scope for this backfill.

---

## 5. Metrics

### Completion Metrics / Definition of Done

- Required files are tracked or explicitly marked as not applicable for this historical phase.
- Required output artifacts are documented.
- Validation commands are listed.
- Scope, non-goals, risks, kill conditions, and transition criteria are explicit.
- No unsupported product, security, or certification-style claim appears.

### Quality & Safety Metrics

- No raw secrets, private keys, access tokens, or unredacted customer data in tracked files.
- Unsafe input returns deterministic unsafe or blocked behavior where applicable.
- Malformed input returns deterministic malformed behavior where applicable.
- Unsupported schema returns deterministic unsupported behavior where applicable.
- Denied or destructive paths do not execute side effects unless explicitly scoped.
- Human-readable reports and machine-readable verdicts are stable where applicable.

### Adoption / Usability Metrics

- A new reviewer can understand the phase boundary from this file.
- Required outputs use stable filenames.
- CLI, script, or workflow usage is listed where applicable.
- Non-goals prevent over-reading the phase as a broader platform.

### Performance / Scale Metrics

- No unbounded directory scan unless explicitly scoped.
- No network call unless explicitly scoped.
- Runtime remains suitable for local CI validation.
- Runtime evidence stays outside tracked source.

---

## 6. Deliverables

### Required Files

Production files:
- No unique production source file for this phase.

Test files:
- No unique tracked test file for this phase.

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/PHASE_MANIFEST_STANDARD.md`
- `docs/phase-notes/B0_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `B0 repository boundary record`

### Code Artifacts

- Define Agent Black Box as AI Agent Control + Evidence Plane.
- Define claim boundaries and forbidden product categories.
- Define phase manifest discipline for B1-B27 backfill.
- Define repository language rules for future phases.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- Clean repository state

### Required Tools / Libraries

- Git
- Markdown

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: System category

Chosen:
- Use AI Agent Control + Evidence Plane.

Rejected:
- Use generic security platform language.

Reason:
- The system controls agent actions and records evidence; it is not a SIEM, SOAR, IDS, or certification system.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

### Decision 2: Docs-only backfill

Chosen:
- Write tracked phase manifests only.

Rejected:
- Modify code or CI in the same branch.

Reason:
- This keeps the branch reviewable and avoids mixing governance with runtime changes.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- Validate B0-B27 docs exist.
- Validate no files outside the docs allowlist changed.
- Run `git diff --check`.

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Cold reviewer opens B0 and understands what AAPP is and is not.
- Maintainer can reject unsupported claim language using B0.

### Validation Script

Use the validation commands listed above for the historical phase. This backfill branch itself performs docs-only validation.

### Review Process

Implementation role:
- Creates only scoped branch changes.

CI:
- Runs automated checks and regression tests.

Human maintainer:
- Reviews scope, files, outputs, non-goals, validation, and merge decision.

Main branch:
- Becomes the official record only after merge and post-merge validation.

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---:|---|
| Constitution becomes marketing copy | High | Use claim boundaries and non-goals. |
| Backfill edits runtime files | High | Use allowlist validation. |

---

## 11. Kill Conditions

Abort or rollback this phase if:

- Any file outside the B0-B27 docs-only allowlist is changed.
- Any runtime code, test, README, CI workflow, release asset, issue metadata, or packaging file is changed.
- Any `.aapp/` runtime evidence is staged or committed.
- Any raw secret, private key, access token, or unredacted customer data appears.
- Any phase claims certification, absolute containment, absolute tamper resistance, or absolute bypass resistance.
- Any phase invents required files that do not exist or are not intentionally created by the scoped phase.
- Any phase after B27 is edited, generated, or implemented.

---

## 12. Success Criteria

When this phase is complete, we will have:

- AAPP has a root product boundary.
- B1-B27 phase docs have a common standard.
- Future phases have a contract format.

Qualitative outcome:

- Reviewer understands the system category in two minutes.
- Maintainer has language to reject scope creep.

---

## 13. Transition to Next Phase

This phase may transition to the next phase only when:

- All required files are tracked or explicitly marked not applicable.
- All required outputs are documented.
- Unit tests pass where applicable.
- Regression tests pass where applicable.
- Non-goals were not violated.
- Post-merge validation passes on `main`.

Next phase:
- B1 - Hook Gateway

The next phase depends on:
- B0 product boundary
- B0 claim boundary

---

## 14. Timeline & Owner

Owner:
- Human maintainer / repository owner

Implementation role:
- Branch implementer

Validation role:
- CI + regression tests + post-merge validation

Target timeline:
- Historical backfill; no runtime change.


---

## 15. Final Phase Record

Built in this phase:
- Define Agent Black Box as AI Agent Control + Evidence Plane.
- Define claim boundaries and forbidden product categories.
- Define phase manifest discipline for B1-B27 backfill.
- Define repository language rules for future phases.

Deferred, not removed:
- Repo enforcement checks can be added in a separate scoped branch.
- README and architecture surface can be refreshed in a separate scoped branch.
- Post-B27 implementation remains out of scope for this backfill.

Final validation:
- Validate B0-B27 docs exist.
- Validate no files outside the docs allowlist changed.
- Run `git diff --check`.

Final status:
- backfilled constitution record
