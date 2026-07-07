# AAPP Evidence Vault Protocol v0.5

## Purpose

The AAPP Evidence Vault Protocol defines how evidence bundles are stored, separated, redacted, retained, and prepared for responsible disclosure.

This document belongs to Layer 0: operating discipline for authorized research and evidence handling.

It is not a claim of production cryptographic assurance, post-quantum security, government affiliation, Qubes certification, or regulatory compliance.

## Non-negotiable boundaries

- Authorized research only.
- No live target scanning without written scope.
- No exploit instructions in public artifacts.
- No phishing.
- No credential theft.
- No persistence.
- No evasion.
- No covering tracks.
- No raw secrets in reports.
- No public disclosure before the disclosure window is satisfied.

## Vault layout

AAPP-EVIDENCE-VAULT/
  README.md
  00-INBOX/
  01-SCOPE/
  02-TRACE/
  03-BUNDLES/
  04-REDACTION/
  05-DISCLOSURE/
  06-PUBLISHABLE/
  07-KEYS-REFERENCES-ONLY/
  08-AUDIT-LOG/

## Compartment rules

### 00-INBOX

Temporary intake area.

Allowed:
- raw notes
- temporary screenshots
- temporary logs
- incoming maintainer messages

Required action:
- triage into the correct compartment
- delete or move after triage

Forbidden:
- long-term secret storage
- public-ready reports

### 01-SCOPE

Stores written authorization and scope definitions.

Allowed:
- scope JSON
- authorization notes
- permitted targets
- permitted tool types
- disclosure contacts

Forbidden:
- exploit payloads
- credentials

### 02-TRACE

Stores AAPP trace files.

Allowed:
- trace.jsonl
- verification output
- hash-chain evidence

Forbidden:
- raw secrets
- unrelated logs

### 03-BUNDLES

Stores created AAPP evidence bundles.

Allowed:
- AAPP-EVIDENCE-BUNDLE directories
- evidence.bundle.json
- hashes.txt
- verification_result.md

Forbidden:
- unredacted vulnerability reports
- private keys

### 04-REDACTION

Stores redaction work products.

Allowed:
- redaction notes
- before/after field lists
- sanitized excerpts

Forbidden:
- raw secret values in final redaction notes

### 05-DISCLOSURE

Stores private disclosure material.

Allowed:
- maintainer report draft
- disclosure timeline
- embargo plan
- contact records

Forbidden:
- coercion language
- extortion language
- public release instructions before patch window

### 06-PUBLISHABLE

Stores public-safe material only.

Allowed:
- sanitized demo bundle
- public README
- public-safe screenshots
- limitation notes

Forbidden:
- secrets
- exploit weaponization
- live target identifiers unless permitted
- unsupported claims

### 07-KEYS-REFERENCES-ONLY

Stores references to keys, not private keys.

Allowed:
- public key fingerprint
- signing key ID
- rotation notes

Forbidden:
- private keys
- dev.key from evidence demos
- API tokens

### 08-AUDIT-LOG

Stores human-readable vault actions.

Allowed:
- action log
- movement log
- deletion log
- disclosure send log

Required:
- append-only style entries
- timestamp
- actor
- action
- reason

## Required vault files

- README.md
- 01-SCOPE/scope.json
- 03-BUNDLES/AAPP-EVIDENCE-BUNDLE/evidence.bundle.json
- 03-BUNDLES/AAPP-EVIDENCE-BUNDLE/hashes.txt
- 03-BUNDLES/AAPP-EVIDENCE-BUNDLE/verification_result.md
- 04-REDACTION/redaction-log.md
- 05-DISCLOSURE/disclosure-timeline.md
- 08-AUDIT-LOG/vault-audit-log.md

## Evidence intake workflow

1. Confirm written authorization.
2. Create or verify scope JSON.
3. Record action trace with AAPP.
4. Verify trace.
5. Create evidence bundle.
6. Scan report for secret-like values.
7. Move bundle into 03-BUNDLES.
8. Write audit-log entry.
9. Prepare private disclosure if a real vulnerability exists.
10. Move only sanitized material into 06-PUBLISHABLE.

## Retention classes

### R0 Temporary

Temporary raw intake.

Default action:
- delete after triage or move into correct compartment

### R1 Working evidence

Trace, scope, reports, screenshots, and notes needed during active work.

Default action:
- keep until disclosure closes

### R2 Disclosure record

Private disclosure report, timeline, maintainer response, and verification evidence.

Default action:
- retain for audit and dispute resolution

### R3 Public-safe archive

Sanitized public demo, limitations, and references.

Default action:
- may publish after review

## Redaction gate

Before anything moves to 06-PUBLISHABLE:

- scan for secret-like values
- remove raw credentials
- remove private tokens
- remove private keys
- remove bystander data
- remove unrelated personal data
- replace sensitive hostnames if not authorized
- verify that report contains only digest-level evidence when needed

## Disclosure gate

Before contacting a maintainer:

- confirm scope
- confirm vulnerability is reproducible inside authorized boundary
- confirm report does not include weaponization
- confirm redaction checklist complete
- confirm timeline and contact path
- confirm no public post is scheduled before patch window

## Public claim restrictions

Do not claim:

- post-quantum secure
- Qubes-certified
- government-grade
- does not claim military-grade
- unbreakable
- compliance is not guaranteed
- AI safety solved

Allowed wording:

- local reference implementation
- tamper-evident evidence bundle
- dev-only HMAC signature where applicable
- scope-gated trace verification
- evidence vault operating protocol
- PQC-ready profile only when clearly marked as not PQC-secure
