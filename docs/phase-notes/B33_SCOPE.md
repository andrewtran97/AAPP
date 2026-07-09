# B33 Policy Backend Adapter

## Purpose

B33 adds a local deterministic Policy Backend Adapter reference path.

It defines an adapter boundary between AAPP policy-shaped requests and backend-shaped policy decision responses.

## File Manifest

- docs/phase-notes/B33_SCOPE.md
- docs/POLICY_BACKEND_ADAPTER.md
- tests/fixtures/policy_backend_adapter/sample_policy_request.json
- aapp/policy_backend_adapter.py
- tests/test_policy_backend_adapter.py

## Scope

B33 implements:

- local_static backend shape
- opa_json_shape backend shape
- deterministic unsupported-backend verdict
- deterministic malformed-input verdict
- policy input digest preservation
- reason-code and obligation pass-through

## Non-Goals

B33 does not:

- run OPA
- require Rego
- open network sockets
- call subprocesses
- implement policy hot reload
- implement multi-node policy sync
- create a production policy service
- change scanner behavior
- change runtime execution behavior
- bypass B28 deterministic policy behavior

## Acceptance

B33 is accepted only after:

- focused B33 unit tests pass
- full test suite passes locally
- exact dirty and staged file guards pass
- no network or subprocess dependency exists in the B33 module
- unsupported backend handling is deterministic
- malformed input handling is deterministic
- policy input digest is preserved

## Claim Boundary

B33 is a local deterministic reference only.

It is a backend adapter boundary, not a production OPA integration.
