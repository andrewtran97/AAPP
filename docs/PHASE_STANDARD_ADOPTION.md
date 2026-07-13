# AAPP Phase Standard Adoption

This document defines prospective adoption of the AAPP Phase Writing Standard without rewriting historical records or expanding the active gate.

## Adoption Scope

After this gate is accepted, every new phase must follow:

- `docs/PHASE_MANIFEST_STANDARD.md` for required structure;
- `docs/PHASE_WRITING_STANDARD.md` for required semantic content.

Historical manifests remain historical records unless a separate corrective gate authorizes a change.

## Current Gate Boundary

Issue #117 authorizes this documentation-only gate.

Exact files:

- `docs/PHASE_WRITING_STANDARD.md`
- `docs/PHASE_STANDARD_ADOPTION.md`
- `README.md`
- `CONTRIBUTING.md`

This gate does not change runtime code, tests, CI behavior, prior phase history, language or runtime tooling, or B45 implementation.

## Adoption Lifecycle

### Before a Branch

- Use one canonical issue.
- Confirm prior-phase acceptance and a clean ledger.
- Define objective, exact file boundary, non-goals, and transition conditions.
- Require written authorization before branch creation.

### Before Implementation

- Create or confirm the required phase manifest.
- Apply every semantic requirement in the Phase Writing Standard.
- Stop when any required element is absent or ambiguous.

### During Implementation

- Modify only authorized files and behavior.
- Use exact dirty-file guards.
- Stop on unexpected output.
- Do not mix unrelated cleanup, deferred architecture, or future-phase work.
- Do not commit generated evidence, secrets, private keys, tokens, or unredacted governed data.

### Before Commit and Pull Request

- Run focused validation when applicable.
- Run the full unit-test suite.
- Run repository guards.
- Run `git diff --check`.
- Verify exact dirty and staged file manifests.
- Reference the canonical issue without closing it.

### Merge and Acceptance

- Require CI success.
- Merge according to repository policy.
- Fast-forward local `main`.
- Rerun post-merge validation on `main`.
- Record the pull request, CI result, validation result, and final `main` commit.
- Close the canonical issue only after validation succeeds.

### Transition

The next phase remains blocked until the active phase is accepted and the ledger is unambiguous.

B45 must not begin until this gate is merged, CI and post-merge validation pass, and issue #117 closes as completed.

## Adoption Checklist

A future phase may start only when all answers are yes:

- Is there one canonical issue?
- Is the previous phase accepted?
- Is repository state clean and known?
- Does the manifest use the required structure?
- Are all semantic requirements explicit?
- Is the exact file and behavior boundary written?
- Are non-goals and deferred work written?
- Are deterministic validation and failure behavior defined?
- Are evidence and public claim boundaries defined?
- Are acceptance and transition rules defined?

A no answer blocks implementation.

## Exception Handling

There is no silent exception path.

Work exceeding the authorized boundary requires a stop and an amended issue and manifest before additional files or behavior change.

## Adoption Evidence

Acceptance evidence consists of:

- the exact four-file diff;
- successful repository guards and full tests;
- pull-request CI;
- merged pull-request identity;
- post-merge validation on `main`;
- the final accepted `main` commit;
- closure of issue #117 after validation.

## Non-Goals

This adoption does not certify historical phases, rewrite B0-B44 manifests, claim production enforcement, or authorize B45.

It adds no runtime service, dependency, network call, subprocess behavior, policy change, or cryptographic change.
