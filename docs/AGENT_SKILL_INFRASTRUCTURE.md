# AAPP Agent Skill Infrastructure

## Status

`REFERENCE / TARGET`

AAPP Agent Skill Infrastructure is the governed supply chain and execution substrate for agent skills. B44A defines contracts only; it implements no registry, package manager, sandbox, queue, or evaluation service.

## Modules

1. Skill Registry
2. Skill Package Manager
3. Skill Contract
4. Capability Runtime
5. Durable Task Bus
6. Evaluation Service

These modules remain subordinate to AAPP authority, evidence, governance, and recovery controls.

## Skill Registry

### TARGET

The registry owns namespace, versions, publisher identity, package digest, compatibility metadata, deprecation, revocation, and evaluation references.

Registry presence is metadata, not a security certification.

## Skill Package Manager

### TARGET

```text
resolve -> lock -> fetch -> digest verify -> signature verify
-> provenance verify -> dependency/license review
-> quarantine -> evaluate -> promote
```

The lock identity must include the skill digest and all execution-relevant dependencies. A signature does not replace evaluation.

## Skill Contract

### REFERENCE

A machine-enforceable contract declares:

- identity and version;
- preconditions;
- requested permissions;
- granted capabilities;
- declared and forbidden effects;
- input/output schemas;
- resource and time limits;
- data classifications and egress constraints;
- recovery class;
- idempotency requirements;
- evaluation profile.

Invariants:

```text
observed_accesses subset_of granted_capabilities subset_of requested_permissions
observed_effects subset_of declared_effects
```

Missing contract, expiry, revocation path, or recovery class blocks governed mutable execution.

## Capability Runtime

### TARGET

Runtime classes:

- `INSTRUCTION_ONLY`
- `WASM_SANDBOXED`
- `MANAGED_CONTAINER`
- `MANAGED_BROWSER`
- `UNSANDBOXABLE`
- `UNSUPPORTED`

The first authorized prototype may support only `INSTRUCTION_ONLY` and `WASM_SANDBOXED`. This B44A gate supports neither at runtime.

The runtime must expose observed accesses and effects to an independent evidence writer and verifier. A skill cannot self-report successful compliance as final evidence.

## Durable Task Bus

### TARGET

Reference components:

- task journal;
- queue;
- lease;
- checkpoint;
- retry policy;
- idempotency key;
- receipt.

Reference lifecycle:

```text
REGISTERED -> VALIDATED -> ADMITTED -> QUEUED -> LEASED
-> RUNNING -> CHECKPOINTED -> VERIFYING -> SUCCEEDED
```

Failure, revocation, quarantine, and recovery states must remain explicit. No idempotency key means no automatic retry of state-changing work.

SQLite or JSONL may be evaluated in a future local prototype. NATS or Temporal adoption requires separate demand and benchmark evidence.

## Evaluation Service

### TARGET

Evaluation identity pins:

- skill digest;
- model digest when applicable;
- runtime digest;
- policy digest;
- evaluation-pack digest;
- fixtures and seed;
- environment and timestamp.

Verdicts:

- `COMPATIBLE`
- `CONDITIONALLY_COMPATIBLE`
- `INCOMPATIBLE`
- `REGRESSION`
- `UNSAFE_FOR_PROFILE`
- `INSUFFICIENT_DATA`
- `UNREPRODUCIBLE`

Compatibility is profile- and version-specific. It is not a universal safety claim.

## Revocation and Recovery

- Revoked skill -> no new lease.
- Revoked capability -> terminate or quarantine active work according to policy.
- Undeclared access or effect -> stop, preserve evidence, and open an incident path.
- Failed recovery -> incident casefile.
- Irreversible external effect -> explicit approval before execution.

## Compatibility Doctrine

### TARGET

AAPP should consume portable skill metadata through adapters and add a machine-enforced contract. It must not create a competing authoring format without evidence that adaptation is insufficient.

## Metrics

- verified_package_rate
- provenance_coverage
- lockfile_reproducibility
- undeclared_access_rate
- undeclared_effect_rate
- task_resume_rate
- evaluation_reproducibility

## Non-Goals

- registry server;
- package installation;
- Wasm execution;
- container or browser runtime;
- unrestricted shell;
- NATS or Temporal deployment;
- production secret access;
- claim that any skill is universally safe.
