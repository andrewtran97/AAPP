# B29 Evidence Performance Plane

## 1. Phase Name & ID

B29 — Evidence Performance Plane.

## 2. Objective / Goal

Add a local evidence performance measurement plane without changing runtime trust semantics.

B29 measures the cost of evidence canonicalization, digest generation, and verification-shaped processing using deterministic local fixtures and benchmark output.

## 3. Problem Statement

AAPP currently has evidence, verification, and tamper-evident artifacts, but there is no scoped local benchmark that shows the cost of evidence processing.

Without measurement, future optimization decisions such as Rust rewrite, batching, zero-copy buffers, or async verification would be speculative.

B29 creates a small benchmark plane so later phases can make performance decisions from data instead of architecture preference.

## 4. Scope

### In Scope

- Local benchmark script for evidence processing cost.
- Synthetic local evidence fixture.
- Unit test for benchmark output shape.
- JSON-compatible benchmark result.
- Deterministic local-only execution.
- Documentation of measured fields.
- No performance guarantee.

### Out of Scope / Non-Goals

- No runtime behavior change.
- No trust semantics change.
- No Rust rewrite.
- No Go service.
- No NATS.
- No Kafka.
- No gRPC.
- No external witness receipt.
- No SIEM export.
- No dashboard.
- No orchestration engine.
- No network call.
- No external service dependency.
- No production performance claim.
- No B30 code.

### Future Considerations

B30 may address external witness receipts after B29 is accepted.

Later phases may introduce Rust or Go only if benchmark data proves a bottleneck.

Future optimization candidates must be justified by p50, p95, p99, throughput, and CI runtime data.

## 5. Metrics

### Completion Metrics / Definition of Done

- `docs/phase-notes/B29_SCOPE.md` exists.
- `benchmarks/evidence_pipeline_latency_bench.py` exists.
- `tests/test_evidence_performance_plane.py` exists.
- `tests/fixtures/evidence_performance/sample_records.jsonl` exists.
- Benchmark script runs locally.
- Benchmark output is JSON-compatible.
- New B29 tests pass.
- Existing tests pass.

### Quality & Safety Metrics

- No network call.
- No external command execution.
- No runtime evidence written into `.aapp/`.
- No production performance claim.
- No trust semantic change.
- No unsupported certification claim.
- No __pycache__ remains.

### Adoption / Usability Metrics

- Reviewer can run benchmark locally.
- Output fields are readable.
- Benchmark does not require secrets.
- Benchmark does not require paid services.

### Performance / Scale Metrics

B29 records measurement fields only:

- record_count
- iterations
- total_seconds
- records_per_second
- min_seconds
- max_seconds
- avg_seconds

B29 does not set pass/fail performance thresholds.

## 6. Deliverables

### Required Files

- `docs/phase-notes/B29_SCOPE.md`
- `benchmarks/evidence_pipeline_latency_bench.py`
- `tests/test_evidence_performance_plane.py`
- `tests/fixtures/evidence_performance/sample_records.jsonl`

### Code Artifacts

- Local benchmark script.
- Test validating benchmark output shape.

### Documentation

- B29 phase manifest.

### Machine-Readable Outputs

- Benchmark JSON printed to stdout.
- No committed benchmark runtime output.

## 7. Dependencies & Prerequisites

- B28 accepted on main.
- PR #80 merged.
- Issue #70 closed.
- Issue #81 open.
- Branch is `b29-evidence-performance-plane`.

## 8. Key Design Decisions

- Measurement first, optimization later.
- Use local synthetic fixture data.
- Avoid production claims.
- Avoid runtime path mutation.
- Avoid new infrastructure.
- Avoid external services.
- Keep implementation small and reviewable.

## 9. Validation Strategy

### Automated Validation

Run:

- B29 focused test.
- quickstart.
- required files checker.
- phase manifest checker.
- claim boundary checker.
- full unittest suite.

### Manual Validation

Review changed files and confirm B29 scope only.

### Scenario Validation

Validate:

- benchmark script runs locally.
- output is JSON-compatible.
- fixture is local.
- no `.aapp/` output is written.
- no network call exists.

### Review Process

One branch equals one product gate.

One PR equals one failure mode.

## 10. Risks & Mitigations

- Risk: B29 becomes optimization rewrite. Mitigation: measurement only.
- Risk: benchmark becomes flaky. Mitigation: no hard latency threshold.
- Risk: benchmark claims production performance. Mitigation: local-only language.
- Risk: runtime behavior changes. Mitigation: no `aapp/*` runtime integration unless explicitly required.
- Risk: generated output committed. Mitigation: stdout-only benchmark result.

## 11. Kill Conditions

- B29 changes runtime trust semantics.
- B29 adds Rust, Go, NATS, Kafka, gRPC, or Kubernetes.
- B29 adds external witness receipt.
- B29 adds SIEM export.
- B29 requires secrets.
- B29 requires paid external service.
- B29 writes runtime evidence into `.aapp/`.
- B29 claims production performance guarantee.
- Existing tests regress.
- New B29 tests fail.
- __pycache__ remains.
- Files outside B29 manifest are changed without explicit reason.

## 12. Success Criteria

B29 succeeds when:

- B29 manifest exists.
- Benchmark script exists.
- Synthetic fixture exists.
- Output shape test passes.
- Full test suite passes.
- CI passes.
- PR merges.
- Post-merge validation passes on main.
- Issue #81 closes only after post-merge validation.

## 13. Transition to Next Phase

Do not start B30 until B29 is merged and post-merge validation passes.

## 14. Timeline & Owner

Owner: repository operator.

Timeline: one scoped PR.

Implementation rule: one branch equals one product gate; one PR equals one failure mode.

## 15. Final Phase Record

Status: active implementation target.

Final acceptance requires merge to main and post-merge validation PASS.
