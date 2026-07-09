# Policy Backend Adapter

## Purpose

Policy Backend Adapter provides a local deterministic reference for adapting AAPP policy-shaped requests into backend-shaped decision responses.

## Supported Local Backend Shapes

B33 supports two local backend shapes:

- local_static
- opa_json_shape

## Input Contract

Required input fields:

- schema_version
- request_id
- subject
- action
- resource
- policy_input_digest

Optional input fields:

- context
- requested_verdict
- reason_codes
- obligations

## Adapter Verdicts

The adapter returns:

- ADAPTED
- UNSUPPORTED
- MALFORMED

## Decision Verdicts

Supported decision verdicts:

- ALLOW
- DENY
- REQUIRE_APPROVAL

## Digest Boundary

The policy_input_digest must be preserved in every adapted output.

## Backend Boundary

The opa_json_shape backend returns a local OPA-shaped JSON response.

It does not:

- run OPA
- require Rego
- open network sockets
- call subprocesses
- implement policy hot reload
- implement multi-node policy sync

## Non-Goals

This reference does not:

- create a production policy service
- change scanner behavior
- change runtime execution behavior
- bypass B28 deterministic policy behavior

## Claim Boundary

This is a local deterministic reference only.
