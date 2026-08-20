# Credibility Oracle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a submission-ready standalone GenLayer Intelligent Contract for an evidence-backed claim oracle.

**Architecture:** The contract is a single GenLayer Python file with small deterministic helper functions for normalization and validator comparison. Tests exercise helpers and source quality without requiring a live GenLayer runtime. Documentation explains consensus boundaries and gives portal-ready submission copy.

**Tech Stack:** GenLayer Python contract, pinned `py-genlayer` runner, PowerShell source-quality tests for local verification, Markdown documentation.

## Global Constraints

- Contract first line must be `# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }`.
- Contract must not contain `py-genlayer:test`, `py-genlayer:latest`, or unversioned `py-genlayer`.
- Consensus must use `gl.vm.run_nondet_unsafe` with an independent validator, not schema-only validation.
- Verdicts are `supported`, `contradicted`, `unverifiable`, and `stale`.
- Confidence buckets are `high`, `medium`, and `low`.
- Keep the artifact standalone; no frontend app.

---

### Task 1: Deterministic Helper Tests

**Files:**
- Create: `tests/test_contract_source.ps1`

**Interfaces:**
- Consumes: `contracts/credibility_bonded_evidence_oracle.py` as source text.
- Produces: source-level tests for dependency header, forbidden aliases, public methods, helper names, and consensus API usage.

- [ ] **Step 1: Write failing source tests**

Create `tests/test_contract_source.ps1` with tests for pinned runner, forbidden aliases, expected helper functions, public write/view methods, and `run_nondet_unsafe`.

- [ ] **Step 2: Run test to verify it fails**

Run: `powershell -ExecutionPolicy Bypass -File tests/test_contract_source.ps1`
Expected: FAIL because the contract file does not exist.

- [ ] **Step 3: Commit**

Run: `git add tests/test_contract_source.ps1 && git commit -m "test: add contract source quality checks"`.

### Task 2: Contract Implementation

**Files:**
- Create: `contracts/credibility_bonded_evidence_oracle.py`
- Test: `tests/test_contract_source.ps1`

**Interfaces:**
- Produces: `CredibilityBondedEvidenceOracle` contract, helper functions `_normalize_verdict`, `_normalize_confidence`, `_confidence_distance`, `_facts_overlap_enough`, `_results_equivalent`, `_parse_analysis`, `_handle_leader_error`, public methods `submit_claim`, `resolve_claim`, `challenge_claim`, `archive_claim`, `get_claim`, `get_claim_count`.

- [ ] **Step 1: Implement contract**

Write the GenLayer contract with pinned runner header, storage dataclass, claim lifecycle methods, `run_nondet_unsafe` consensus resolution, defensive LLM parsing, web fetch error classification, and independent validator comparison.

- [ ] **Step 2: Run source tests**

Run: `powershell -ExecutionPolicy Bypass -File tests/test_contract_source.ps1`
Expected: PASS.

- [ ] **Step 3: Run GenVM lint if available**

Run: `genvm-lint check contracts/credibility_bonded_evidence_oracle.py`
Expected: PASS. If `genvm-lint` is not installed or runner dependencies are unavailable, record that limitation in `SUBMISSION.md`.

- [ ] **Step 4: Commit**

Run: `git add contracts/credibility_bonded_evidence_oracle.py tests/test_contract_source.ps1 && git commit -m "feat: add credibility bonded evidence oracle"`.

### Task 3: Documentation and Submission Copy

**Files:**
- Create: `README.md`
- Create: `SUBMISSION.md`
- Create: `tweet.md`

**Interfaces:**
- Consumes: implemented contract behavior and quest criteria.
- Produces: reviewer-facing explanation, portal-ready contribution copy, and an English tweet draft.

- [ ] **Step 1: Write README**

Document purpose, why GenLayer consensus is needed, state machine, verdict semantics, validator principle, methods, local tests, and integration test plan.

- [ ] **Step 2: Write submission copy**

Create `SUBMISSION.md` with title, summary, artifact paths, consensus explanation, tests, and suggested portal fields.

- [ ] **Step 3: Write tweet**

Create `tweet.md` with one polished English post aimed at GenLayer creators, including a positive opinion, constructive positive feedback, and an upbeat close.

- [ ] **Step 4: Run verification**

Run: `powershell -ExecutionPolicy Bypass -File tests/test_contract_source.ps1`, `git status --short`, and inspect docs for placeholders.

- [ ] **Step 5: Commit**

Run: `git add README.md SUBMISSION.md tweet.md && git commit -m "docs: add submission package and tweet draft"`.

## Self-Review

Spec coverage: the tasks cover contract source, consensus logic, state model, error handling, tests, README, submission copy, and tweet copy.

Placeholder scan: no task depends on TODO/TBD content.

Type consistency: helper and method names in Task 2 are the same names tested and documented in Tasks 1 and 3.
