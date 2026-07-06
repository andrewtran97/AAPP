# AAPP — Flight Recorder for AI Agent Tool Actions

AAPP is a local reference implementation for tamper-evident AI agent action provenance.

It creates a verifiable action trail for agent/tool workflows:

```text
scope → tool request → policy decision → approval state → trace → replay → evidence bundle
```

Normal logs tell you something happened.

AAPP tries to prove what the agent was allowed to do, what tool it requested, what policy decided, and whether the evidence was changed later.

## Why now

AI agents are moving from chat into tool use.

MCP makes tool access portable. Agents can connect to files, databases, tools, workflows, and external systems.

That creates a new trust boundary:

```text
Can the agent use this tool?
Was the action in scope?
Was the decision allow, deny, or approval-required?
Can we verify the evidence after the fact?
Can a reviewer replay the action timeline?
```

AAPP is built for that boundary.

## The difference

AAPP is not observability.

AAPP is not a scanner.

AAPP is not a SIEM.

AAPP is not a pentest bot.

AAPP is provenance for the agent-action boundary.

```text
OpenTelemetry helps observe systems.
Sigstore/Rekor helps prove software supply-chain events.
AAPP focuses on AI agent tool actions.
```

## What it proves today

AAPP v1.1 can show:

- a scoped action trail
- tool request records
- policy decisions: `allow`, `deny`, `require_human_approval`
- hash-linked JSONL traces
- dev-only HMAC-SHA384 signatures
- strict verification
- replay reports
- evidence bundles
- secret-like value redaction
- denied tool attempts that remain visible without executing
- local MCP-style tool boundary evidence

## Current baseline

Current public baseline:

- `aapp-baseline-v1.1`
- public demo bundle
- external review packet
- local MCP-style boundary research
- GitHub Actions boundary review
- self-security advisory drill

Release:

https://github.com/andrewtran97/AAPP/releases/tag/aapp-baseline-v1.1

## 3-minute challenge

Try to tamper with the evidence.

```bash
git clone https://github.com/andrewtran97/AAPP.git
cd AAPP

python3 -m unittest discover -s tests -v

bash scripts/build_a1_mcp_boundary_research.sh evidence/a1-mcp-boundary

python3 -m aapp.cli verify \
  evidence/a1-mcp-boundary/recorded/trace.jsonl \
  --key-file evidence/a1-mcp-boundary/recorded/dev.key
```

Now modify one line in:

```text
evidence/a1-mcp-boundary/recorded/trace.jsonl
```

Run verify again.

If verification still passes after tampering, open an issue.

## What the demo produces

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

The bundle is designed to make local agent/tool activity easier to verify, replay, and review.

## What AAPP is not

AAPP does not claim:

- production security certification
- post-quantum security
- Qubes certification
- government affiliation
- compliance guarantee
- live MCP security
- production signing infrastructure

The current signing mode is dev-only.

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

## Reviewer entry point

Start here:

- Release v1.1: https://github.com/andrewtran97/AAPP/releases/tag/aapp-baseline-v1.1
- Public launch issue: https://github.com/andrewtran97/AAPP/issues/25
- External review request: https://github.com/andrewtran97/AAPP/issues
- Security policy: `SECURITY.md`
- MCP boundary research: `docs/MCP_BOUNDARY_RESEARCH.md`
- GitHub Actions boundary review: `docs/GITHUB_ACTIONS_BOUNDARY_REVIEW.md`

Useful review questions:

```text
1. Could you understand what AAPP does in 3 minutes?
2. Is the evidence bundle understandable?
3. Is this meaningfully different from a normal audit log?
4. What blocks pilot use?
5. What claim should be removed or softened?
```

## Governance

Main branch changes are gated by:

- pull request requirement
- signed commits
- required `basic` CI check
- squash merge
- force-push block
- deletion restriction
- linear history

## Project status

AAPP is an early reference implementation.

It is useful for:

- protocol review
- local demos
- agent/tool evidence review
- MCP-style boundary research
- replayable evidence bundle review
- external technical feedback

It is not ready for production signing, regulated compliance use, or high-assurance security claims.
