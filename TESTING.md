# Testing Guide

## Local Source Check

Run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File tests/test_contract_source.ps1
```

Expected output:

```text
Contract source checks passed.
```

This check verifies:

- pinned `py-genlayer` runner header
- no `py-genlayer:test`
- no `py-genlayer:latest`
- expected contract class
- `gl.vm.run_nondet_unsafe` usage
- independent validator re-analysis
- helper functions
- public methods
- all verdict values
- all confidence buckets
- declared bond semantics
- challenge clearing of old verdict fields
- minimum material fact threshold

## GenVM Lint

In a GenLayer-ready Python environment:

```bash
pip install -r requirements-dev.txt
genvm-lint check contracts/credibility_bonded_evidence_oracle.py
```

`genvm-lint check` should be treated as the authoritative static validation before deployment.

## Live Integration Tests

Use GenLayer Studio or studionet.

Recommended cases:

1. **Supported claim**
   - Claim: a project shipped a named release.
   - Evidence: official release notes or repository tag page.
   - Expected verdict: `supported`.

2. **Contradicted claim**
   - Claim: a page states one value.
   - Evidence: the page clearly states a conflicting value.
   - Expected verdict: `contradicted`.

3. **Unverifiable claim**
   - Claim: a broad or private assertion.
   - Evidence: unrelated or insufficient public page.
   - Expected verdict: `unverifiable`.

4. **Stale claim**
   - Claim: a time-sensitive status.
   - Evidence: old page or outdated announcement.
   - Expected verdict: `stale`.

5. **Challenge flow**
   - Resolve a claim.
   - Challenge it with a new evidence URL.
   - Confirm old verdict fields are cleared.
   - Resolve again and confirm `review_count` increments.

## What Not to Assert

Do not assert exact LLM prose. The contract intentionally stores human-readable summaries, but consensus depends on normalized verdict, confidence, and material facts.

Good tests assert state invariants:

- status transitions
- verdict enum values
- review count increments
- challenged claims clear old verdict data
- invalid claims revert before consensus
- supported/contradicted/unverifiable/stale cases produce valid verdicts
