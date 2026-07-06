# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| `aapp-baseline-v1.1` | Yes |
| Earlier baselines | No, unless needed for historical verification |

## Reporting a vulnerability

Do not report security vulnerabilities in public GitHub issues.

Use GitHub private vulnerability reporting if it is available for this repository. If private vulnerability reporting is not available, open a public issue that asks for the preferred security contact without describing the vulnerability, exploit path, secret, target detail, or reproduction steps.

## What to include

Include only redacted, authorized evidence:

- affected AAPP version or tag
- short impact summary
- scope or authorization boundary
- redacted reproduction summary
- AAPP evidence bundle if available
- replay report if available
- relevant hashes or verification result
- suggested remediation area if known

## What not to include

Do not include:

- raw secrets
- private keys
- access tokens
- live exploit instructions
- persistence steps
- evasion steps
- credential theft material
- bystander data
- third-party target data without written scope

## AAPP evidence bundles

AAPP evidence bundles are acceptable as supporting context only when they are redacted and scoped.

AAPP evidence does not replace maintainer verification. Maintainers must verify impact, scope, affected version, and remediation before creating or publishing a security advisory.

## Advisory handling

A GitHub repository security advisory should only be created for a real vulnerability with reproducible impact.

Do not create fake advisories for drills.

Do not request a CVE for a drill, unsupported claim, theoretical issue, or non-security bug.

## Public disclosure

Public disclosure should happen only after:

- maintainer acknowledgement or reasonable contact attempts
- fix or mitigation decision
- redaction review
- publication review
- removal of raw secrets and unsafe reproduction steps

## Scope boundary

Authorized research only.

No live target testing without written scope.

No exploit weaponization.
