# Credibility-Bonded Evidence Oracle

A GenLayer Intelligent Contract primitive for turning messy public evidence into auditable on-chain claim verdicts.

## Thesis

Most useful claims in builder ecosystems are not clean yes/no values. A grant milestone might be partially shipped. A bounty proof might be real but incomplete. A DAO proposal might cite evidence that is accurate but stale. Traditional smart contracts are excellent at deterministic accounting, but they cannot judge whether public evidence actually supports a human claim.

This repository explores one reusable shape for that gap:

> Evidence review should be a consensus primitive, not a private backend opinion.

`CredibilityBondedEvidenceOracle` lets a builder submit a claim, attach an evidence URL, declare a stake commitment, and ask GenLayer validators to resolve the claim as `supported`, `contradicted`, `unverifiable`, or `stale`.

The contract is intentionally standalone. It is not a frontend, not a finished app, and not a generic "AI decides X" example. The core contribution is the contract boundary: non-deterministic evidence judgment happens through GenLayer consensus, while state transitions remain explicit and inspectable.

## What Makes It a Primitive

- **Reusable shape:** any app can wrap the oracle for milestone checks, bounty review, DAO evidence, reputation attestations, provenance, or data-quality claims.
- **Real consensus logic:** resolution uses `gl.vm.run_nondet_unsafe` with a validator that independently repeats the evidence analysis.
- **Clear state model:** claims move through `submitted`, `resolved`, `challenged`, and `archived`.
- **Stable comparison fields:** validators compare verdict, confidence bucket, and material fact overlap instead of raw LLM prose.
- **Fail-safe categories:** the contract can return `unverifiable` or `stale` instead of forcing a weak yes/no answer.
- **Standalone deployability:** the contract is one GenVM Python file with a pinned runner dependency.

## Reviewer Links

- [Contract source](contracts/credibility_bonded_evidence_oracle.py)
- [Contract specification](CONTRACT.md)
- [Engineering decisions](DECISIONS.md)
- [Testing guide](TESTING.md)
- [Reviewer guide](docs/reviewer-guide.md)
- [Integration plan](docs/integration-plan.md)
- [Source-quality test](tests/test_contract_source.ps1)

## Contract at a Glance

| Area | Design |
| --- | --- |
| Contract | `CredibilityBondedEvidenceOracle` |
| Source | `contracts/credibility_bonded_evidence_oracle.py` |
| Consensus move | Custom validator with `gl.vm.run_nondet_unsafe` |
| Primary input | Claim text + evidence URL |
| Output | Verdict, confidence bucket, summary, material facts |
| Verdicts | `supported`, `contradicted`, `unverifiable`, `stale` |
| Lifecycle | `submitted` -> `resolved`; optional `challenged`; optional `archived` |
| Bond model | Declared stake metadata, not token escrow |

## How Consensus Is Used

The leader function fetches the evidence URL and asks an LLM to classify whether the evidence supports the claim. It returns normalized fields only:

- `verdict`
- `confidence`
- `summary`
- `material_facts`

The validator does not trust the leader's JSON shape. It independently fetches the same evidence, reruns the analysis, and compares stable fields:

1. Verdict must match exactly.
2. Confidence may differ by one adjacent bucket, except when either side is `low`.
3. At least two material facts must overlap enough to show both analyses relied on the same evidence.

That makes disagreement useful. If validators cannot independently arrive at a compatible result, the contract does not silently accept the leader's answer.

## Repository Layout

```text
genlayer-credibility-oracle/
├── README.md
├── CONTRACT.md
├── DECISIONS.md
├── TESTING.md
├── LICENSE
├── gltest.config.yaml
├── requirements-dev.txt
├── contracts/
│   └── credibility_bonded_evidence_oracle.py
├── docs/
│   ├── integration-plan.md
│   ├── reviewer-guide.md
│   └── superpowers/
│       ├── plans/
│       └── specs/
└── tests/
    └── test_contract_source.ps1
```

The `docs/superpowers` directory records the design and implementation trail. The public review documents are `CONTRACT.md`, `DECISIONS.md`, `TESTING.md`, and the files under `docs/`.

## Quick Verification

On Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File tests/test_contract_source.ps1
```

Expected output:

```text
Contract source checks passed.
```

The local script checks the pinned runner header, forbidden runner aliases, expected public methods, helper functions, verdict constants, confidence constants, `run_nondet_unsafe` usage, challenge clearing, declared bond semantics, and material fact thresholds.

## GenLayer Verification

In a GenLayer-ready environment, run:

```bash
pip install -r requirements-dev.txt
genvm-lint check contracts/credibility_bonded_evidence_oracle.py
```

For live behavior, deploy to GenLayer Studio or studionet and follow [docs/integration-plan.md](docs/integration-plan.md).

## Status

Built as a standalone Intelligent Contract submission artifact. Local source-quality checks pass. GenVM lint and live consensus testing should be run in a GenLayer environment before production use.
