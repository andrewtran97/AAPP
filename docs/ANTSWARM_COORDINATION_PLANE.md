# AAPP AntSwarm Coordination Layer

## Status

`RESEARCH`

AntSwarm is a stigmergic coordination hypothesis for selecting among already eligible candidate workflows. It is not a ninth control plane and owns no authority.

## Canonical Boundary

The deterministic authority kernel decides eligibility. AntSwarm may optimize exploration, task allocation, candidate path selection, and failure adaptation only after scope, identity, capability, policy, governance, and lease requirements are satisfied.

```text
Deterministic Authority Kernel -> eligible candidate set
AntSwarm Scheduler -> candidate path selection
Capability Runtime -> bounded execution
Independent Verifier -> outcome verdict
Trusted Reducer -> reward update from verified evidence
```

## Roles

- Scout: proposes candidate paths.
- Worker: executes an admitted bounded step.
- Validator: evaluates evidence independently.
- Sentinel: observes violations and revocation signals.
- Recovery: proposes or performs separately authorized recovery.
- Archivist: preserves references and evaluation history.

Roles do not imply separate models or separate runtime copies.

## Pheromone Vector

Path state is a vector, not truth:

- verified success;
- verification strength;
- freshness;
- relevance;
- latency efficiency;
- cost efficiency;
- novelty;
- saturation;
- risk;
- failure rate.

No scalar reward may erase risk, failed verification, or revocation.

## Trusted Update Flow

```text
agent reports result -> evidence writer records
-> independent verifier checks -> trusted reducer computes update
-> append-only reward reference updates path state
```

An agent cannot update pheromone directly or serve as the sole validator of its own output.

## Hard Rules

- Probabilistic scheduling != probabilistic authorization.
- Unverified success receives no positive reward.
- Revoked or expired capability makes a path ineligible.
- One agent cannot be sole validator of its own result.
- Mutable resources require a single-writer barrier or equivalent deterministic conflict control.
- Reward inputs must reference verifier and evidence identities.
- Scheduler failure cannot bypass default deny.

## Admission Preconditions

Research implementation remains blocked until:

- a single-agent baseline exists;
- a fixed-pipeline baseline exists;
- common fixtures and metrics exist;
- the trusted reducer is independent from workers;
- duplicate side effects are prevented;
- replay and saturation behavior are bounded;
- rollback to the fixed pipeline is demonstrated.

## Evaluation

Compare AntSwarm against fixed baselines on verified completion rate, verification strength, failure rate, duplicate effects, latency, cost, recovery success, and reproducibility.

Self-reported completion and activity volume are not success metrics.

## Kill Conditions

Stop or reject the research path when:

- AntSwarm underperforms a fixed pipeline on verified outcomes;
- reward gaming is not deterministically detected;
- an agent can modify its own reward;
- duplicate mutable effects occur;
- revocation does not remove path eligibility;
- results cannot be reproduced from pinned inputs;
- complexity cost exceeds measured benefit.

## Non-Goals

- authorization, approval, policy, or truth decisions;
- production mutation;
- self-modifying authority;
- autonomous reward updates;
- multi-model deployment;
- GPU or edge optimization;
- implementation in B44A.
