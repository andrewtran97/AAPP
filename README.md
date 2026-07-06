# Agent Action Provenance Protocol

AAPP is a local reference implementation for tamper-evident evidence records of AI agent actions.

It records what an agent was allowed to do, which tool was requested, what policy decision was made, what artifact was produced, and whether the resulting action trail can be verified and replayed.

## Why this exists

AI agents are moving from text generation into tool use.

When an agent can call tools, write files, request approvals, or generate artifacts, teams need more than a chat transcript or application log. They need a structured evidence trail that can answer:

- What action was requested?
- Was it in scope?
- Which tool was involved?
- Was the decision allow, deny, or approval-required?
- Was evidence modified after the fact?
- Can the action timeline be replayed?

AAPP is an evidence layer for that boundary.

## Current baseline

Current public baseline:

- `aapp-baseline-v1.1`
- public demo bundle
- external review packet
- local MCP-style tool boundary research
- GitHub Actions boundary review
- self-security advisory drill

Release:

- https://github.com/andrewtran97/AAPP/releases/tag/aapp-baseline-v1.1

## What AAPP does

AAPP currently provides:

- local JSONL action records
- SHA-384 hash-linked traces
- dev-only HMAC-SHA384 signatures
- scope-gated recording
- strict trace verification
- replay reports
- evidence bundle generation
- redaction of secret-like values before report generation
- local MCP-style tool decision recording
- responsible disclosure and review templates

## What AAPP is not

AAPP is not:

- a scanner
- a pentest bot
- an exploit framework
- an AI firewall
- a live MCP server
- a production signing service
- a compliance guarantee
- a post-quantum security implementation

The current signing mode is for local development and reference implementation use only.

## Install

Clone the repository:

```bash
git clone https://github.com/andrewtran97/AAPP.git
cd AAPP
```

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

## Quick start

Run the local scoped demo:

```bash
python3 -m aapp.cli demo \
  --scope examples/simple-tool-call/scope.demo.json \
  --out evidence/demo
```

Verify the generated trace:

```bash
python3 -m aapp.cli verify \
  evidence/demo/trace.jsonl \
  --key-file evidence/demo/dev.key
```

Generate a replay report:

```bash
python3 -m aapp.cli replay \
  --trace evidence/demo/trace.jsonl \
  --key-file evidence/demo/dev.key \
  --scope examples/simple-tool-call/scope.demo.json \
  --out evidence/demo/replay_report.md
```

Create an evidence bundle:

```bash
python3 -m aapp.cli bundle \
  --scope examples/simple-tool-call/scope.demo.json \
  --trace evidence/demo/trace.jsonl \
  --key-file evidence/demo/dev.key \
  --report evidence/demo/replay_report.md \
  --out evidence/demo/AAPP-EVIDENCE-BUNDLE
```

## MCP-style tool boundary demo

AAPP includes a local MCP-style simulator.

It does not contact a live MCP server, network target, authorization server, external service, or credential store.

Run:

```bash
bash scripts/build_a1_mcp_boundary_research.sh evidence/a1-mcp-boundary
```

Expected output:

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

## Evidence bundle

An AAPP evidence bundle contains:

```text
AAPP-EVIDENCE-BUNDLE/
  scope.json
  trace.jsonl
  evidence.bundle.json
  evidence.report.md
  hashes.txt
  verification_result.md
```

The bundle is designed to make local agent/tool activity easier to review, replay, and verify.

## Security boundary

Authorized research only.

Do not use AAPP for:

- live target testing without written scope
- exploit weaponization
- credential theft
- persistence
- evasion
- phishing
- storing raw secrets in evidence bundles

Security issues should not be reported in public issues. See `SECURITY.md`.

## Project status

AAPP is an early reference implementation.

The current baseline is useful for:

- local demos
- protocol review
- MCP-style tool boundary research
- evidence bundle review
- external technical feedback

It is not ready for production signing, regulated compliance use, or high-assurance security claims.

## Reviewers

Start here:

- Release v1.1: https://github.com/andrewtran97/AAPP/releases/tag/aapp-baseline-v1.1
- Public launch issue: https://github.com/andrewtran97/AAPP/issues/25
- Security policy: `SECURITY.md`
- MCP boundary research: `docs/MCP_BOUNDARY_RESEARCH.md`
- GitHub Actions boundary review: `docs/GITHUB_ACTIONS_BOUNDARY_REVIEW.md`
- External review pack: release asset `aapp-external-review-packet-v1.1.tar.gz`

## Repository governance

Main branch changes are gated by:

- pull request requirement
- signed commits
- required `basic` CI check
- squash merge
- force-push block
- deletion restriction
- linear history
