# B47 — SBOM / CBOM / AI-BOM Export

## 1. Phase Name & ID

- Phase: `B47`
- Name: SBOM / CBOM / AI-BOM Export
- Authorization issue: `#128`
- Starting commit: `b911e0e5ca6c0366058cfc6e98d97b3eb32f4993`
- Status: `ACTIVE`
- Classification: `REFERENCE`

B47 defines one local deterministic BOM export contract.
It does not scan repositories or claim complete, certified, or production BOM coverage.

## 2. Objective / Goal

Convert one validated inventory request into deterministic CycloneDX JSON-shaped
or SPDX JSON-shaped output while preserving declared software, dependencies,
cryptographic assets, models, dataset references, runtimes, services, licenses,
provenance references, and evidence references.

## 3. Problem Statement

AAPP has a deterministic provenance reference but no bounded BOM export contract.

Without a fixed contract, later integrations could silently discard unknown
licenses, omit missing provenance, accept unsupported formats, mutate inputs,
or represent partial synthetic inventory as a complete production BOM.

## 4. Scope

### In Scope

- One BOM export request schema.
- One bounded inventory schema.
- `CYCLONEDX_JSON` output shape.
- `SPDX_JSON` output shape.
- Software component and dependency records.
- Cryptographic asset records.
- Model and dataset-reference records.
- Runtime and service records.
- License, provenance, and evidence-reference preservation.
- Canonical JSON encoding and SHA-256 BOM digest.
- Deterministic verdicts, reason codes, and checks.
- One fixture, focused tests, and phase documentation.

Supported verdicts:

- `EXPORTED`
- `INCOMPLETE`
- `LICENSE_UNKNOWN`
- `PROVENANCE_MISSING`
- `MALFORMED`
- `UNSUPPORTED_FORMAT`

### Threat Model

B47 must reject or classify:

- Missing required request or inventory fields.
- Invalid field types.
- Unsupported output formats.
- Empty required inventory.
- Duplicate or malformed component identities.
- Unknown license data hidden from the result.
- Missing provenance hidden from the result.
- Input mutation.
- Non-deterministic output for identical input.
- Synthetic fixture data represented as a complete production BOM.
- Scope expansion into scanning, signing, external services, or B48.

### Out of Scope / Non-Goals

- No live package or dependency scanner.
- No filesystem or repository scan.
- No package-manager invocation.
- No network.
- No subprocess.
- No external service.
- No signing or transparency submission.
- No completeness guarantee.
- No standards-validation guarantee.
- No compliance or certification claim.
- No new dependency.
- No B48 implementation.

### Future Considerations

Live inventory discovery, external standards validators, signing, release
submission, and customer deployment require separately authorized phases and
measured integration demand.

## 5. Metrics

### Completion Metrics / Definition of Done

- Exactly five authorized files.
- Both supported output formats have deterministic coverage.
- Every supported verdict has focused test coverage.
- Focused and full tests pass.
- Repository guards, product E2E, CI, and post-merge validation pass.

### Quality & Safety Metrics

- Unsupported formats never produce `EXPORTED`.
- Missing required inventory never produces `EXPORTED`.
- Unknown license data remains visible.
- Missing provenance remains visible.
- Identical input produces identical output.
- Input objects are not mutated.
- No network or subprocess import.

### Adoption / Usability Metrics

- One documented Python call path.
- One request shape.
- One inventory shape.
- One result shape.
- Reason codes identify the deterministic failure boundary.

### Performance / Scale Metrics

B47 evaluates one bounded in-memory inventory request.

No production throughput, completeness, or inventory-scale claim is made.

## 6. Deliverables

### Required Files

- `docs/phase-notes/B47_SCOPE.md`
- `docs/BOM_EXPORT.md`
- `aapp/bom_export.py`
- `tests/fixtures/bom_export/sample_inventory.json`
- `tests/test_bom_export.py`

No other repository file is authorized.

### Code Artifacts

The BOM export module owns schema validation, canonical encoding, deterministic
format selection, field preservation, verdict selection, BOM digest calculation,
and result creation.

### Documentation

The BOM export document will define request, inventory, component, dependency,
license, provenance, evidence-reference, output, and result contracts.

### Machine-Readable Outputs

The result must contain:

- schema version;
- request ID;
- output format;
- rendered BOM object when eligible;
- deterministic BOM digest when eligible;
- verdict;
- reason codes;
- deterministic checks;
- preserved provenance and evidence references.

No implicit wall-clock timestamp or generated identifier is allowed.

## 7. Dependencies & Prerequisites

- B46 accepted on main.
- Issue `#128` open with `B47_AUTHORIZATION_MARKER_V1`.
- Starting commit `b911e0e5ca6c0366058cfc6e98d97b3eb32f4993`.
- Python standard library only.
- Existing canonical JSON, digest, and provenance conventions.
- No new package, network, subprocess, scanner, or service dependency.

## 8. Key Design Decisions

1. The exporter transforms only inventory supplied in the request.
2. It does not discover packages, files, models, or services.
3. Output format is an exact supported enumeration.
4. Input list order is preserved.
5. Object keys use canonical deterministic ordering.
6. Unknown license data produces `LICENSE_UNKNOWN`.
7. Missing provenance produces `PROVENANCE_MISSING`.
8. Unsupported formats fail closed.
9. Malformed inventory cannot produce an output BOM.
10. Identical inputs produce identical outputs.
11. Input objects are never mutated.
12. Output is shape-aligned only and is not certification.

Evaluation order:

1. Object, schema, required-field, and type validation.
2. Supported-format validation.
3. Required inventory validation.
4. Component and dependency identity validation.
5. License evaluation.
6. Provenance evaluation.
7. Format-specific rendering.
8. Canonical BOM digest calculation.
9. `EXPORTED` only after every required check passes.

## 9. Validation Strategy

### Automated Validation

Run from repository root:

- `python3 -m unittest discover -s tests -p test_bom_export.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 scripts/check_phase_manifest.py`
- `python3 scripts/check_claim_boundaries.py`
- `python3 scripts/check_required_files.py` after all five files exist.
- `git diff --check`
- `bash scripts/run_agent_black_box_e2e.sh /tmp/aapp-b47-e2e`

### Manual Validation

- Confirm exactly five changed files.
- Confirm no new dependency.
- Confirm no scanner, network, subprocess, signing, or external service.
- Confirm fixtures contain synthetic data only.
- Confirm documentation makes no completeness or certification claim.
- Confirm no B48 content.

### Scenario Validation

- Valid CycloneDX JSON-shaped export.
- Valid SPDX JSON-shaped export.
- Missing required inventory.
- Unknown license.
- Missing provenance.
- Malformed request or inventory.
- Unsupported output format.
- Duplicate component identity.
- Deterministic repeated result.
- Input non-mutation.

### Review Process

- Human executor performs terminal operations and merge decision.
- Implementation role changes only the five authorized files.
- Automated reviewer runs focused tests, full tests, and repository guards.
- Exact dirty-file and staged-file guards are required.
- PR uses `Refs #128`.
- CI, squash merge, main synchronization, and post-merge validation are required.
- One acceptance record is required before issue closure.

## 10. Risks & Mitigations

- Partial inventory presented as complete: preserve `REFERENCE` labeling.
- Unknown license hidden: produce `LICENSE_UNKNOWN`.
- Missing provenance hidden: produce `PROVENANCE_MISSING`.
- Unsupported format accepted: fail closed.
- Nondeterminism: prohibit implicit time and generated identifiers.
- Input mutation: copy or read input without modifying it.
- Standards overclaim: describe outputs as JSON-shaped reference records.
- Scope drift: exact five-file allowlist and B48 prohibition.

## 11. Kill Conditions

Stop when:

- A sixth repository file changes.
- The phase manifest or issue authorization becomes ambiguous.
- Scanner execution, network, subprocess, signing, external service, or a dependency appears.
- Unsupported format can become `EXPORTED`.
- Missing inventory can become `EXPORTED`.
- Unknown license or missing provenance is silently discarded.
- Output depends on implicit wall-clock time or a generated identifier.
- Input objects are mutated.
- Fixture data is represented as a complete production BOM.
- B48 work enters the diff.
- Focused tests, full tests, guards, E2E, CI, or post-merge validation fail.

## 12. Success Criteria

B47 succeeds only after exactly five authorized files are accepted, both output
formats and all deterministic failure scenarios pass, CI passes, the PR is
squash-merged, main is post-merge validated, and issue `#128` closes as
completed with exactly one acceptance record.

## 13. Transition to Next Phase

B47 does not authorize B48.

B48 requires a new authorization issue, exact manifest, accepted starting-main
validation, and a separate open-source security posture contract.

## 14. Timeline & Owner

- Owner: repository maintainer.
- Human executor: terminal execution and merge decision.
- Implementation role: exact authorized file changes only.
- Automated reviewer: focused tests, full suite, guards, E2E, and CI.
- Final record: merged PR, CI result, post-merge validation, acceptance record, and main commit.
- Execution: one issue, one branch, and one exact file manifest.
- Current next action: create BOM export documentation only after this scope file passes validation.
