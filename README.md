# Agent Action Provenance Protocol

AAPP is an open specification and local reference implementation for tamper-evident evidence records of AI agent actions, tool calls, approvals, policy decisions, and generated artifacts.

## Current phase

Reference Recorder v0.1.

## What this implementation does

- creates local JSONL action records
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

## Demo

    python3 -m aapp.cli demo --out evidence/demo
    python3 -m aapp.cli verify evidence/demo/trace.jsonl --key-file evidence/demo/dev.key
    python3 -m aapp.cli report evidence/demo/trace.jsonl --out evidence/demo/evidence.report.md

## Tests

    python3 -m unittest discover -s tests -v

## Technical rule

No signed action trail, no trusted agent.
