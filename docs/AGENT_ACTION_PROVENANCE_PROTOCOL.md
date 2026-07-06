# Agent Action Provenance Protocol

## Problem

AI agents can read files, call tools, modify code, request approvals, call APIs, and generate artifacts.

When an agent causes damage, a company needs evidence of:

- which agent acted
- which tool was called
- what scope was authorized
- what input and output were used
- whether human approval existed
- what policy decision was made
- what artifact changed
- whether the record was altered later

## Protocol goal

AAPP creates tamper-evident action records for AI agent activity.

The protocol does not execute exploits.

The protocol does not collect credentials.

The protocol does not store raw secrets in reports.

The protocol records evidence metadata, digests, policy decisions, approvals, and artifact references.

## Core record chain

Each record includes:

- schema_version
- record_id
- session_id
- parent_hash
- actor
- tool
- scope
- policy
- input_digest
- output_digest
- artifact_digest
- approval_ref
- timestamp
- record_hash
- signature

## Kill conditions

Stop development if:

- records can be modified without verification failure
- raw secrets appear in reports
- scope is optional for active operations
- the project implies government affiliation
- the project claims certification not granted
- the project claims post-quantum security before implementation and review
