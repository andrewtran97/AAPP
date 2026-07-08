# Judge Court Layer

## 1. Purpose

The Judge Court Layer is a review and ranking layer for candidate agent outputs.

It may help compare candidate patches, reports, or recommendations.

It must not become final authority for merge, deploy, allow, deny, security-sensitive execution, or compliance acceptance.

## 2. Current Phase Boundary

B29A is documentation-only.

This document records the target authority boundary for the Judge Court Layer.

B29A does not add judge runtime code, model routing, evaluation workers, merge automation, deployment automation, or policy execution changes.

## 3. Authority Chain

The authority chain is:

1. Candidate agent proposes.
2. Hard gates reject invalid candidates.
3. Static scoring ranks candidates.
4. LLM semantic review may comment or recommend.
5. Deterministic aggregator produces a recommendation.
6. CI validates.
7. Policy gate validates.
8. Human or configured merge authority decides.
9. Main is accepted only after post-merge validation.

## 4. Non-Authority Rule

The Judge Court Layer must not be final authority for:

- merge
- deploy
- allow
- deny
- destructive execution
- security-sensitive execution
- compliance acceptance
- production release acceptance

Final authority remains deterministic gates, CI, policy, and human or configured authority.

## 5. Target Flow

The target flow is:

task + acceptance criteria
-> candidate outputs
-> hard gate
-> static scoring
-> LLM semantic review
-> deterministic aggregation
-> CI
-> policy gate
-> human or configured authority
-> PR, reject, rerun, or human review

## 6. Hard Gate Rejects

Hard gates reject before LLM review when any of these occur:

- forbidden file change
- runtime drift
- test failure
- claim boundary failure
- secret-like value detected
- wrong phase file introduced
- tamper mismatch
- missing required file
- malformed JSON
- unsupported schema version
- policy violation

## 7. Static Scoring Boundary

Static scoring may use deterministic signals such as:

- changed file scope
- test pass or fail state
- required files present
- forbidden files absent
- claim boundary result
- fixture coverage
- benchmark output shape
- JSON parse validity
- documentation heading presence

Static scoring must not override hard gates.

## 8. LLM Semantic Review Boundary

LLM semantic review may evaluate:

- clarity
- consistency
- missing explanation
- likely reviewer confusion
- mismatch between stated scope and changed files
- documentation quality
- reason-code clarity

LLM semantic review must not override hard gates, CI, policy, or human/configured authority.

## 9. Deterministic Aggregator Boundary

The deterministic aggregator may combine hard gate results, static scores, and semantic review notes into a recommendation.

Allowed recommendation outputs:

- APPROVE_FOR_PR
- REJECT
- REQUIRES_HUMAN_REVIEW
- REQUIRES_RERUN

The recommendation is not final merge authority.

## 10. CI Boundary

CI remains a required validation layer.

If CI fails, the candidate is not accepted.

If CI is skipped, missing, or inconclusive, the candidate must not be treated as accepted.

## 11. Policy Boundary

Policy gate remains a required validation layer for security-sensitive or scope-sensitive actions.

Policy gate output must be deterministic and reason-coded.

LLM review must not become policy decision authority.

## 12. Human Or Configured Authority Boundary

Human or configured merge authority is the final approval layer after deterministic validation.

This layer may approve, reject, request rerun, or request manual review.

## 13. Evidence Boundary

Judge Court Layer output should be recorded as review evidence when implemented in a later phase.

The evidence should include:

- candidate id
- hard gate result
- static score
- semantic review summary
- aggregator recommendation
- CI result
- policy result
- final authority result

B29A does not implement this evidence record.

## 14. Failure Modes

The Judge Court Layer fails when:

- LLM review becomes final authority
- hard gates are treated as optional
- CI failure is ignored
- policy denial is ignored
- semantic quality is confused with execution safety
- candidate ranking hides missing tests
- recommendation is treated as acceptance
- merge happens without post-merge validation

## 15. Non-Goals

B29A does not add:

- judge runtime
- model router
- LLM evaluation worker
- merge bot
- deployment bot
- policy execution change
- CI workflow change
- production service
- B30 external witness receipt implementation

## 16. Current Phase Boundary

B29A records Judge Court Layer boundaries only.

Implementation belongs to later scoped phases.
