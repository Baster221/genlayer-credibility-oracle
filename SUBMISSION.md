# GenLayer Portal Submission

## Title

Credibility-Bonded Evidence Oracle

## Short Description

A reusable GenLayer Intelligent Contract primitive for verifying evidence-backed claims through independent validator consensus.

## Suggested Portal Body

I built a standalone GenLayer Intelligent Contract called **Credibility-Bonded Evidence Oracle**.

The contract lets builders submit a claim, attach an evidence URL, commit a bond amount, and resolve the claim through GenLayer consensus. The output is an auditable verdict: `supported`, `contradicted`, `unverifiable`, or `stale`, plus a confidence bucket, concise rationale, and material facts.

This is designed as a reusable primitive, not a one-off demo. It can support grant milestone checks, bounty proof review, DAO proposal evidence, reputation attestations, content provenance, and data-quality assertions.

The strongest part of the contract is the validator design. Resolution uses `gl.vm.run_nondet_unsafe`; the validator does not merely check JSON shape. It independently fetches the evidence, reruns the LLM analysis, and compares stable fields: exact verdict agreement, confidence bucket tolerance, and material fact overlap.

Files included:

- `contracts/credibility_bonded_evidence_oracle.py`
- `README.md`
- `tests/test_contract_source.ps1`
- `docs/superpowers/specs/2026-08-21-credibility-bonded-evidence-oracle-design.md`
- `docs/superpowers/plans/2026-08-21-credibility-oracle-implementation.md`

Local verification completed:

```text
powershell -ExecutionPolicy Bypass -File tests/test_contract_source.ps1
Contract source checks passed.
```

GenVM lint note: this local Windows environment does not currently expose `python`, `pytest`, or `genvm-lint` in PATH, so I included the intended lint command and integration test plan in the README for reviewers/builders to run in a GenLayer-ready environment.

## Consensus Explanation

The contract uses GenLayer where it matters: converting subjective, external evidence into a state-changing verdict. Validators independently perform the same evidence analysis and compare normalized decision fields. This makes the primitive useful for other apps that need transparent, appealable, and auditable evidence review.

## Recommended Evidence Link

Use the public GitHub repository URL after publishing this project.

## Tags

GenLayer, Intelligent Contract, Oracle, Evidence Verification, Consensus, Builder Primitive
