# B4 - Git / CI Evidence Adapter

## 1. Phase Name & ID

**Phase ID:** B4
**Phase Name:** Git / CI Evidence Adapter
**Phase Type:** implementation
**Status:** backfilled from merged historical phase
**Primary PR:** #31
**Primary Issue:** Historical

---

## 2. Objective / Goal

Bind agent activity to repository and CI context.

Business goal:
- Give reviewers branch, commit, and CI context for agent actions.

Technical goal:
- Capture Git and CI metadata with diff digests, not raw diffs or tokens.

---

## 3. Problem Statement

This phase exists because:
- Agent actions need repository context.
- Raw diffs and tokens must not leak.
- CI metadata should be bounded.

Without this phase:
- Evidence is detached from commit context.
- Reviewer cannot connect action to Git state.

---

## 4. Scope

### In Scope

- Branch/head capture.
- Status count.
- Diff digests.
- GitHub Actions metadata when present.
- Signed trace and report.

### Out of Scope / Non-Goals

- No raw diff storage.
- No token capture.
- No full observability platform.

### Future Considerations

- Unified session bundle.
- CI verification action.

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
- `aapp/git_ci_evidence.py`

Test files:
- `tests/test_git_ci_evidence.py`

Fixture files:
- No unique fixture file or directory for this phase.

Documentation:
- `docs/phase-notes/B4_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `gitci.trace.jsonl`
- `gitci report`

### Code Artifacts

- Branch/head capture.
- Status count.
- Diff digests.
- GitHub Actions metadata when present.
- Signed trace and report.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B1 - Hook Gateway
- B3 - MCP Proxy Recorder

### Required Tools / Libraries

- Python 3.10+
- Git

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Digest diffs

Chosen:
- Store diff digests.

Rejected:
- Store raw diffs.

Reason:
- Diffs may contain secrets or proprietary code.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m unittest tests.test_git_ci_evidence -v
- python3 -m unittest discover -s tests -v

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Clean repo -> branch/head evidence.
- Modified file -> status/digest evidence.

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
| Diff leakage | High | Digest instead of raw content. |
| CI overreach | Medium | Capture bounded metadata only. |

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

- Git/CI context is part of evidence.
- Raw diffs remain out of trace.

Qualitative outcome:

- Reviewer connects evidence to repository state.

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
- B5 - Unified Session Bundle

The next phase depends on:
- Git/CI trace

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
- Branch/head capture.
- Status count.
- Diff digests.
- GitHub Actions metadata when present.
- Signed trace and report.

Deferred, not removed:
- Unified session bundle.
- CI verification action.

Final validation:
- python3 -m unittest tests.test_git_ci_evidence -v
- python3 -m unittest discover -s tests -v

Final status:
- backfilled from merged historical phase
