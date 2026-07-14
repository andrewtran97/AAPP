# B46 — Supply-Chain Provenance

## Status

- Phase: `B46`
- Authorization issue: `#126`
- Status: `REFERENCE`
- Runtime: local deterministic Python contract
- External services: none

This document defines the B46 local provenance contract. It is not a production build service, signed attestation, transparency-log submission, SLSA certification, or release publication mechanism.

## Purpose

B46 binds one expected provenance request to one build record and returns a deterministic verdict.

The contract answers:

- Which source repository and commit produced the artifact?
- Which builder and workflow produced it?
- Which ordered materials were declared?
- Which artifact identity and digest were produced?
- Which source evidence digest supports the record?
- Did the record match the expected bindings?

## Standards Mapping

SLSA provenance describes verifiable information about where, when, and how an artifact was produced.

B46 maps local fields to that model:

- `artifact` maps to an attestation subject.
- `artifact.digest` maps to the subject digest.
- `source` maps to canonical source identity.
- `builder.id` maps to builder identity.
- `workflow.id` maps to the build workflow identity.
- `materials` maps to resolved build inputs.
- `source_evidence_digest` preserves the upstream evidence reference.

The mapping is descriptive only. B46 does not emit a signed in-toto envelope and does not claim a SLSA Build level.

## Supported Schemas

- Request: `aapp.supply_chain_provenance_request.v1`
- Build record: `aapp.supply_chain_provenance_build.v1`
- Result: `aapp.supply_chain_provenance_result.v1`

Unknown schema versions return `UNSUPPORTED`.

## Request Schema

```json
{
  "schema_version": "aapp.supply_chain_provenance_request.v1",
  "request_id": "request-001",
  "expected_source": {
    "repository": "https://example.invalid/org/repo",
    "commit": "0123456789abcdef0123456789abcdef01234567"
  },
  "expected_builder": {
    "id": "builder:local:v1"
  },
  "expected_workflow": {
    "id": "workflow:reference-build:v1"
  },
  "expected_materials": [
    {
      "uri": "git+https://example.invalid/org/repo@0123456789abcdef0123456789abcdef01234567",
      "digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
  ],
  "expected_artifact": {
    "name": "dist/example.tar.gz",
    "digest": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "expected_source_evidence_digest": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
}
```

## Build Record Schema

```json
{
  "schema_version": "aapp.supply_chain_provenance_build.v1",
  "source": {
    "repository": "https://example.invalid/org/repo",
    "commit": "0123456789abcdef0123456789abcdef01234567"
  },
  "builder": {
    "id": "builder:local:v1",
    "trusted": true
  },
  "workflow": {
    "id": "workflow:reference-build:v1"
  },
  "materials": [
    {
      "uri": "git+https://example.invalid/org/repo@0123456789abcdef0123456789abcdef01234567",
      "digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
  ],
  "artifact": {
    "name": "dist/example.tar.gz",
    "digest": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "started_at": "2026-07-13T12:00:00Z",
  "finished_at": "2026-07-13T12:00:01Z",
  "source_evidence_digest": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "provenance_digest": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
}
```

`trusted` must be a JSON boolean. Boolean values are not accepted where integers are required.

## Canonical Provenance Digest

The canonical digest is SHA-256 over the UTF-8 bytes of the build record encoded as canonical JSON with:

- keys sorted;
- separators `,` and `:`;
- no insignificant whitespace;
- `ensure_ascii=false`;
- `provenance_digest` excluded from the digest input.

The stored value uses `sha256:<64 lowercase hexadecimal characters>`.

The digest proves byte-level consistency of the local record. It does not prove that the builder, source, artifact, or timestamps are truthful.

## Result Schema

```json
{
  "schema_version": "aapp.supply_chain_provenance_result.v1",
  "request_id": "request-001",
  "verdict": "VERIFIED",
  "reason_codes": [
    "ALL_CHECKS_PASSED"
  ],
  "source_repository": "https://example.invalid/org/repo",
  "source_commit": "0123456789abcdef0123456789abcdef01234567",
  "builder_id": "builder:local:v1",
  "workflow_id": "workflow:reference-build:v1",
  "material_count": 1,
  "artifact_name": "dist/example.tar.gz",
  "artifact_digest": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "source_evidence_digest": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "checks": {
    "schemas_supported": true,
    "provenance_digest_matches": true,
    "source_matches": true,
    "builder_trusted": true,
    "builder_matches": true,
    "workflow_matches": true,
    "materials_match": true,
    "artifact_matches": true,
    "source_evidence_digest_matches": true
  }
}
```

No result field is generated from implicit wall-clock time. The request ID is copied from the request.

## Deterministic Evaluation Order

1. Validate that request and build record are objects.
2. Validate required fields and exact field types.
3. Validate supported schema versions.
4. Recompute and compare `provenance_digest`.
5. Compare source repository and source commit.
6. Require `builder.trusted` to be `true`.
7. Compare builder identity.
8. Compare workflow identity.
9. Compare the ordered material list.
10. Compare artifact name and artifact digest.
11. Compare and preserve the source evidence digest.
12. Return `VERIFIED` only when every check passes.

The first failed boundary determines the verdict and primary reason code.

## Verdicts

- `VERIFIED`: every required check passed.
- `INCOMPLETE`: a required field is absent or an expected list is empty.
- `DIGEST_MISMATCH`: provenance, material, artifact, workflow-bound, or evidence digest data does not match.
- `SOURCE_MISMATCH`: source repository or source commit does not match.
- `BUILDER_UNTRUSTED`: builder trust is false or builder identity does not match.
- `MALFORMED`: an input is not an object, a field has the wrong type, a digest is malformed, or a timestamp is malformed.
- `UNSUPPORTED`: a schema version is not supported.

No mismatch may become `VERIFIED`.

## Checks Object

The `checks` object records deterministic booleans only.

A check that has not been reached remains `false`. The checks object is evidence of evaluator behavior, not proof that external facts are true.

## Local Usage Shape

```python
from aapp.supply_chain_provenance import evaluate_supply_chain_provenance

result = evaluate_supply_chain_provenance(request, build_record)
```

The evaluator must not mutate either input object.

## Failure Semantics

- Missing required data fails closed.
- Unsupported schemas fail closed.
- Digest mismatches fail closed.
- Source mismatches fail closed.
- Untrusted builders fail closed.
- Identical inputs produce identical results.
- Failure never triggers a build, publication, signing operation, network call, or subprocess.

## Security and Claim Boundary

B46 is a local deterministic reference adapter.

It can prove:

- the evaluator received specific structured fields;
- canonical bytes produced a specific digest;
- configured expectations matched or did not match;
- a source evidence digest was preserved;
- a deterministic verdict and reason code were produced.

It cannot prove:

- a real build occurred;
- the builder identity is externally authenticated;
- source code was complete or safe;
- the artifact is vulnerability-free;
- timestamps are externally trustworthy;
- a signature or transparency log exists;
- any SLSA Build level or certification was achieved.

## Non-Goals

- No live build service.
- No build execution.
- No network.
- No subprocess.
- No Sigstore.
- No Rekor.
- No signing.
- No transparency submission.
- No artifact publication.
- No production enforcement.
- No SLSA compliance or certification claim.
- No new dependency.
- No B47 implementation.
