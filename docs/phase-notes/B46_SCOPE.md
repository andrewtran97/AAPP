# B46 — Supply-Chain Provenance

## 1. Phase Name & ID

- Phase: `B46`
- Name: Supply-Chain Provenance
- Authorization issue: `#126`
- Starting commit: `539f5925597f76663ca387a5b6e2e65d70cfa493`
- Status: `ACTIVE`
- Classification: `REFERENCE`

B46 defines one local deterministic provenance statement and verifier contract.
It does not implement a live build service, signing service, transparency log, or certification.

## 2. Objective / Goal

Convert one validated build input into a deterministic provenance result that binds
source repository, source commit, builder identity, workflow identity, materials,
artifact identity, artifact digest, timestamps, and source evidence digest.

## 3. Problem Statement

AAPP has evidence, attestation, identity, and policy reference controls, but it does
not yet have one bounded supply-chain provenance contract.

Without a fixed contract, later build and release integrations could accept missing
materials, substituted source or artifact identities, untrusted builders, unsupported
schemas, or claims that exceed the local reference implementation.

## 4. Scope

### In Scope

- One provenance request schema and one build record schema.
- Canonical JSON encoding and SHA-256 digest verification.
- Source repository and source commit binding.
- Builder identity and workflow identity binding.
- Ordered material records with identity and digest fields.
- Artifact identity and artifact digest binding.
- Request-provided timestamps.
- Source evidence digest preservation.
- Deterministic verdicts and reason codes.
- One fixture, focused tests, and phase documentation.

Supported verdicts:

- `VERIFIED`
- `INCOMPLETE`
- `DIGEST_MISMATCH`
- `SOURCE_MISMATCH`
- `BUILDER_UNTRUSTED`
- `MALFORMED`
- `UNSUPPORTED`

### Threat Model

B46 must reject or classify:

- Missing required fields and invalid field types.
- Unsupported schema versions.
- Artifact digest substitution.
- Source repository substitution.
- Source commit substitution.
- Builder identity marked untrusted.
- Workflow identity substitution.
- Material omission, duplication, or digest substitution.
- Source evidence digest omission or tampering.
- Non-deterministic output for identical input.
- Fixture data represented as production provenance proof.
- Scope expansion into signing, publishing, B47, or external services.

### Out of Scope / Non-Goals

- No live build service.
- No build execution.
- No Sigstore or Rekor call.
- No signing or transparency submission.
- No network.
- No subprocess.
- No external service.
- No artifact publishing.
- No SLSA compliance or certification claim.
- No production build enforcement.
- No new dependency.
- No B47 BOM implementation.

### Future Considerations

Live builders, external attestations, signing, transparency logs, and release
publication require separately authorized phases, pinned provider contracts,
key-management controls, and demonstrated integration demand.

## 5. Metrics

### Completion Metrics / Definition of Done

- Exactly five authorized files.
- Every supported verdict has deterministic coverage.
- Valid, malformed, incomplete, mismatch, and untrusted scenarios are covered.
- Focused and full tests pass.
- Repository guards, product E2E, CI, and post-merge validation pass.

### Quality & Safety Metrics

- No missing required field produces `VERIFIED`.
- No source, artifact, workflow, material, or evidence mismatch produces `VERIFIED`.
- Unsupported schemas never produce success.
- Untrusted builders never produce `VERIFIED`.
- Source evidence digest is preserved in the result.
- Identical input produces identical output.
- No network or subprocess import.

### Adoption / Usability Metrics

- One documented Python call path.
- One request shape.
- One build record shape.
- One result shape.
- Reason codes identify the first deterministic failure boundary.

### Performance / Scale Metrics

B46 evaluates one bounded in-memory request and build record.
No production throughput, build-scale, or latency claim is made.

## 6. Deliverables

### Required Files

- `docs/phase-notes/B46_SCOPE.md`
- `docs/SUPPLY_CHAIN_PROVENANCE.md`
- `aapp/supply_chain_provenance.py`
- `tests/fixtures/supply_chain_provenance/sample_build.json`
- `tests/test_supply_chain_provenance.py`

No other repository file is authorized.

### Code Artifacts

The provenance module owns canonical encoding, digest calculation, schema
validation, deterministic binding checks, verdict selection, and result creation.

### Documentation

The provenance document will define request, build, material, artifact, and result
schemas, evaluation order, verdict meanings, usage, evidence expectations, and
claim boundaries.

### Machine-Readable Outputs

The result must contain schema version, request ID, source repository, source commit,
builder identity, workflow identity, material count, artifact identity, artifact
digest, source evidence digest, verdict, reason codes, and deterministic checks.

No implicit wall-clock timestamp or generated identifier is allowed.

## 7. Dependencies & Prerequisites

- B45 accepted on main.
- Issue `#126` open with `B46_AUTHORIZATION_MARKER_V1`.
- Starting commit `539f5925597f76663ca387a5b6e2e65d70cfa493`.
- Python standard library only.
- Existing evidence, identity, attestation, and digest conventions.
- No new package, network, subprocess, or service dependency.

## 8. Key Design Decisions

1. Request and build record remain separate objects.
2. Identical inputs produce identical outputs.
3. Time values are provided by the request and build record.
4. Canonical digests exclude the digest field that stores the result.
5. Source repository and source commit are exact string bindings.
6. Builder trust must be an exact JSON boolean.
7. Boolean values are not accepted as integers.
8. Materials are ordered and each material requires identity and SHA-256 digest.
9. Evaluation is fail-closed.
10. Source evidence digest is preserved.
11. Fixture data is not production provenance proof.
12. SLSA language is mapping guidance, not certification.

Evaluation order:

1. Object, schema, required-field, and type validation.
2. Supported-schema validation.
3. Canonical provenance digest validation.
4. Source repository and source commit checks.
5. Builder trust and builder identity checks.
6. Workflow identity check.
7. Material completeness and digest checks.
8. Artifact identity and artifact digest checks.
9. Source evidence digest preservation.
10. `VERIFIED` only after every check passes.

## 9. Validation Strategy

### Automated Validation

Run from repository root:

- `python3 -m unittest discover -s tests -p test_supply_chain_provenance.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 scripts/check_phase_manifest.py`
- `AAPP_STRICT_PHASE_MANIFEST=1 python3 scripts/check_phase_manifest.py`
- `python3 scripts/check_claim_boundaries.py`
- `python3 scripts/check_required_files.py` after all five deliverables exist.
- `git diff --check`
- `bash scripts/run_agent_black_box_e2e.sh /tmp/aapp-b46-e2e`

### Manual Validation

- Confirm exactly five changed files.
- Confirm no new dependency.
- Confirm no network, subprocess, signing, or external-service behavior.
- Confirm no secret-like or customer-derived fixture material.
- Confirm no B47 content.
- Confirm documentation does not claim certification or production enforcement.

### Scenario Validation

- Valid provenance statement.
- Missing required field.
- Unsupported request or build schema.
- Artifact digest mismatch.
- Source repository mismatch.
- Source commit mismatch.
- Untrusted builder.
- Workflow identity mismatch.
- Missing or altered material.
- Source evidence digest preservation.
- Malformed input.
- Repeated deterministic result.

### Review Process

- Human executor performs terminal operations and merge decision.
- Implementation role changes only the five authorized files.
- Automated reviewer runs deterministic tests and repository guards.
- Exact dirty-file and staged-file guards are required.
- PR uses `Refs #126`.
- CI, squash merge, main synchronization, and post-merge validation are required.
- One acceptance record is required before issue closure.

## 10. Risks & Mitigations

- Fixture mistaken for production proof: enforce `REFERENCE` labeling.
- Source substitution: compare exact repository and commit bindings.
- Artifact substitution: verify canonical artifact digest.
- Builder spoofing: require exact builder identity and trust boolean.
- Material omission: require an ordered non-empty material list.
- Digest recursion: exclude each stored digest field from its digest input.
- Nondeterminism: prohibit implicit time and generated identifiers.
- SLSA overclaim: state mapping only and no certification claim.
- Scope drift: exact five-file allowlist and B47 prohibition.

## 11. Kill Conditions

Stop when:

- A sixth repository file changes.
- The phase manifest or issue authorization becomes ambiguous.
- Network, subprocess, signing, external service, publishing, or a dependency appears.
- A missing field or mismatch can become `VERIFIED`.
- An untrusted builder can become `VERIFIED`.
- Source evidence digest is not preserved.
- Output depends on implicit wall-clock time or a generated identifier.
- Fixture data is represented as production proof.
- B47 work enters the diff.
- Focused tests, full tests, repository guards, E2E, CI, or post-merge validation fail.

## 12. Success Criteria

B46 succeeds only after exactly five authorized files are accepted, all deterministic
scenarios pass, CI passes, the PR is squash-merged, main is post-merge validated,
and issue `#126` closes as completed with exactly one acceptance record.

## 13. Transition to Next Phase

B46 does not authorize B47.

B47 requires a new issue, exact manifest, fresh starting-main validation, and a
separate decision on CycloneDX or SPDX output boundaries.

## 14. Timeline & Owner

- Owner: repository maintainer.
- Human executor: terminal execution and merge decision.
- Implementation role: exact authorized file changes only.
- Automated reviewer: focused tests, full suite, guards, E2E, and CI.
- Final record: merged PR, CI result, post-merge validation, acceptance record, and main commit.
- Execution: one issue, one branch, and one exact file manifest.
- Current next action: create the provenance documentation only after this scope file passes validation.
