# AAPP Phase Writing Standard

This document defines the semantic writing requirements for future AAPP phases.

It complements `docs/PHASE_MANIFEST_STANDARD.md`. The manifest standard owns the required phase-note structure. This standard defines what those sections must say for implementation, review, failure handling, and acceptance.

## Applicability

This standard applies prospectively after this gate is accepted.

Historical phase notes are not rewritten solely to adopt this standard.

Every new phase requires written authorization, an exact scope manifest, explicit non-goals, deterministic validation, and a post-merge acceptance record.

## Required Semantic Contract

Every future phase must express these requirements within the corresponding headings required by `docs/PHASE_MANIFEST_STANDARD.md`.

| Requirement | Required expression | Manifest location |
| --- | --- | --- |
| Phase intent | State the bounded business and technical outcome. | Objective / Goal and Problem Statement |
| Operator posture | Identify the executor, implementation role, automated reviewer, and final record. | Key Design Decisions, Review Process, Timeline & Owner |
| Authorization boundary | Identify the issue, allowed files and behavior, prohibited behavior, and exception authority. | Scope and Dependencies & Prerequisites |
| Threat model | Identify protected assets, untrusted inputs, trust boundaries, bypass paths, misuse, and failure modes. | Problem Statement and Risks & Mitigations |
| Deterministic rules | Define input, condition, verdict, and failure behavior. | Key Design Decisions and Validation Strategy |
| Evidence expectation | Name required artifacts, digests, reports, receipts, or test output. | Deliverables and Validation Strategy |
| Public claim boundary | State what the phase demonstrates and does not demonstrate. | Out of Scope / Non-Goals and Risks & Mitigations |
| Verification commands | Provide exact focused, full-suite, guard, diff, and post-merge commands. | Automated Validation |
| Failure handling | Define fail-stop, recovery, evidence preservation, and progression blockers. | Risks & Mitigations and Kill Conditions |
| Acceptance rule | Define merge, CI, post-merge validation, issue closure, and transition conditions. | Success Criteria and Transition to Next Phase |

A phase is not ready for implementation when any required element is absent or ambiguous.

## Operator Posture

- Human executor: runs terminal operations and makes merge decisions.
- Implementation role: changes only authorized files and behavior.
- Automated reviewer: runs deterministic tests and repository guards.
- Main branch: becomes the official record only after merge and post-merge validation.
- Advisory AI: may propose work but cannot create scope, approval, acceptance, evidence identity, or final authority.

No role may silently expand the issue or phase manifest.

## Authorization Boundary

The phase must state:

- the canonical issue or written mandate;
- the starting branch and expected base when relevant;
- the exact allowed file manifest;
- permitted runtime, data, network, subprocess, and external-service effects;
- prohibited changes and deferred work;
- the approval required for an exception.

Work outside this boundary requires a stop and an amended authorization before implementation continues.

## Threat Model

The threat model must be specific to the phase and consider applicable risks:

- scope expansion or bypass;
- malformed or adversarial input;
- missing identity, policy, capability, tenant, or evidence references;
- evidence omission, substitution, truncation, or fabrication;
- secret, personal, tenant, or rights-restricted data exposure;
- duplicate or irreversible side effects;
- unsupported public claims;
- new dependency, supply-chain, or external-service assumptions.

Do not copy threats that cannot affect the scoped deliverables.

## Deterministic Rules

Preferred form:

`condition -> verdict or required action`

Every rule must define its failure result. Missing required authority or evidence defaults to blocking behavior unless the phase defines a narrower safe result.

AI-generated recommendations cannot serve as final authorization, acceptance, signature, receipt, or verifier identity.

## Evidence Expectation

The phase must state what evidence is generated, where it is expected, and how it is verified.

Evidence requirements must distinguish:

- source input from derived output;
- recorded facts from recommendations;
- reference behavior from production enforcement;
- tamper-evident records from absolute correctness or legal proof;
- sanitized metadata from raw secrets or governed payloads.

Runtime evidence under `.aapp/`, raw secrets, private keys, access tokens, and unredacted customer data must not be committed.

## Public Claim Boundary

Public language must remain limited to implemented and verified behavior.

A phase must not imply external certification, regulatory authorization, universal safety, guaranteed containment, objective truth, or production readiness unless independently established and explicitly authorized.

Target, reference, research, and out-of-scope capabilities must not be presented as implemented.

## Verification Commands

Commands must be copy-pasteable, deterministic, and run from the repository root.

When applicable, define:

1. branch, base, and dirty-state guards;
2. focused tests;
3. the full unit-test suite;
4. phase, claim-boundary, and required-file guards;
5. `git diff --check`;
6. exact dirty and staged file allowlists;
7. post-merge validation on `main`.

Manual inspection may supplement deterministic validation but cannot replace it.

## Failure Handling

Unexpected output stops the current block.

Failed validation preserves the failure evidence, leaves unrelated files untouched, and blocks staging, commit, merge, issue closure, and next-phase work.

Recovery must be defined before destructive or state-changing production action. A documentation-only phase performs no runtime mutation.

## Acceptance Rule

A phase is accepted only when:

- implementation matches the authorization and exact file manifest;
- focused and full validation pass;
- repository guards and CI pass;
- the pull request is reviewed and merged;
- `main` is post-merge validated;
- acceptance evidence and the final `main` commit are recorded;
- the canonical issue closes only after post-merge validation;
- next-phase transition conditions are satisfied.

A local PASS, commit, pushed branch, or merged pull request alone is not full acceptance.

## Writing Quality Rules

Use precise status language: implemented, reference, target, research, or out of scope.

Use exact paths, commands, verdicts, reason codes, and expected outputs where they exist.

Do not use aspirational architecture as evidence of implementation or replace measurable acceptance with unsupported adjectives.

## Control Laws

- No written authorization -> no phase work.
- No phase manifest -> no branch.
- No exact file boundary -> no implementation.
- No threat model -> no security claim.
- No deterministic validation -> no acceptance.
- No evidence expectation -> no completion claim.
- No failure handling -> no state-changing action.
- No CI -> no merge.
- No post-merge validation -> main not accepted.
- No accepted current phase -> no next phase.

## Non-Goals

This standard does not change runtime behavior, tests, historical records, policy decisions, cryptographic behavior, external services, or B45 implementation.

It does not replace `docs/PHASE_MANIFEST_STANDARD.md` or create a competing manifest format.
