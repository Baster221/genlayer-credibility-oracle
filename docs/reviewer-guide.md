# Reviewer Guide

This guide is for GenLayer reviewers evaluating the repository as an Intelligent Contract submission.

## What to Inspect First

1. `contracts/credibility_bonded_evidence_oracle.py`
2. `CONTRACT.md`
3. `DECISIONS.md`
4. `TESTING.md`

## Why the Contract Is Not a Thin Wrapper

The contract does not accept an LLM answer and store it. It runs a leader analysis and requires validators to independently redo the evidence analysis. The validator compares the result using a contract-defined equivalence rule.

The consensus-critical fields are:

- verdict
- confidence bucket
- material facts

The summary is review metadata, not the consensus anchor.

## State Boundary

The contract owns:

- claim registry
- lifecycle status
- declared stake metadata
- consensus result
- challenge state
- review count

The contract does not own:

- frontend routing
- user identity UI
- off-chain indexing
- token escrow
- source website availability

## Review Questions

Useful questions for evaluating this primitive:

- Does the validator independently verify the substance of the leader output?
- Are non-deterministic outputs normalized before storage?
- Does the state model avoid ambiguous old/new evidence after challenges?
- Can another builder wrap this contract without adopting a specific frontend?
- Does the contract fail safely when evidence is weak or stale?

## Known Limitations

- `declared_bond_atto` is not token escrow.
- Caller-supplied time labels are not authoritative timestamps.
- Live consensus behavior should be tested in GenLayer Studio or studionet.
- The local PowerShell test is a source-quality guard, not a full GenVM validation suite.

## Highlight Potential

The primitive is designed around a recurring builder need: transparent evidence review. It can be reused anywhere a system needs to decide whether public evidence supports an action, without asking users to trust a private backend.
