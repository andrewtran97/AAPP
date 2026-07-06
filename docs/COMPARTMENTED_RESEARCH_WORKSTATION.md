# Compartmented Research Workstation

## Purpose

This is Layer 0 for authorized whitehat research and AAPP development.

It separates research, evidence, signing keys, disclosure, and publishing.

## Compartments

dom0 or host control plane:
- no browsing
- no unnecessary network use
- no research samples

vault environment:
- offline when possible
- stores private keys
- stores encrypted evidence bundles
- stores signed manifests

research environment:
- source review
- build and reproduction
- no production credentials

fuzz environment:
- fuzzing and crash reproduction
- disposable or resettable

reverse environment:
- Ghidra, radare2, debuggers
- authorized binaries only

network lab environment:
- packet capture for owned or authorized traffic
- no unauthorized scanning

disclosure environment:
- encrypted email
- maintainer/vendor communication
- responsible disclosure timeline

publish environment:
- sanitized writeups after disclosure window
- no weaponized exploit content

## Rules

Authorized research only.

No phishing.

No credential theft.

No persistence.

No evasion.

No covering tracks.

No live target scanning without written scope.

No raw secrets in public material.
