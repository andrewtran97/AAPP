# B2 - Local Hook Install / Session Capture

## 1. Phase Name & ID

**Phase ID:** B2
**Phase Name:** Local Hook Install / Session Capture
**Phase Type:** local runtime
**Status:** backfilled historical local runtime phase
**Primary PR:** Historical
**Primary Issue:** Historical

---

## 2. Objective / Goal

Make local hook capture usable while keeping runtime evidence out of source control.

Business goal:
- Allow local review without polluting the repository with runtime artifacts.

Technical goal:
- Preserve `.aapp/` as ignored local evidence and avoid tracked runtime output.

---

## 3. Problem Statement

This phase exists because:
- Local sessions create evidence files.
- Runtime files can contain sensitive context.
- Source and runtime evidence must stay separated.

Without this phase:
- Runtime evidence may be committed.
- Local testing becomes unsafe for repo hygiene.

---

## 4. Scope

### In Scope

- Local session capture behavior.
- Ignored runtime evidence convention.
- No force-add of `.aapp/`.

### Out of Scope / Non-Goals

- No tracked `.aapp/` evidence.
- No production installer.
- No external integration claim.

### Future Considerations

- MCP recorder.
- Unified session bundle.

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
- `docs/phase-notes/B2_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `.aapp/evidence/* runtime output, ignored`

### Code Artifacts

- Local session capture behavior.
- Ignored runtime evidence convention.
- No force-add of `.aapp/`.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B1 - Hook Gateway

### Required Tools / Libraries

- Git
- .gitignore discipline

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Runtime evidence ignored

Chosen:
- Keep `.aapp/` out of tracked source.

Rejected:
- Force-add local evidence.

Reason:
- Runtime evidence can contain sensitive context.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- git status --short
- Confirm `.aapp/` runtime evidence is not staged.

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Local session capture -> output remains ignored.

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
| Runtime evidence committed | High | Never force-add `.aapp/`. |

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

- Local capture convention is explicit.
- Repo source remains clean.

Qualitative outcome:

- Maintainer can separate source files from evidence runtime files.

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
- B3 - MCP Proxy Recorder

The next phase depends on:
- Local runtime evidence convention

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
- Local session capture behavior.
- Ignored runtime evidence convention.
- No force-add of `.aapp/`.

Deferred, not removed:
- MCP recorder.
- Unified session bundle.

Final validation:
- git status --short
- Confirm `.aapp/` runtime evidence is not staged.

Final status:
- backfilled historical local runtime phase
