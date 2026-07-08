# AAPP Phase Manifest Standard

Every AAPP phase must have a tracked phase manifest.

Required location:

`docs/phase-notes/Bxx_SCOPE.md`

This standard exists to prevent scope drift, missing files, stale roadmap language, unsupported claims, and phase handoff ambiguity.

## Required Template

Every new phase manifest must include the following exact headings.

Historical B0-B27 backfill records may remain legacy records, but all new phase work should follow this template.

## 1. Phase Name & ID

State the canonical phase ID and phase name.

Example:

`B27C - Developer Distribution Gate`

## 2. Objective / Goal

State the business and technical goal of the phase in 1-2 clear sentences.

## 3. Problem Statement

Explain why this phase is necessary and what failure mode it prevents.

## 4. Scope

Define the boundary of the phase.

### In Scope

List exactly what this phase includes.

### Out of Scope / Non-Goals

List what this phase intentionally does not include.

### Future Considerations

List related work that is deferred to later phases.

## 5. Metrics

Define how completion and quality are measured.

### Completion Metrics / Definition of Done

State the minimum measurable requirements for completion.

### Quality & Safety Metrics

State safety, correctness, regression, and claim-boundary metrics.

### Adoption / Usability Metrics

State adoption or usability metrics when applicable. If not applicable, say why.

### Performance / Scale Metrics

State performance or scale metrics when relevant. If not applicable, say why.

## 6. Deliverables

List concrete artifacts.

### Required Files

List exact required file paths.

### Code Artifacts

List production code artifacts, or state that there are no runtime code artifacts.

### Documentation

List documentation artifacts.

### Machine-Readable Outputs

List JSON, JSONL, SARIF, reports, receipts, or CI outputs when applicable.

## 7. Dependencies & Prerequisites

List phases, tools, repo state, or design decisions that must exist before this phase starts.

## 8. Key Design Decisions

Document major design choices, trade-offs, and why one option was chosen over another.

## 9. Validation Strategy

Define how the phase is checked.

### Automated Validation

List automated commands, tests, and CI checks.

### Manual Validation

List human review checks.

### Scenario Validation

List realistic scenarios that must pass.

### Review Process

State who reviews, what evidence is reviewed, and what blocks merge.

## 10. Risks & Mitigations

List key risks and how each risk is reduced.

## 11. Kill Conditions

State the conditions that immediately stop, rollback, or block the phase.

## 12. Success Criteria

State what success looks like after the phase is complete.

## 13. Transition to Next Phase

State the criteria, artifacts, validation state, and handoff conditions required before the next phase can start.

## 14. Timeline & Owner

State owner and expected execution window.

For solo execution:

Owner: human executor.  
Timeline: single product-gate PR.

## Final Phase Record

After merge, the final record is the merged PR, CI result, post-merge validation, and main branch commit.

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
- Do not claim FedRAMP authorization.
- Do not claim FIPS validation.
- Do not claim CISA approval.
- Do not claim DoD, NASA, or Microsoft certification.
- Do not claim full containment.
- Do not claim impossible-to-bypass security.
- Do not claim compliance guarantee.

## Scope of This Backfill

B27A backfilled historical phase manifests.

B27B enforces repo governance through templates, required-file checks, phase-manifest checks, and claim-boundary checks.

B27B must not rewrite runtime modules, fixtures, tests, or B28 implementation.
