# Credibility-Bonded Evidence Oracle Design

## Goal

Build a standalone GenLayer Intelligent Contract that other builders can reuse as a primitive for verifying evidence-backed claims. The contract accepts a claim, an evidence URL, and a submitter bond, then uses GenLayer consensus to classify whether the evidence supports the claim.

This is intentionally not a full frontend product. The contract owns the minimum state transition that benefits from GenLayer: turning subjective external evidence into an auditable on-chain verdict.

## Use Case

Builders can use this oracle for grant milestone checks, reputation attestations, bounty proofs, data-quality assertions, DAO proposals, and content provenance workflows. A caller submits a claim such as "Project X shipped the documented milestone" with an evidence URL. Validators independently inspect the evidence and agree on a stable verdict.

## Contract Boundary

Frontend or backend owns user interface, indexing, account analytics, and non-authoritative preview scoring.

External sources own the raw evidence documents or web pages.

The GenLayer contract owns claim state, submitter bond tracking, consensus-backed verdict assignment, review metadata, recheck lifecycle, and deterministic state transitions after consensus.

## State Model

Each claim stores an ID, submitter, claim text, evidence URL, bond amount, status, verdict, confidence bucket, summary, material facts, timestamps, and review count.

The lifecycle is:

1. `submitted`: claim is registered with a bond.
2. `resolved`: consensus produced a stable verdict.
3. `challenged`: owner or submitter requests a recheck with new evidence.
4. `archived`: claim is no longer active but remains readable.

Verdicts are `supported`, `contradicted`, `unverifiable`, and `stale`.

Confidence buckets are `high`, `medium`, and `low`; buckets are used instead of raw scores to make validator comparison more stable.

## Consensus Logic

Resolution uses `gl.vm.run_nondet_unsafe` with a leader function and a validator function.

The leader fetches the evidence URL, extracts readable text, asks an LLM for a JSON verdict, normalizes the response, and returns only stable fields: verdict, confidence bucket, material facts, and summary.

The validator reruns the same analysis independently, then compares stable decision fields:

- Verdict must match exactly.
- Confidence may differ by one adjacent bucket, unless either side is `low`.
- Material facts must overlap enough to prove both analyses relied on similar evidence.
- Summary is stored for humans but is not used as an exact consensus field.

The validator does not accept leader output based only on JSON shape. It performs its own evidence fetch and LLM analysis, then compares the substance of the result.

## Error Handling

Errors are classified with explicit prefixes:

- `[EXPECTED]`: deterministic business rule failure, such as duplicate IDs.
- `[EXTERNAL]`: stable external input failure, such as a permanent 404.
- `[TRANSIENT]`: temporary network or server failure.
- `[LLM_ERROR]`: malformed or unusable model output.

Validators agree on deterministic and external failures only when messages match. Transient errors agree only when both sides hit a transient failure. LLM errors force disagreement so consensus can rotate.

## Files

- `contracts/credibility_bonded_evidence_oracle.py`: main contract.
- `README.md`: purpose, consensus boundary, state machine, usage examples, and submission notes.
- `tests/test_direct_contract.py`: direct-mode oriented unit tests for deterministic helpers and state assumptions.
- `SUBMISSION.md`: concise copy for the GenLayer portal.
- `tweet.md`: polished English tweet draft aimed at attracting creator attention with positive feedback.

## Testing

The implementation should include direct tests for normalization, verdict comparison, confidence comparison, duplicate IDs, and input validation. Full consensus with live web and LLM calls is documented as an integration test path because it requires a GenLayer runtime environment.

The contract must start with a pinned GenVM runner header and must not use `py-genlayer:test`, `py-genlayer:latest`, or unversioned `py-genlayer`.
