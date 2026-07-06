# A2 — GitHub Actions Workflow Permission / Artifact Boundary Review

## Purpose

This document records AAPP Route A2: review of AAPP's GitHub Actions workflow permission, trigger, artifact, and automation boundary.

## Why this exists

AAPP cannot credibly ask others to trust its evidence/provenance workflow if its own CI boundary is unclear.

## Review target

- `.github/workflows/ci.yml`
- workflow permissions
- trigger boundary
- third-party action pinning
- artifact boundary
- untrusted input boundary
- release asset provenance boundary

## Non-goals

- no exploit development
- no live target testing
- no third-party repository testing
- no fake advisory
- no claim that CI is fully secure

## Required checks

- `GITHUB_TOKEN` has least-privilege permissions.
- `pull_request_target` is absent or explicitly justified.
- `workflow_run` is absent or explicitly justified.
- third-party actions are reviewed and either pinned or documented.
- artifact upload/download is reviewed if present.
- untrusted GitHub event context is not directly interpolated into shell.
- release assets remain tied to signed tag and checksum flow.

## Current A2 output

Run:

```bash
python3 tools/audit_github_actions_boundary.py
```

Expected output:

- list of workflow files
- permission findings
- trigger findings
- action pinning notes
- artifact boundary notes
- untrusted input notes

## Success condition

A maintainer can understand which workflow boundary was reviewed, what is pass/note/warn, and whether any hardening PR is needed.

## Kill condition

Stop if:

- workflow hardening weakens CI protection
- branch protection is bypassed
- workflow introduces secrets
- finding is called a vulnerability without reproducible security impact
- public issue contains sensitive exploit details
