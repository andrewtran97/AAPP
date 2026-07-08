# AAPP — Agent Black Box

[![ci](https://github.com/andrewtran97/AAPP/actions/workflows/ci.yml/badge.svg)](https://github.com/andrewtran97/AAPP/actions/workflows/ci.yml)

Agent Black Box is a flight recorder for AI agent tool actions.

It records hook events, MCP tool calls, Git/CI evidence, and produces a tamper-evident session bundle so a reviewer can see what was requested, what policy decided, what evidence was produced, and whether the evidence changed later.

## Why it exists

AI agents are moving from chat into tool use.

The trust boundary is no longer just "what did the model say?" The new boundary is:

```text
What was the agent allowed to do?
What tool did it request?
Was the request allowed, denied, or routed to approval?
Did denied action execution stop?
Was the denied attempt still recorded?
Can the evidence bundle be verified later?
Can tampering be detected?
Agent Black Box is built for that boundary.

What it is

Agent Black Box is a local reference implementation for agent-action evidence.

Core evidence path:

scope
→ tool request
→ policy decision
→ trace
→ evidence bundle
→ manifest
→ report
→ signature / verification
What it is not

Agent Black Box is not:

an IDE replacement
a scanner
a SIEM
a pentest bot
a dashboard product
a compliance certification system
a full agent containment guarantee
a post-quantum security claim
Current status
Area	Status
Local hook capture	Available
MCP proxy recorder	Available
Git/CI evidence adapter	Available
Unified session bundle	Available
GitHub Action verifier	Available
VS Code/Cursor evidence panel	Reference adapter
Product E2E run	Available
Offline evidence package	Available
Evidence package QA	Complete
Independent validation	Pending
Security certification	Not claimed
Quick start

Requirements:

Python 3.10+
Git
OpenSSL for Ed25519 signing workflows

Run the core test suite:

git clone https://github.com/andrewtran97/AAPP.git
cd AAPP
python3 -m unittest discover -s tests -v

Run the end-to-end product flow:

bash scripts/run_agent_black_box_e2e.sh

Expected result:

Agent Black Box E2E product run: PASS
What the E2E run verifies

The product run executes the full evidence chain:

Hook gateway capture.
MCP proxy recording.
Git/CI evidence capture.
Unified session bundle creation.
GitHub Action-style verifier command.
Tamper rejection.

Expected outputs:

.aapp/evidence/agent-black-box-e2e/
  sources/
    hook/session.trace.jsonl
    mcp/mcp.trace.jsonl
    git-ci/gitci.trace.jsonl
  session-bundle/
    AGENT-BLACK-BOX-BUNDLE/
      manifest.json
      hook.trace.jsonl
      mcp.trace.jsonl
      gitci.trace.jsonl
      hashes.txt
      verification_result.md
      session.report.md
  github-action-style-report.md
  PRODUCT_RUN_SUMMARY.txt
Evidence package

A session bundle contains:

AGENT-BLACK-BOX-BUNDLE/
  manifest.json
  hook.trace.jsonl
  mcp.trace.jsonl
  gitci.trace.jsonl
  hashes.txt
  verification_result.md
  session.report.md

The bundle is designed to make local agent/tool activity easier to verify, replay, and review without storing raw secrets in the report.

Signing

Agent Black Box currently supports two signing layers:

Layer	Purpose
Dev HMAC-SHA384	Internal tamper-evident trace and bundle verification
Detached Ed25519 pilot signing	Review/pilot signing for the bundle manifest

Detached Ed25519 signing creates:

manifest.ed25519.sig
signature.profile.json
ed25519_public.pem

The private key is not copied into the evidence bundle.

Offline review package

For install-blocked environments, use the offline evidence package from the prerelease:

agent-black-box-v0.2.0-rc.20260706163212

Release:

https://github.com/andrewtran97/AAPP/releases/tag/agent-black-box-v0.2.0-rc.20260706163212

Offline review should start with:

README-OFFLINE-REVIEW.txt
PRODUCT_RUN_SUMMARY.txt
session-bundle/AGENT-BLACK-BOX-BUNDLE/session.report.md
session-bundle/AGENT-BLACK-BOX-BUNDLE/verification_result.md
session-bundle/AGENT-BLACK-BOX-BUNDLE/signature.profile.json
github-action-style-report.md
GitHub Action verifier

The repository includes a composite GitHub Action verifier:

.github/actions/agent-black-box-verify/action.yml

It runs the session bundle verifier and report command against a provided bundle.

Use cases

Agent Black Box is useful for:

local agent/tool evidence review
MCP-style tool boundary review
CI evidence capture
tamper-evident session bundle review
denied-action audit trails
pilot review of AI agent workflow provenance
Security boundary

Authorized research only.

Do not use this project for:

live target testing without written scope
exploit weaponization
credential theft
persistence
evasion
phishing
storing raw secrets in evidence bundles

Security issues should not be reported in public issues. See SECURITY.md.

Roadmap

Near-term:

B12 documentation and demo clarity.
Offline evidence package navigation.
Reviewer-friendly evidence map.
Packaging only if install friction remains a blocker.

Not planned right now:

dashboard expansion
scanner features
compliance certification claims
Rust/Go rewrite before schema freeze
VSIX/npm publication before packaging is justified
Contributing

See CONTRIBUTING.md.

Contribution priority:

Clear evidence semantics.
Small patches.
Deterministic tests.
No raw secrets.
No unsupported security or compliance claims.
License

See LICENSE.

If no LICENSE file is present, usage rights are not granted beyond normal repository viewing. Add an explicit license before presenting this as an open-source package.

## License

Apache License 2.0.

See `LICENSE`.

<!-- B27C_DEVELOPER_QUICKSTART_START -->
## Developer Quickstart

AAPP / Agent Black Box is an AI Agent Control + Evidence Plane for local developer review.

Run the local quickstart:

bash quickstart.sh

Run examples:

bash examples/local-agent/run.sh
bash examples/github-action/run.sh
bash examples/mcp-tool-call/run.sh

This quickstart is local-only.

It does not require secrets.

It does not require paid external services.

It does not open a browser.

It does not write runtime evidence into .aapp/.

Claim boundaries:

cat docs/CLAIM_BOUNDARIES.md
<!-- B27C_DEVELOPER_QUICKSTART_END -->
