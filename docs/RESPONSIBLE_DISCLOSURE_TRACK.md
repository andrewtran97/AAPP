# AAPP Responsible Disclosure Track v1.0

## Purpose

This track defines how AAPP evidence is prepared for private responsible disclosure when authorized research identifies a real vulnerability.

AAPP does not publish exploit weaponization. AAPP produces scoped, redacted, tamper-evident evidence.

## Rules

- Written scope required.
- Private disclosure before public release.
- No coercion.
- No extortion.
- No exploit weaponization.
- No raw secrets.
- No persistence instructions.
- No evasion instructions.
- No live target details in public material unless explicitly authorized.
- Public release requires redaction gate and disclosure gate.

## Disclosure flow

1. Confirm scope.
2. Verify AAPP trace.
3. Create evidence bundle.
4. Create replay report.
5. Redact sensitive details.
6. Prepare private maintainer report.
7. Send private disclosure.
8. Track acknowledgement.
9. Track fix/patch window.
10. Retest only inside scope.
11. Prepare public-safe summary after gate approval.

## Required artifacts

- vulnerability_report_private.md
- disclosure_email.md
- disclosure_timeline.md
- embargo_checklist.md
- publication_checklist.md
- redaction_log.md
- replay_report.md
- evidence.bundle.json

## Kill conditions

Stop if:

- no written scope
- exploit instructions are required to explain impact
- report contains raw secrets
- report contains private keys
- publication occurs before disclosure gate
- maintainer contact path is unknown
- legal authorization is ambiguous
