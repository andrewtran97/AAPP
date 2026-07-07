# B28 — Policy Abstraction + Deterministic Risk Signals

## Product gate

B28 introduces a policy abstraction contract and deterministic threat signal emission over that contract.

The core boundary is:

raw agent/tool/workflow event
→ policy abstraction normalization
→ deterministic threat signal emission
→ threat.signals.json

Policy abstraction is not optional. The detector must consume normalized subject/action/resource/context/risk/obligation records.

## Built in this branch

### Policy abstraction layer

- Adds `aapp/policy_abstraction.py`.
- Normalizes raw event sources into:
  - subject
  - action
  - resource
  - context
  - risk
  - obligation
- Validates required fields.
- Rejects malformed source payloads.
- Rejects unsupported source schemas.
- Rejects unsafe source payloads containing raw secrets/private keys.
- Redacts unsafe fields before detector consumption.
- Produces deterministic normalized policy records.

### Threat signal layer

- Adds `aapp/threat_detection_signals.py`.
- Consumes normalized policy abstraction output.
- Emits deterministic `threat.signals.json`.

Required deterministic signal types:

- REPEATED_DENY
- POLICY_TIMEOUT
- DEGRADED_MODE
- UNUSUAL_TOOL_COMPOSITION
- SENSITIVE_EXTERNAL_SINK
- MISSING_EVIDENCE_OBLIGATION

Required verdicts:

- SIGNALS_EMITTED
- NO_SIGNALS
- MALFORMED
- UNSAFE
- UNSUPPORTED

## Required files

- aapp/policy_abstraction.py
- aapp/threat_detection_signals.py
- tests/test_policy_abstraction.py
- tests/test_threat_detection_signals.py
- tests/fixtures/policy_abstraction/*
- tests/fixtures/threat_detection_signals/*
- docs/phase-notes/B28_SCOPE.md

## Required output

- threat.signals.json

## Deferred, not removed

- ML anomaly detection.
- SIEM export.
- External witness receipt.
- Crypto inventory.
- Crypto policy decision.
- Crypto migration planner.
- TEE / attestation provider adapter.
- Policy backend adapter.

## Non-goals

- No SIEM clone.
- No SOAR automation.
- No network IDS.
- No ML threat model.
- No FedRAMP/FIPS/CISA certification claim.
- No state mutation during detection-only path.
- No policy backend integration.
- No Cedar/Rego engine integration in B28.

## Validation

- `tests/test_policy_abstraction.py`
- `tests/test_threat_detection_signals.py`
- B15-B27 regression tests.
- CLI emits deterministic `threat.signals.json`.
- No raw secret/private key in signal output.
- No state mutation during detection-only path.

Closes #70
