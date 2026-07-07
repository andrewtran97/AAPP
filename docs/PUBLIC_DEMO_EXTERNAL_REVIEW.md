# AAPP Public Demo + External Review Pack v1.1

## Purpose

This pack prepares a public-safe local demo and external review workflow for AAPP.

AAPP is a tamper-evident evidence layer for AI agent actions. It is not a scanner, pentest bot, exploit framework, AI firewall, or live MCP security product.

## Public demo boundary

The demo is local only.

It does not contact:
- a live MCP server
- a network target
- an external service
- a real vendor system
- a credential store

## Required public demo outputs

- README.md
- recorded/trace.jsonl
- recorded/dev.key
- recorded/mcp-results.json
- recorded/verification_result.md
- replay_report.md
- AAPP-EVIDENCE-BUNDLE/scope.json
- AAPP-EVIDENCE-BUNDLE/trace.jsonl
- AAPP-EVIDENCE-BUNDLE/evidence.bundle.json
- AAPP-EVIDENCE-BUNDLE/evidence.report.md
- AAPP-EVIDENCE-BUNDLE/hashes.txt
- AAPP-EVIDENCE-BUNDLE/verification_result.md

## External review target

Send the review pack to 3 named reviewers.

Minimum acceptable result:
- public-safe demo created
- review packet sent to 3 reviewers
- at least 1 written review requested before expanding claims

Stronger result:
- at least 1 written external review received
- limitations updated from review
- unsupported claims removed

## Reviewer profile

Acceptable reviewers:
- security engineer
- AppSec engineer
- AI agent tooling engineer
- incident response engineer
- secure software supply-chain engineer
- MCP/tooling engineer

## Review questions

1. Can you understand what AAPP proves in 3 minutes?
2. Is the demo clearly local-only?
3. Does the evidence bundle show scope, trace, hashes, verification, and replay?
4. Are denied and approval-required actions visible?
5. Are there unsupported claims?
6. Are there privacy or disclosure risks?
7. What would block you from trusting this as a reference implementation?

## Claim restrictions

Do not claim:
- production security
- post-quantum security
- Qubes-certified
- government-grade
- does not claim military-grade
- compliance is not guaranteed
- AI safety solved
- live MCP secured
- live MCP integration
- production security certification

Allowed wording:
- local reference implementation
- local MCP-style simulator
- tamper-evident action trace
- scope-gated verification
- evidence bundle
- replay report
- responsible disclosure pack
