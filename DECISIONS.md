# Engineering Decisions

This document explains the contract design choices that matter for reviewers and builders.

## 1. One Primitive, Not a Catalog

This repository intentionally focuses on one strong primitive: evidence-backed claim verification. A larger catalog can be impressive, but a single contract with a clear boundary is easier to audit, reuse, and deploy.

## 2. Custom Validator Instead of Exact Equality

The contract evaluates web evidence with LLM assistance. Exact byte equality would make consensus fragile because independent model outputs can use different words while reaching the same decision.

The contract therefore uses `gl.vm.run_nondet_unsafe` and defines equivalence in code:

- exact verdict agreement
- compatible confidence buckets
- material fact overlap

This preserves a stable state transition without pretending LLM prose is deterministic.

## 3. Validator Reruns the Evidence Analysis

The validator does not merely check that the leader returned valid JSON. It performs the same substantive task independently.

That matters because format validation would let the leader decide alone. Independent re-analysis makes the validator a real participant in consensus.

## 4. Material Facts Are Compared, Not Summaries

Summaries are useful for human review but poor consensus fields. Two valid summaries may use different wording.

Material facts are better comparison anchors. The contract requires at least two facts and checks overlap between the leader and validator facts. This forces both sides to ground the verdict in similar evidence.

## 5. Confidence Uses Buckets

Raw numerical confidence is noisy. A model returning `82` and another returning `76` should not necessarily fail consensus.

The contract stores `high`, `medium`, and `low`. Validators allow adjacent disagreement only when neither side is `low`. Low-confidence outputs must agree exactly because they signal uncertainty.

## 6. `unverifiable` and `stale` Are First-Class Verdicts

The contract does not force every evidence review into true or false.

`unverifiable` prevents weak or unrelated evidence from becoming a false positive. `stale` lets the oracle reject outdated evidence for time-sensitive claims.

## 7. Declared Bond, Not Escrow

`declared_bond_atto` is stake metadata, not token custody.

This keeps the contract standalone for the Intelligent Contracts category. A production application that needs real slashing can pair this primitive with a separate escrow/payment contract and call the oracle only after funds are locked.

## 8. Challenge Clears Old Verdict Fields

When a claim is challenged with new evidence, the contract clears the previous verdict, confidence, summary, facts, and resolution label.

This prevents clients from accidentally treating old consensus output as if it applies to the new evidence URL.

## 9. Caller-Provided Time Labels

`submitted_at` and `resolved_at` are labels supplied by the caller. They are not treated as authoritative block timestamps.

The contract keeps them for readable review trails while avoiding assumptions about runtime clock support.

## 10. Source-Quality Test as Local Baseline

This environment did not expose Python or `genvm-lint` in PATH when the repository was prepared. The repository therefore includes a PowerShell source-quality test that can run locally now, plus instructions for `genvm-lint` in a GenLayer-ready environment.

The PowerShell test is not a replacement for GenVM lint or live consensus tests. It is a baseline guard for the requirements most likely to regress in this artifact.
