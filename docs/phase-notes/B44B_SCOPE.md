# B44B Coding-Agent Bounded File Mutation Workflow

## 1. Phase Name & ID

`B44B - Coding-Agent Bounded File Mutation Workflow`

Status: `REFERENCE`

Authorization: GitHub issue `#122`.

## 2. Objective / Goal

Implement one local deterministic reference workflow that accepts one structured request, mutates one declared UTF-8 text file, verifies actual post-state through a separate verifier module, restores pre-state after verification failure, and emits a receipt only after successful verification.

## 3. Problem Statement

The accepted repository contains independent scope, policy, identity, evidence, governance, and recovery-shaped modules, but it does not yet demonstrate one bounded mutable workflow from authority references through filesystem state, verification, recovery, and receipt.

Protected assets:

- files outside the exact declared target;
- the target pre-state;
- authority references;
- evidence continuity;
- receipt integrity;
- the distinction between verified success and recovered or unresolved failure.

Untrusted inputs:

- the structured request;
- workspace and target paths;
- expected pre-state digest;
- old and new text;
- policy decision and authority references;
- filesystem state that may contain links or unexpected file types.

## 4. Scope

### In Scope

- One structured request.
- One caller-provided temporary workspace.
- One canonical POSIX relative target path.
- One `replace_exact_text` operation.
- Required scope, identity, capability, and policy-decision references.
- SHA-384 pre-state and post-state digests.
- UTF-8 text only.
- Exactly one old-text occurrence.
- Parent and target symlink rejection.
- Hard-link rejection.
- Independent verifier reopening the actual target.
- Pre-state restoration after execution or verification failure.
- Reason-coded denied-attempt evidence.
- Success receipt only after verifier verdict `VERIFIED`.

### Out of Scope / Non-Goals

- No LLM or advisory model.
- No arbitrary patch format.
- No shell, subprocess, network, browser, container, or external service.
- No production repository mutation.
- No durable task queue or persistent idempotency ledger.
- No process-crash or power-loss recovery guarantee.
- No restoration of timestamps, ownership, ACLs, or extended attributes.
- No concurrent-writer coordination.
- No B45 attestation adapter.
- No new architecture plane or evidence protocol.
- No production containment, certification, or universal agent-safety claim.

### Future Considerations

Durable replay prevention, crash-consistent journaling, concurrent-writer control, metadata restoration, and production repository admission require separate authorization and measurable need.

## 5. Metrics

### Completion Metrics / Definition of Done

- Exactly six authorized files change.
- Focused B44B tests pass.
- Full unit-test discovery passes.
- Baseline phase-manifest, claim-boundary, required-file, and diff checks pass.
- Product E2E and tamper rejection pass outside the repository.
- Exact dirty and staged file sets equal the six-file manifest.
- CI passes.
- Squash merge and post-merge validation pass before issue closure.

### Quality & Safety Metrics

- Writes outside the exact target: zero.
- Success receipts without independent verification: zero.
- Symlink or traversal escapes accepted: zero.
- Hard-linked targets accepted: zero.
- Failed verification reported as success: zero.
- Failed recovery reported as success: zero.
- Raw target content copied into receipt: zero.

### Adoption / Usability Metrics

A reviewer can construct the fixture request, run one local mutation, inspect reason-coded evidence, distinguish verified success from recovered failure, and reproduce the focused tests without external services.

### Performance / Scale Metrics

The workflow processes one local text file synchronously. No throughput, concurrency, or production-scale claim is made.

## 6. Deliverables

### Required Files

- `docs/phase-notes/B44B_SCOPE.md`
- `docs/BOUNDED_MUTATION_WORKFLOW.md`
- `aapp/bounded_mutation_workflow.py`
- `aapp/bounded_mutation_verifier.py`
- `tests/fixtures/bounded_mutation_workflow/sample_workflow.json`
- `tests/test_bounded_mutation_workflow.py`

### Code Artifacts

- Request validation and bounded mutation workflow.
- Separate actual-filesystem verifier.
- Recovery and incident-shaped failure result.
- Deterministic evidence events and verified receipt construction.

### Documentation

- This phase manifest.
- Workflow contract, control laws, result states, limitations, and verification guidance.

### Machine-Readable Outputs

The Python API returns a dictionary containing status, reason codes, request digest, pre/post-state digests, verifier result, recovery result, optional incident, optional receipt, and ordered evidence events. No output is committed by default.

## 7. Dependencies & Prerequisites

- Issue `#122` is the sole written authorization.
- Branch: `b44b-bounded-mutation-workflow-122`.
- Accepted starting commit: `91dcd9aa106debb31fb6200498d6e3151cd47fc8`.
- Phase Writing Standard and B44A are accepted.
- Pre-implementation full tests, baseline guards, product E2E, and tamper rejection passed.
- Python standard library only.
- Ubuntu/Linux filesystem semantics are the reference environment.

## 8. Key Design Decisions

- Flat request fields keep the contract small and explicit.
- Unknown fields are rejected to avoid hidden behavior.
- The target path must be canonical, relative, and free of traversal.
- Directory-descriptor-relative opens and no-follow checks limit path substitution.
- Regular files with more than one hard link are rejected.
- The workflow writes only the target file; it creates no sidecar or temporary file.
- Direct in-place writing preserves the target inode but is not crash-consistent.
- The verifier reopens the target independently and checks device, inode, hard-link count, and digest.
- The idempotency key is required and receipt-bound; persistent replay prevention is not implemented.
- Receipt creation occurs only after the verifier returns `VERIFIED`.

## 9. Validation Strategy

### Automated Validation

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest tests.test_bounded_mutation_workflow -v

PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -v

python3 scripts/check_phase_manifest.py
python3 scripts/check_claim_boundaries.py
python3 scripts/check_required_files.py
git diff --check

rm -rf /tmp/aapp-b44b-e2e
bash scripts/run_agent_black_box_e2e.sh /tmp/aapp-b44b-e2e
```

A targeted manifest assertion must confirm all Phase Writing Standard headings exist in `B44B_SCOPE.md`. The repository-wide strict checker is not an acceptance command for B44B because accepted B43 and B44 manifests predate that format.

### Manual Validation

- Inspect the exact six-file diff.
- Confirm no subprocess, network, browser, or dependency addition.
- Confirm the verifier reads actual filesystem state.
- Confirm success receipt construction follows verifier success.
- Confirm limitations do not imply production containment or crash recovery.
- Confirm generated evidence remains outside the repository.

### Scenario Validation

- Valid request mutates exactly one target and produces a verified receipt.
- Absolute path and traversal requests are denied without mutation.
- Target and parent symlinks are denied.
- Hard-linked targets are denied.
- Stale pre-state is denied.
- Missing authority reference is denied.
- Zero or multiple text matches are denied.
- Verifier failure restores original bytes and emits no receipt.
- Recovery failure produces incident-shaped evidence.
- Post-write tampering fails independent verification.

### Review Process

The human executor reviews the exact diff and decides commit, push, PR, and merge. CI is the automated reviewer. `main` becomes the official record only after squash merge and post-merge validation. The PR body uses `Refs #122`; the issue closes only after an acceptance record.

## 10. Risks & Mitigations

- Path escape -> canonical relative path plus descriptor-relative no-follow traversal.
- Symlink substitution -> explicit no-follow metadata checks on parent and target components.
- Hard-link alias -> reject link count other than one.
- Stale write -> require exact pre-state digest.
- Ambiguous mutation -> require exactly one old-text occurrence.
- False success -> independent verifier inspects actual state before receipt.
- Verification failure -> restore original bytes and verify restored digest.
- Recovery failure -> incident-shaped result with no receipt.
- Crash during direct write -> documented limitation; no production use claim.
- Duplicate execution -> idempotency key is evidence-bound; durable replay prevention remains out of scope.

## 11. Kill Conditions

Stop the phase when:

- any file outside the six-file manifest changes;
- any write occurs outside the exact target;
- an absolute, traversal, symlink, or hard-link path is admitted;
- a success receipt exists without verifier verdict `VERIFIED`;
- the verifier trusts workflow-reported content instead of actual state;
- failed verification does not trigger recovery;
- failed recovery is reported as success;
- subprocess, network, browser, external service, or dependency behavior appears;
- production repository mutation is required;
- B45 work enters the diff;
- focused tests, full tests, baseline guards, E2E, tamper rejection, CI, or post-merge validation fail.

## 12. Success Criteria

- Exact six-file implementation matches issue `#122`.
- All required denial, verification, recovery, and incident scenarios pass.
- Exact dirty and staged guards pass.
- CI passes.
- The PR is squash-merged.
- Local `main` fast-forwards to accepted remote `main`.
- Post-merge validation passes.
- Issue `#122` receives one acceptance record and then closes.

## 13. Transition to Next Phase

No later phase starts until B44B is merged, post-merge validated, recorded as accepted, and issue `#122` is closed. Acceptance does not automatically authorize B45.

## 14. Timeline & Owner

Owner: human executor.

Implementation role: create only the six authorized files.

Timeline: one focused implementation pull request.
