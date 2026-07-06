# MCP-style Tool Permission Boundary v0.7

## Purpose

This document defines the local MCP-style tool permission boundary used by AAPP Phase 9.

This is not a live MCP server. It is a local simulator that models the permission boundary AAPP will later record and adapt.

## Boundary rule

No policy, no tool.

No allowlist, no execution.

No approval, no approval-required tool.

No network in local simulator.

Denied tools must produce a denied decision and must not execute.

## Tool registry

- read_file
- write_file
- shell_echo
- blocked_api_call

## Policy controls

- allowed_tools
- denied_tools
- approval_required_tools
- network_allowed

## Required negative behavior

- unknown tool is rejected
- denied tool is not executed
- approval-required tool is not executed without approval_ref
- network-like tool is blocked
- malformed policy is rejected

## Non-goals

- no live MCP server
- no network calls
- no external targets
- no credential access
- no exploit instructions
- no production security claim
