# Agent Action Provenance Protocol

AAPP is an open specification and local reference implementation for tamper-evident evidence records of AI agent actions, tool calls, approvals, policy decisions, and generated artifacts.

## Current phase

Scope Gate v0.2.

## What this implementation does

- creates local JSONL action records
- requires a scope file before active demo recording
- blocks unauthorized scopes and disallowed tool types
- links records with a SHA-384 hash chain
- signs record hashes with HMAC-SHA384 for local development only
- verifies tamper evidence
- redacts secret-like values before report generation
- generates a Markdown evidence report

## What this implementation does not do

- no exploit code
- no phishing
- no credential theft
- no persistence
- no evasion
- no live target scanning
- no production signing infrastructure
- no claim of post-quantum security

## Scope check

    python3 -m aapp.cli scope-check --scope examples/simple-tool-call/scope.demo.json --actor-type agent --tool-type file_read

## Demo

    python3 -m aapp.cli demo --scope examples/simple-tool-call/scope.demo.json --out evidence/demo
    python3 -m aapp.cli verify evidence/demo/trace.jsonl --key-file evidence/demo/dev.key
    python3 -m aapp.cli report evidence/demo/trace.jsonl --out evidence/demo/evidence.report.md

## Blocked demo

    python3 -m aapp.cli demo --scope examples/simple-tool-call/scope.blocked.json --out evidence/blocked-demo

## Tests

    python3 -m unittest discover -s tests -v

## Technical rule

No scope, no active recording.

No signed action trail, no trusted agent.
