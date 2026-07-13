
Contributing

Agent Black Box is a local reference implementation for AI agent tool-action evidence.

The project accepts small, testable changes that improve evidence capture, verification, documentation clarity, or reviewability.

Contribution rules

Use small patches.

Do not mix protocol changes, docs changes, packaging, and refactors in one pull request.

Do not add:

scanner behavior
exploit automation
credential collection
persistence
evasion
phishing workflows
compliance certification claims
full agent containment claims
post-quantum security claims
Required checks

Before opening a pull request, run:

python3 -m unittest discover -s tests -v
bash scripts/run_agent_black_box_e2e.sh

If the VS Code/Cursor adapter is changed, also run its local compile/test path before submitting.

Evidence handling

Do not commit:

raw secrets
private keys
access tokens
unredacted customer data
bystander data
local runtime evidence under .aapp/
node_modules/
extension build output unless intentionally packaging
Security reports

Do not report vulnerabilities in public issues.

Use the process in SECURITY.md.

Pull request standard

A good pull request includes:

what changed
why it changed
test command output
risk or boundary impact
files affected
Language standard

Use product-grade status language:

Evidence package QA: complete.
Offline evidence package: available.
Independent validation: pending.
Security certification: not claimed.

Avoid unsupported claims:

security certification language
compliance-readiness language
agent containment guarantees
production certification language
post-quantum security language

## Phase Writing Standard

All new AAPP phases must follow:

- `docs/PHASE_MANIFEST_STANDARD.md`
- `docs/PHASE_WRITING_STANDARD.md`
- `docs/PHASE_STANDARD_ADOPTION.md`

New phase work requires written authorization, an exact file boundary, explicit non-goals, deterministic validation, failure handling, and post-merge acceptance.

Historical phase notes are not rewritten solely to adopt the current standard.
