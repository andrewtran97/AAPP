# MCP Recorder Adapter v0.8

## Purpose

The MCP Recorder Adapter connects the local MCP-style permission boundary to AAPP action records.

This phase records simulated MCP-style tool calls as signed AAPP trace records.

## Boundary

This is not a live MCP server.

No network.

No external target.

No credential access.

No exploit instructions.

## Flow

Policy
→ local MCP-style tool call decision
→ AAPP action record
→ hash chain
→ dev-only signature
→ verifier
→ trace output

## Required behavior

- allowed tool calls are recorded
- denied tool calls are recorded as denied
- approval-required calls without approval are recorded as require_human_approval
- approval-required calls with approval_ref are recorded as allow
- blocked network-like tool does not execute
- recorded trace verifies through AAPP verifier

## Non-goals

- no production MCP adapter
- no live server
- no remote tool invocation
- no post-quantum security claim
- no compliance guarantee
