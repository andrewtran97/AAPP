# B44A Canonical System V2 Documentation Gate

## 1. Phase Name & ID

`B44A - Canonical System V2 Documentation Gate`

## 2. Objective / Goal

Consolidate the accepted AAPP definition, architecture boundaries, open-source doctrine, governed AI schemas, skill infrastructure, and AntSwarm research boundary into six status-labeled documents without changing runtime behavior.

## 3. Problem Statement

Architecture material exists across prior discussions and documents with mixed implementation status. Without explicit status labels and one bounded canonical record, target and research concepts can be mistaken for implemented enforcement.

Protected assets are repository claim integrity, phase history, exact scope, and the distinction between current reference behavior and future architecture. Untrusted inputs include aspirational language, stale terminology, copied architecture claims, and unsupported implementation assertions.

## 4. Scope

### In Scope

- Update the canonical system document to V2.
- Add open-source adoption doctrine.
- Add four governed advisory-agent schema boundaries.
- Add agent skill infrastructure contracts.
- Add AntSwarm as research-only coordination with no authority.
- Apply `IMPLEMENTED`, `REFERENCE`, `TARGET`, `RESEARCH`, and `OUT_OF_SCOPE` status vocabulary.

### Out of Scope / Non-Goals

- Runtime code, tests, fixtures, schemas, CI, dependencies, or behavior changes.
- New products, control planes, AI roles, or target-language scaffolding.
- B45 implementation.
- Go, Rust, TypeScript, NATS, Temporal, GPU, browser, cloud, container, Wasm, or production-service implementation.
- Production enforcement, production DLP, production tenant isolation, certification, or post-quantum security claims.

### Future Considerations

B45 and later roadmap work require separate issues, manifests, exact files, implementation evidence, and acceptance. Documentation in B44A grants no future runtime authority.

## 5. Metrics

### Completion Metrics / Definition of Done

- Exactly six authorized files are changed.
- All five status labels are defined and used consistently.
- All required manifest sections exist.
- Full unit tests, repository guards, E2E, tamper rejection, and CI pass.

### Quality & Safety Metrics

- Unsupported implementation claims: zero.
- Runtime files changed: zero.
- Files outside the exact manifest changed: zero.
- Claim-boundary guard failures: zero.

### Adoption / Usability Metrics

Human review can identify current, reference, target, research, and excluded behavior without consulting architecture discussions outside the repository.

### Performance / Scale Metrics

Not applicable. B44A changes documentation only and introduces no execution path.

## 6. Deliverables

### Required Files

- `docs/AGENT_BLACK_BOX_CANONICAL_SYSTEM.md`
- `docs/OPEN_SOURCE_STRATEGY.md`
- `docs/AI_AGENT_SCHEMAS.md`
- `docs/AGENT_SKILL_INFRASTRUCTURE.md`
- `docs/ANTSWARM_COORDINATION_PLANE.md`
- `docs/phase-notes/B44A_SCOPE.md`

### Code Artifacts

No runtime code artifacts.

### Documentation

The six files in Required Files are the complete documentation deliverable.

### Machine-Readable Outputs

No committed machine-readable output. Tests, guards, CI, and temporary E2E output provide validation evidence.

## 7. Dependencies & Prerequisites

- Issue #120 is the sole written authorization.
- Phase Writing Standard and Phase Manifest Standard are accepted on `main`.
- PR #119 is merged and post-merge validated.
- Starting `main` commit is `27c9d13a2caa1d1c47a2439e287f05a3d8460408`.
- Branch is `docs/b44a-canonical-system-v2-120`.
- Worktree is clean before implementation.

## 8. Key Design Decisions

- Preserve one AAPP system and the accepted eight-plane architecture.
- Use explicit status labels instead of implying implementation through document placement.
- Keep AI advisory and deny it final authority.
- Keep AntSwarm research-only and subordinate to deterministic authority.
- Prefer upstream adapters over rewrites; dependency adoption remains separately gated.
- Use documentation only because no runtime enforcement is authorized.

Operator posture:

- Human executor runs terminal operations and decides merge.
- Implementation role changes only the six authorized files.
- CI and repository guards provide automated review.
- `main` becomes the official record only after merge and post-merge validation.

## 9. Validation Strategy

### Automated Validation

Run from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/check_phase_manifest.py
AAPP_STRICT_PHASE_MANIFEST=1 python3 scripts/check_phase_manifest.py
python3 scripts/check_claim_boundaries.py
python3 scripts/check_required_files.py
git diff --check
rm -rf /tmp/aapp-b44a-e2e
bash scripts/run_agent_black_box_e2e.sh /tmp/aapp-b44a-e2e
```

Exact dirty and staged-file allowlists must equal the six Required Files.

### Manual Validation

- Confirm every architecture section has an unambiguous status.
- Confirm target and research text is not written as current implementation.
- Confirm no ninth control plane, new product, runtime behavior, or dependency adoption is introduced.
- Confirm all links and file names are exact.

### Scenario Validation

- A reader can distinguish current Python reference behavior from production targets.
- A reader cannot interpret AI or AntSwarm as final authority.
- A reader can identify the exact open-source adoption gate and skill-runtime boundary.
- Tampered E2E evidence remains rejected by the existing runtime.

### Review Process

The human executor reviews the exact six-file diff, test and guard results, E2E result, CI, claim boundaries, and status accuracy. Any missing status, extra file, failed validation, or unsupported claim blocks merge.

## 10. Risks & Mitigations

- Architecture inflation -> retain one system, eight planes, and existing product hierarchy.
- Target presented as implemented -> require explicit status labels and manual review.
- Documentation authorizes behavior -> state that runtime work requires a separate gate.
- Claim drift -> run the claim-boundary guard and inspect public wording.
- Scope drift -> enforce exact dirty and staged-file allowlists.
- Historical rewrite -> change only the canonical doc plus five new B44A documents.

## 11. Kill Conditions

Stop the phase when:

- any file outside the six-file manifest changes;
- runtime behavior, test behavior, CI, dependency, or external service changes;
- a new product, control plane, or implementation claim appears;
- B45 work enters the diff;
- a guard, full test, E2E, tamper rejection, or CI check fails;
- issue #120, branch, or base identity is inconsistent.

Failure preserves evidence, leaves unrelated files untouched, and blocks staging, commit, PR, merge, issue closure, and next-phase work.

## 12. Success Criteria

- Exact six-file implementation matches issue #120.
- Full validation and CI pass.
- Pull request is squash-merged.
- Local `main` is fast-forwarded to accepted remote `main`.
- Post-merge validation passes on `main`.
- Acceptance evidence records PR, CI, final commit, and issue closure.

## 13. Transition to Next Phase

No next phase starts until B44A is merged, `main` passes post-merge validation, issue #120 closes as completed, and the ledger is unambiguous. B44A acceptance does not automatically authorize B45; B45 requires its own issue and exact manifest.

## 14. Timeline & Owner

Owner: human executor.
Timeline: single documentation-gate pull request.

## Final Phase Record

The final record is the merged pull request, successful CI result, post-merge validation evidence, issue #120 closure, and accepted `main` commit.
