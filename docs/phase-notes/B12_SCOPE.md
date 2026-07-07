# B12 - README / CONTRIBUTING Brand Surface

## 1. Phase Name & ID

**Phase ID:** B12
**Phase Name:** README / CONTRIBUTING Brand Surface
**Phase Type:** documentation
**Status:** backfilled from merged historical phase
**Primary PR:** #40
**Primary Issue:** Historical

---

## 2. Objective / Goal

Make the public repository understandable and safe to contribute to.

Business goal:
- Improve first-impression clarity while preserving claim boundaries.

Technical goal:
- Update README positioning, quickstart, contribution rules, and status language.

---

## 3. Problem Statement

This phase exists because:
- Public repo needs clear framing.
- Contributors need boundaries.
- Unsupported claims create trust risk.

Without this phase:
- Reviewers misunderstand the project.
- PRs mix unrelated changes.
- Claim drift persists.

---

## 4. Scope

### In Scope

- README product surface.
- CONTRIBUTING rules.
- Quickstart.
- Evidence path explanation.
- Claim boundary language.

### Out of Scope / Non-Goals

- No protocol change.
- No runtime change.
- No dashboard.
- No scanner expansion.

### Future Considerations

- License.
- Release hygiene audit.
- Later README refresh in a separate scoped branch.

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
- `README.md`
- `CONTRIBUTING.md`
- `docs/phase-notes/B12_SCOPE.md`

Scripts / Workflows:
- No unique script or workflow for this phase.

Examples:
- No unique example artifact for this phase.

### Required Output Artifacts

- `README status sections`
- `CONTRIBUTING rules`

### Code Artifacts

- README product surface.
- CONTRIBUTING rules.
- Quickstart.
- Evidence path explanation.
- Claim boundary language.

### Documentation Artifacts

- This phase manifest.
- Phase boundary, non-goals, validation, and transition criteria.

---

## 7. Dependencies & Prerequisites

### Required Previous Phases

- B11 - Offline Review / Evidence Package QA

### Required Tools / Libraries

- Markdown

### Required Design Decisions

- Runtime evidence must not be committed from `.aapp/`.
- Public claims must describe evidence-supporting capability, not certification.
- Small phase scope is preferred over broad platform claims.
- Post-B27 work must use a separate scope.

---

## 8. Key Design Decisions

### Decision 1: Bounded public language

Chosen:
- Use precise status language.

Rejected:
- Use broad security platform language.

Reason:
- Credibility depends on accurate claims.

Trade-off:
- More explicit control and review burden, lower scope and claim risk.

---

## 9. Validation Strategy

### Automated Tests

- python3 -m unittest discover -s tests -v
- bash scripts/run_agent_black_box_e2e.sh

### Manual Checklist

- Confirm only scoped files changed.
- Confirm output artifacts are documented.
- Confirm non-goals are not violated.
- Confirm no unsupported claim language appears.
- Confirm runtime evidence is not staged.

### Scenario Tests

- Cold reviewer -> can run quickstart.
- Contributor -> sees small-patch rule.

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
| README stale | Medium | Refresh in separate scoped branch. |
| Contributor scope drift | High | Use contribution rules and future templates. |

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

- Public repo has clearer product/contribution surface.

Qualitative outcome:

- New reviewer understands available vs pending.

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
- B13 - Apache-2.0 License

The next phase depends on:
- Public status language

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
- README product surface.
- CONTRIBUTING rules.
- Quickstart.
- Evidence path explanation.
- Claim boundary language.

Deferred, not removed:
- License.
- Release hygiene audit.
- Later README refresh in a separate scoped branch.

Final validation:
- python3 -m unittest discover -s tests -v
- bash scripts/run_agent_black_box_e2e.sh

Final status:
- backfilled from merged historical phase
