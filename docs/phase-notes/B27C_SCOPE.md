# B27C Developer Distribution Gate

## 1. Phase Name & ID

B27C — Developer Distribution Gate.

## 2. Objective / Goal

Make the repository understandable and runnable by a new developer without changing runtime behavior.

## 3. Problem Statement

A new developer must be able to clone the repository, understand what AAPP does, run local examples, and see claim boundaries without private context.

## 4. Scope

### In Scope

- Developer quickstart.
- Claim boundary documentation.
- Local agent example.
- GitHub Action style example.
- MCP tool call style example.
- README developer quickstart section.
- Local-only demo outputs.
- No secrets.
- No paid external service.

### Out of Scope / Non-Goals

- No B28 code.
- No runtime behavior change.
- No scanner behavior change.
- No policy engine behavior change.
- No orchestration engine.
- No learning pipeline.
- No dashboard.
- No external authorization status claim.
- No paid external service dependency.
- Do not touch `aapp/*`.
- Do not touch `tests/test_*`.
- Do not touch `tests/fixtures/*`.
- Do not create `aapp/policy_abstraction.py`.
- Do not create `aapp/deterministic_risk_signals.py`.

### Future Considerations

- B27D may cover public release readiness.
- B28 may cover policy abstraction and deterministic risk signals after B27C is accepted on main.
- B46-B58 remain proposed post-B45 extension phases, not active implementation.

## 5. Metrics

### Completion Metrics / Definition of Done

- Required B27C files exist.
- `quickstart.sh` is executable.
- Three example scripts are executable.
- README includes developer quickstart section.
- Claim boundary document exists.
- Existing tests pass.
- Changed files are limited to B27C manifest.

### Quality & Safety Metrics

- No secrets required.
- No paid external service required.
- No unsupported public claim.
- No `.aapp/` evidence committed.
- No `__pycache__` remains.
- No B28 file created.

### Adoption / Usability Metrics

- New developer can run `bash quickstart.sh`.
- New developer can run each example locally.
- Claim boundaries are visible from repository docs.

### Performance / Scale Metrics

- Quickstart target: under 90 seconds on a normal developer machine.
- No runtime performance path added.
- No network dependency added.

## 6. Deliverables

### Required Files

- `docs/phase-notes/B27C_SCOPE.md`
- `docs/CLAIM_BOUNDARIES.md`
- `quickstart.sh`
- `examples/local-agent/README.md`
- `examples/local-agent/run.sh`
- `examples/github-action/README.md`
- `examples/github-action/run.sh`
- `examples/mcp-tool-call/README.md`
- `examples/mcp-tool-call/run.sh`
- `README.md`

### Code Artifacts

No runtime code artifacts.

B27C adds local shell examples only.

### Documentation

- B27C phase manifest.
- Claim boundaries.
- Example READMEs.
- README developer quickstart section.

### Machine-Readable Outputs

No persistent runtime output.

Example scripts may write temporary local JSON files under `/tmp`.

## 7. Dependencies & Prerequisites

- B27B accepted on main.
- Current branch is `b27c-developer-distribution-gate`.
- Issue #75 is open.
- Python 3 available.
- Bash available.
- Existing tests and validators remain unchanged.

## 8. Key Design Decisions

- Keep B27C documentation-first.
- Keep examples local-only.
- Do not change runtime code.
- Do not change test fixtures.
- Do not create B28 files.
- Use temporary directories for demo output.
- Keep public language bounded.

## 9. Validation Strategy

### Automated Validation

Run:

```bash
bash quickstart.sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_required_files.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_phase_manifest.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_claim_boundaries.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
Manual Validation

Review:

changed file list
README quickstart section
claim boundary table
example READMEs
example outputs
Scenario Validation
Fresh developer runs quickstart.
Local agent example runs.
GitHub Action style example runs.
MCP tool call style example runs.
No secret prompt appears.
Review Process
Validate locally.
Commit only B27C files.
Push branch.
Open PR.
Wait for CI.
Merge only if CI passes.
Pull main.
Run post-merge validation.
Close issue #75 only after post-merge validation passes.
10. Risks & Mitigations
Risk: B28 leaks into B27C.
Mitigation: forbidden file guard.
Risk: runtime drift.
Mitigation: diff guard against aapp/, tests/test_*, and tests/fixtures/.
Risk: unsupported language appears in docs.
Mitigation: claim boundary checker and manual review.
Risk: examples imply production deployment.
Mitigation: label as local developer examples only.
11. Kill Conditions
B27C changes runtime behavior.
B27C changes scanner behavior.
B27C changes policy engine behavior.
B27C introduces B28 implementation.
B27C requires secrets.
B27C requires paid external services.
B27C public docs claim external authorization status or final legal acceptance.
Existing tests regress.
__pycache__ remains.
Issue #75 is closed before merge and post-merge validation.
12. Success Criteria

B27C succeeds when all required files exist, quickstart passes, examples run, existing tests pass, changed files are limited to the B27C manifest, CI passes, and post-merge validation passes on main.

13. Transition to Next Phase

Do not start B28 until B27C is merged into main and post-merge validation passes.

14. Timeline & Owner

Owner: repository operator.

Timeline: one branch, one PR, one failure mode.

15. Final Phase Record

Status: active implementation.

Final acceptance requires merge to main and post-merge validation PASS.
