# A1 — MCP Authorization / Tool Permission Boundary Research

## Purpose

A1 tests whether AAPP can produce useful evidence for MCP-style authorization and tool-permission decisions.

## Boundary

This is local-only research.

It does not contact:
- a live MCP server
- a network target
- an external service
- a real authorization server
- a credential store

## Why this exists

MCP connects AI applications to external systems such as files, databases, tools, and workflows. That creates a boundary where an agent asks to use a tool, policy decides allow/deny/approval, and an evidence layer should record what happened.

AAPP does not replace MCP authorization. AAPP records evidence around the decision boundary.

## Research question

Can AAPP make MCP-style tool decisions replayable and reviewable?

## What AAPP must show

- scope file exists
- local policy file exists
- tool decision is recorded
- denied action is preserved as denied
- approval-required action is visible
- trace verifies
- replay report explains timeline
- evidence bundle packages proof artifacts

## Expected local output

```text
evidence/a1-mcp-boundary/
  recorded/
    trace.jsonl
    dev.key
    mcp-results.json
    verification_result.md
  replay_report.md
  AAPP-EVIDENCE-BUNDLE/
    scope.json
    trace.jsonl
    evidence.bundle.json
    evidence.report.md
    hashes.txt
    verification_result.md
```

## Non-goals

- no live MCP server integration
- no exploit
- no credential handling
- no token testing
- no production security claim
- no advisory claim

## Success condition

A reviewer can answer:

1. Which tool was requested?
2. Was it allowed, denied, or approval-required?
3. What scope controlled it?
4. What policy controlled it?
5. Does the trace verify?
6. Can the timeline be replayed?
7. Does the bundle contain scope, trace, hashes, report, and verification result?

## Kill condition

Stop if:

- live MCP server is required
- network access is required
- credential/token material is required
- denied tool executes
- trace cannot verify
- replay report does not show deny/approval/allow
- evidence bundle is missing required files
