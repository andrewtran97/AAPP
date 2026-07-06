# AAPP Compartmented Research Workstation SOP v0.6

## Purpose

This SOP defines a local operating model for authorized research, evidence handling, redaction, disclosure preparation, and public-safe publication.

This is Layer 0 operating discipline. It is not a claim of Qubes affiliation, Qubes certification, government-grade security, military-grade security, post-quantum security, or compliance certification.

## Operating principle

Separate work by risk and disclosure state.

Do not mix:
- raw intake
- scoped research
- trace generation
- bundle creation
- redaction work
- private disclosure
- public material
- key references

## Workstation compartments

### C0-HOST-BASELINE

Purpose:
- OS updates
- package manager
- Git configuration
- signing configuration
- local hooks

Allowed:
- repo checkout
- Git operations
- signed commits
- signed tags

Forbidden:
- raw secrets
- exploit material
- unredacted reports

### C1-SCOPE-CONTROL

Purpose:
- written authorization
- scope JSON
- permitted actor/tool rules

Allowed:
- scope documents
- scope.demo.json-style files
- authorization notes

Forbidden:
- credentials
- private keys
- raw target data outside written scope

### C2-RESEARCH-SANDBOX

Purpose:
- local-only analysis
- parser tests
- fake target simulation
- non-networked experiments

Allowed:
- local fixtures
- synthetic traces
- local sample files

Forbidden:
- live target scanning
- credential capture
- persistence
- evasion
- covering tracks

### C3-AAPP-TRACE

Purpose:
- AAPP recording and verification

Allowed:
- trace.jsonl
- dev-only signing key for local demo
- verification output

Forbidden:
- production private keys
- raw secrets in records
- unscoped recordings

### C4-EVIDENCE-BUNDLE

Purpose:
- create and verify AAPP evidence bundles

Allowed:
- AAPP-EVIDENCE-BUNDLE
- evidence.bundle.json
- hashes.txt
- verification_result.md

Forbidden:
- unredacted exploit steps
- private keys
- raw credentials

### C5-REDACTION

Purpose:
- sanitize reports and artifacts

Allowed:
- redaction log
- before/after field list
- digest-only excerpts

Forbidden:
- raw secrets in final notes
- public-ready files before checklist pass

### C6-DISCLOSURE

Purpose:
- private maintainer disclosure

Allowed:
- private report
- disclosure timeline
- maintainer contact log
- patch-window notes

Forbidden:
- coercion
- extortion
- public release before disclosure gate

### C7-PUBLISHABLE

Purpose:
- public-safe demo and review pack

Allowed:
- sanitized sample bundle
- limitations document
- demo script
- public README

Forbidden:
- secrets
- live target identifiers unless authorized
- exploit weaponization
- unsupported claims

### C8-KEY-REFERENCE

Purpose:
- reference key IDs and fingerprints only

Allowed:
- public key fingerprint
- signing key ID
- rotation note

Forbidden:
- private keys
- dev.key
- API tokens
- recovery phrases

## Daily operating sequence

1. Start in C0-HOST-BASELINE.
2. Confirm Git branch is not main for feature work.
3. Confirm written scope in C1-SCOPE-CONTROL.
4. Run local-only work in C2-RESEARCH-SANDBOX.
5. Record actions through AAPP in C3-AAPP-TRACE.
6. Verify trace.
7. Create evidence bundle in C4-EVIDENCE-BUNDLE.
8. Redact and scan in C5-REDACTION.
9. Prepare private disclosure in C6-DISCLOSURE if real vulnerability exists.
10. Move only approved material to C7-PUBLISHABLE.
11. Record all movement in vault audit log.

## Network rule

Default: no live target interaction.

Allowed only when:
- written scope exists
- target is explicitly listed
- tool type is authorized
- action is logged
- output is redacted before report

## Evidence rule

No scope, no active recording.

No signed action trail, no trusted agent.

No verified bundle, no disclosure package.

No redaction gate, no public material.

## Key handling rule

Do not store private keys inside the evidence vault or publishable compartments.

Allowed:
- public key reference
- key fingerprint
- signing key ID

Forbidden:
- private key material
- demo dev.key in vault docs
- API tokens
- recovery seeds

## Shutdown checklist

- [ ] Working tree clean or intentional changes reviewed
- [ ] No generated evidence tracked
- [ ] No bytecode tracked
- [ ] No raw secrets in reports
- [ ] Audit log updated
- [ ] Public material separated from private disclosure material
