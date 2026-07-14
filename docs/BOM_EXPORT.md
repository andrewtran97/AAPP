# B47 — SBOM / CBOM / AI-BOM Export

## Status

`REFERENCE`

Local deterministic output-shape adapter only.

No live inventory discovery, completeness guarantee, standards certification,
external validation, signing, publication, network, or subprocess execution.

## Purpose

Convert one supplied inventory into one deterministic BOM-shaped result.

Supported formats:

- `CYCLONEDX_JSON`
- `SPDX_JSON`

Reference profiles:

- CycloneDX JSON 1.6-shaped output
- SPDX JSON 2.3-shaped output

These outputs are shape-aligned reference records, not claims of full schema
conformance.

## Request Contract

Required fields:

- `schema_version`
- `request_id`
- `output_format`
- `inventory`
- `source_evidence_digest`

The request must be a JSON object.

Unknown output formats fail closed.

## Inventory Contract

The inventory may contain:

- `components`
- `dependencies`
- `cryptographic_assets`
- `models`
- `datasets`
- `runtimes`
- `services`
- `provenance_refs`
- `evidence_refs`

Every supplied object requires a stable identifier.

Components require:

- `id`
- `name`
- `version`
- `type`
- `license`

Dependencies require:

- `from`
- `to`

No repository, package manager, filesystem, or network discovery occurs.

## Deterministic Evaluation Order

1. Validate request object and schema version.
2. Validate output format.
3. Validate required inventory collections.
4. Validate object identities and field types.
5. Reject duplicate identities.
6. Evaluate license status.
7. Evaluate provenance references.
8. Render the selected output shape.
9. Calculate the canonical BOM digest.
10. Return the deterministic result.

Identical inputs must produce identical results.

Input objects must not be mutated.

## Verdicts

### `EXPORTED`

The request, inventory, format, licenses, and provenance checks passed.

### `INCOMPLETE`

Required inventory data is missing or empty.

### `LICENSE_UNKNOWN`

At least one required component has no usable license value.

### `PROVENANCE_MISSING`

Required provenance references are absent.

### `MALFORMED`

The request or inventory has an invalid structure or field type.

### `UNSUPPORTED_FORMAT`

The requested output format is not supported.

## CycloneDX JSON-Shaped Output

The reference object contains:

- `bomFormat`
- `specVersion`
- `version`
- `metadata`
- `components`
- `dependencies`
- `services`
- `properties`

Cryptographic assets, models, datasets, provenance references, and evidence
references remain visible through bounded component or property records.

No random serial number or implicit timestamp is generated.

## SPDX JSON-Shaped Output

The reference object contains:

- `spdxVersion`
- `dataLicense`
- `SPDXID`
- `name`
- `documentNamespace`
- `creationInfo`
- `packages`
- `relationships`
- `externalDocumentRefs`
- `annotations`

Identifiers and namespace values must derive from supplied input.

No implicit timestamp or generated identifier is allowed.

## Result Contract

The result contains:

- `schema_version`
- `request_id`
- `output_format`
- `verdict`
- `reason_codes`
- `checks`
- `bom`
- `bom_digest`
- `source_evidence_digest`

`bom` and `bom_digest` are present only when the verdict is `EXPORTED`.

The digest is SHA-256 over canonical JSON bytes of the rendered BOM object.

## Failure Semantics

- Missing inventory never becomes `EXPORTED`.
- Unsupported format never becomes `EXPORTED`.
- Unknown license data is not silently discarded.
- Missing provenance is not silently discarded.
- Malformed input does not produce a BOM.
- Failure does not trigger external operations.

## Security and Claim Boundary

B47 proves only that supplied input was evaluated and rendered by the local
deterministic reference contract.

It does not prove:

- inventory completeness;
- source-code completeness;
- vulnerability absence;
- license compliance;
- provenance authenticity;
- standards conformance;
- production deployment readiness.

## Non-Goals

- No live scanner.
- No filesystem or repository scan.
- No package-manager invocation.
- No network.
- No subprocess.
- No external service.
- No signing or transparency submission.
- No production BOM claim.
- No compliance or certification claim.
- No new dependency.
- No B48 implementation.
