# Bounded Mutation Workflow

## Status

`REFERENCE`

This document describes the B44B local deterministic workflow authorized by issue `#122`. It does not define a production repository mutation service.

## Purpose

The workflow demonstrates one bounded mutable path:

```text
structured request
-> authority validation
-> exact target admission
-> pre-state digest check
-> one exact text mutation
-> independent actual-state verification
-> verified receipt
```

Verification failure changes the path:

```text
verification failure
-> restore original bytes
-> verify restored digest
-> recovered failure or incident-shaped failure
```

## Request Contract

Required fields:

| Field | Rule |
| --- | --- |
| `schema_version` | Must equal `aapp.bounded_mutation.request.v1` |
| `request_id` | Non-empty string |
| `workspace_root` | Existing absolute directory; final root path cannot be a symlink |
| `scope_ref` | Non-empty authority reference |
| `identity_ref` | Non-empty workload or agent identity reference |
| `capability_ref` | Non-empty capability reference |
| `policy_decision_ref` | Non-empty policy-decision reference |
| `policy_decision` | Must equal `ALLOW` |
| `target_relative_path` | Canonical POSIX relative path |
| `operation` | Must equal `replace_exact_text` |
| `expected_pre_state_digest` | SHA-384 digest with `sha384:` prefix |
| `old_text` | Non-empty UTF-8 text that must occur exactly once |
| `new_text` | UTF-8 replacement text; may be empty |
| `idempotency_key` | Non-empty string bound into evidence and receipt |
| `recovery_class` | Must equal `REVERSE` |

Unknown fields are rejected.

## Admission Rules

The workflow rejects:

- absolute target paths;
- `..`, empty, non-canonical, or backslash-separated paths;
- missing authority references;
- policy decisions other than `ALLOW`;
- unsupported operations or recovery classes;
- workspace roots that are missing, relative, or symlinks;
- parent-directory symlinks;
- target symlinks;
- non-regular files;
- targets with a hard-link count other than one;
- stale pre-state digests;
- non-UTF-8 targets;
- zero or multiple matches for `old_text`;
- no-op replacement requests.

The implementation uses directory-descriptor-relative filesystem access and checks each parent and target component without following symlinks.

## Mutation Semantics

The only supported operation is:

```text
replace exactly one occurrence of old_text with new_text
```

The workflow:

1. Opens the admitted target for read/write.
2. Captures target device, inode, link count, bytes, and SHA-384 pre-state digest.
3. Confirms the declared pre-state digest.
4. Computes the expected post-state bytes and digest.
5. Writes directly to the same target descriptor.
6. Flushes the target with `fsync`.
7. Closes the execution descriptor.
8. Calls the separate verifier module.

No sidecar file, temporary file, subprocess, shell, network call, or external service is used.

## Independent Verification

`aapp/bounded_mutation_verifier.py` reopens the target from the declared workspace and relative path. It does not accept workflow-reported content as proof.

The verifier checks:

- safe path reopening;
- regular-file type;
- hard-link count;
- original device and inode identity;
- actual bytes read from the filesystem;
- actual SHA-384 digest against the expected post-state digest.

Only verdict `VERIFIED` permits receipt creation.

## Evidence

The result contains ordered evidence events. Events bind:

- request digest;
- scope, identity, capability, and policy-decision references;
- target relative path;
- pre-state digest;
- expected and actual post-state digest;
- verifier verdict;
- recovery status.

Raw file content is not copied into the receipt.

## Receipt

A success receipt is created only after independent verification. It binds:

- request and idempotency identities;
- authority references;
- target and operation;
- pre-state and post-state digests;
- verifier verdict;
- evidence digest;
- deterministic receipt identity.

The receipt is unsigned local reference data. It is not legal finality, certification, or external trust proof.

## Recovery

If execution or independent verification fails after mutation begins, the workflow attempts to reopen the same target and requires the original device, inode, regular-file type, and single-link state.

Recovery writes the original bytes, flushes them, rereads the file, and verifies the restored digest.

Result states:

| Status | Meaning | Receipt |
| --- | --- | --- |
| `DENIED` | Request did not enter mutation or failed an admission rule | None |
| `VERIFIED` | Mutation completed and actual post-state verified | Present |
| `RECOVERED_FAILURE` | Mutation occurred, verification failed, original bytes restored | None |
| `INCIDENT` | Verification failed and recovery could not be confirmed | None |

## Limitations

- Reference environment is Ubuntu/Linux.
- The workflow is synchronous and single-process.
- It has no durable idempotency store.
- It does not coordinate concurrent writers.
- Direct in-place writing is not crash-consistent across process termination or power loss.
- Recovery restores bytes only, not timestamps, ownership, ACLs, or extended attributes.
- It does not determine whether a workspace is a production repository.
- Callers must use a disposable temporary workspace for this phase.
- It does not provide arbitrary patching or production containment.

## Verification

Focused test:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest tests.test_bounded_mutation_workflow -v
```

Full validation is defined in `docs/phase-notes/B44B_SCOPE.md`.
