# Credibility-Bonded Evidence Oracle

A standalone GenLayer Intelligent Contract primitive for verifying evidence-backed claims.

The contract lets builders submit a claim, attach an evidence URL, declare a bond commitment, and resolve the claim through GenLayer consensus. Validators independently read the same evidence and classify the claim as `supported`, `contradicted`, `unverifiable`, or `stale`.

## Why This Needs GenLayer

Many builder workflows need a judgment that is too subjective for a deterministic smart contract but too important to leave to a private backend. Examples include grant milestone checks, bounty proof review, reputation attestations, DAO proposal evidence, content provenance, and data-quality assertions.

This contract keeps that judgment on-chain and auditable:

- The contract stores the claim, evidence URL, declared bond commitment, status, verdict, confidence bucket, and material facts.
- The final verdict is produced by GenLayer consensus, not by the submitter.
- Validators rerun the evidence analysis independently and compare stable fields.
- The state transition is minimal and reusable, so other apps can build around it.

## Contract Boundary

The frontend or backend owns UI, indexing, user accounts, cached previews, and analytics.

The external website owns the raw evidence.

The GenLayer contract owns the authoritative state transition from `submitted` to `resolved`, including the consensus-backed verdict and review metadata.

## State Machine

`submitted`
: A claim has been registered with claim text, evidence URL, and a declared bond commitment.

`resolved`
: Consensus produced a verdict, confidence bucket, summary, and material facts.

`challenged`
: The submitter or owner has supplied replacement evidence and requested another review. Previous verdict fields are cleared so consumers cannot accidentally treat the old result as applying to the new evidence.

`archived`
: The owner closed the claim while preserving historical read access.

## Verdicts

- `supported`: the evidence directly supports the claim.
- `contradicted`: the evidence materially conflicts with the claim.
- `unverifiable`: the evidence is missing, ambiguous, unrelated, or insufficient.
- `stale`: the evidence is outdated for a time-sensitive claim.

Confidence is stored as `high`, `medium`, or `low` instead of raw scores. Buckets are more stable for validator agreement.

## Consensus Design

Resolution uses `gl.vm.run_nondet_unsafe`.

The leader:

1. Fetches the evidence URL.
2. Sends the claim and evidence text to an LLM with `response_format="json"`.
3. Normalizes the verdict, confidence bucket, summary, and material facts.

The validator:

1. Reruns the same evidence fetch and LLM analysis independently.
2. Requires exact verdict agreement.
3. Allows confidence to differ by one adjacent bucket, except when either side is `low`.
4. Requires at least two material facts and enough overlap to show both outputs relied on the same evidence.

This is not a schema-only validator. A leader cannot win consensus merely by returning valid JSON; validators perform their own substantive analysis.

## Public Methods

`submit_claim(claim_id, claim_text, evidence_url, declared_bond_atto, submitted_at)`
: Registers a new claim. The claim text must be meaningful, the URL must be HTTP(S), the declared bond commitment must meet the minimum, and IDs cannot be reused.

## Bond Semantics

`declared_bond_atto` is explicit stake metadata, not token escrow. The contract records and enforces a minimum declared commitment so reviewers and integrating apps can reason about spam resistance. A production deployment that needs real slashing should pair this primitive with token escrow or a payment contract and call this oracle only after escrow has been locked.

`resolve_claim(claim_id, resolved_at)`
: Runs GenLayer consensus and stores the verdict.

`challenge_claim(claim_id, new_evidence_url)`
: Lets the submitter or owner move a resolved claim back into review with new evidence.

`archive_claim(claim_id)`
: Lets the owner archive a claim.

`get_claim(claim_id)`
: Returns all claim metadata.

`get_claim_count()`
: Returns the number of submitted claims.

## Error Handling

The contract uses explicit error prefixes:

- `[EXPECTED]`: deterministic business rule failures.
- `[EXTERNAL]`: stable external failures such as a 404.
- `[TRANSIENT]`: temporary network or server failures.
- `[LLM_ERROR]`: malformed or unusable LLM output.

Validators compare expected and external failures exactly, accept transient agreement only when both sides hit transient failures, and reject LLM errors to force rotation.

## Files

- `contracts/credibility_bonded_evidence_oracle.py`: GenLayer contract source.
- `tests/test_contract_source.ps1`: local source-quality tests.
- `SUBMISSION.md`: portal-ready contribution copy.
- `tweet.md`: English tweet draft for the quest.
- `docs/superpowers/specs/2026-08-21-credibility-bonded-evidence-oracle-design.md`: design spec.
- `docs/superpowers/plans/2026-08-21-credibility-oracle-implementation.md`: implementation plan.

## Local Verification

Run:

```powershell
powershell -ExecutionPolicy Bypass -File tests/test_contract_source.ps1
```

Expected:

```text
Contract source checks passed.
```

The local test checks the pinned runner header, forbidden runner aliases, expected public methods, helper functions, verdict constants, confidence constants, `run_nondet_unsafe` usage, challenge clearing, declared bond semantics, and material fact thresholds.

## GenVM Lint

The contract is written for `genvm-lint check contracts/credibility_bonded_evidence_oracle.py`, but this machine currently does not expose `python`, `pytest`, or `genvm-lint` in PATH. Before deployment, run GenVM lint in a GenLayer-ready environment:

```bash
genvm-lint check contracts/credibility_bonded_evidence_oracle.py
```

## Integration Test Plan

In GenLayer Studio or a configured GenLayer environment:

1. Deploy with a nonzero `minimum_bond_atto`.
2. Submit a claim with a stable public evidence URL.
3. Resolve the claim and confirm validators agree on verdict and confidence.
4. Challenge the claim with stronger or newer evidence.
5. Resolve again and confirm `review_count` increments and state remains readable.

Recommended test claims:

- Supported milestone claim with an official release note as evidence.
- Contradicted claim where evidence says the opposite.
- Unverifiable claim with an unrelated evidence URL.
- Stale claim with old evidence for a time-sensitive statement.
