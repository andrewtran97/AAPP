# Tamper-Evident Evidence Vault

## Purpose

The evidence vault stores vulnerability reports, AAPP traces, signed manifests, hashes, and disclosure timelines.

## Evidence bundle layout

VULN-EVIDENCE-BUNDLE/
- report.md
- threat_model.md
- affected_versions.md
- reproduction_steps.md
- crash_or_trace.log
- patch_or_mitigation.md
- hashes.txt
- signature.asc
- disclosure_timeline.md

## AAPP bundle layout

AAPP-EVIDENCE-BUNDLE/
- scope.yaml
- trace.jsonl
- evidence.bundle.json
- evidence.report.md
- hashes.txt
- signature.asc
- verification_result.md

## Storage rules

Encrypt evidence at rest.

Keep signing keys separate from research environments.

Do not store raw secrets in reports.

Use redaction before publishing.

Use signed manifests for integrity.

Maintain disclosure timeline for every report.
