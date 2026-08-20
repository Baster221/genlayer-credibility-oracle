# Contract Specification

## CredibilityBondedEvidenceOracle

`CredibilityBondedEvidenceOracle` is a reusable GenLayer Intelligent Contract for resolving whether public evidence supports a submitted claim.

The primitive is useful when a builder needs an auditable judgment over external evidence but does not want a private server to be the final authority.

## Purpose

Accept a claim and evidence URL, run GenLayer consensus over the evidence, and persist a stable verdict that downstream applications can read.

Example use cases:

- Grant milestone checks.
- Bounty proof review.
- DAO proposal evidence review.
- Reputation attestations.
- Content provenance.
- Dataset or documentation quality checks.

## Consensus Move

The contract uses custom adjudication with:

```python
gl.vm.run_nondet_unsafe(analyze_evidence, validator_fn)
```

This is used instead of `strict_eq` because LLM analysis over web evidence is not byte-deterministic. It is also used instead of a schema-only validator because the validator must verify the substance of the result.

## Validator Principle

The leader and validator independently perform the evidence analysis.

A result is equivalent only if:

1. The normalized verdict is identical.
2. Confidence buckets are compatible.
3. At least two material facts overlap.

The summary is stored for humans but is not compared exactly. Exact prose comparison would make consensus brittle without improving the reliability of the state transition.

## State

Each claim stores:

- `submitter`
- `claim_text`
- `evidence_url`
- `declared_bond_atto`
- `status`
- `verdict`
- `confidence`
- `summary`
- `material_facts_json`
- `submitted_at`
- `resolved_at`
- `review_count`
- `challenged_by`

The global state also stores:

- `owner`
- `minimum_bond_atto`
- `claim_count`
- `claims`
- `claim_ids`

## Lifecycle

`submitted`
: The claim has been registered and is awaiting consensus resolution.

`resolved`
: GenLayer consensus produced a verdict and supporting metadata.

`challenged`
: A resolved claim was reopened with a replacement evidence URL. Previous verdict fields are cleared so readers cannot confuse old results with the new evidence.

`archived`
: The owner archived the claim while preserving read access.

## Public API

### `submit_claim(claim_id, claim_text, evidence_url, declared_bond_atto, submitted_at)`

Registers a new claim.

Validation:

- `claim_id` must be non-empty.
- `claim_text` must be at least 20 characters.
- `evidence_url` must start with `http://` or `https://`.
- `declared_bond_atto` must be greater than or equal to `minimum_bond_atto`.
- `claim_id` cannot already exist.

### `resolve_claim(claim_id, resolved_at)`

Runs GenLayer consensus and stores the verdict.

Allowed when status is:

- `submitted`
- `challenged`

### `challenge_claim(claim_id, new_evidence_url)`

Allows the submitter or contract owner to reopen a resolved claim with new evidence.

The method clears:

- `verdict`
- `confidence`
- `summary`
- `material_facts_json`
- `resolved_at`

### `archive_claim(claim_id)`

Allows the owner to archive a claim.

### `get_claim(claim_id)`

Returns all claim metadata.

### `get_claim_count()`

Returns the number of submitted claims.

## Verdicts

- `supported`: evidence directly supports the claim.
- `contradicted`: evidence materially conflicts with the claim.
- `unverifiable`: evidence is missing, ambiguous, unrelated, or insufficient.
- `stale`: evidence is outdated for a time-sensitive claim.

## Error Classes

- `[EXPECTED]`: deterministic business rule failure.
- `[EXTERNAL]`: stable external failure such as a permanent 404.
- `[TRANSIENT]`: temporary network or server failure.
- `[LLM_ERROR]`: malformed or unusable model output.

## Reuse Shape

Downstream builders can treat the oracle as an evidence gate:

1. Submit claim and evidence.
2. Resolve through consensus.
3. Read verdict.
4. Execute app-specific behavior only when the verdict meets policy.

Examples:

- Pay a bounty only if `verdict == "supported"`.
- Mark a grant milestone complete only if `verdict == "supported"` and `confidence == "high"`.
- Route a dispute to manual review when `verdict == "unverifiable"`.
- Reject stale evidence in governance or reporting workflows.
