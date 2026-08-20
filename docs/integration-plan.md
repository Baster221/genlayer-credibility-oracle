# Integration Plan

This plan describes how a builder can integrate `CredibilityBondedEvidenceOracle` into a larger application.

## Pattern: Evidence Gate

1. Application collects a user claim.
2. Application collects one public evidence URL.
3. Application optionally locks real stake or escrow off-chain or in another contract.
4. Application calls `submit_claim`.
5. Application calls `resolve_claim`.
6. Application reads `get_claim`.
7. Application executes its own policy based on verdict and confidence.

## Example Policies

Grant milestone:

```text
Pay next tranche when verdict == supported and confidence == high.
Send to manual review when verdict == unverifiable.
Reject when verdict == contradicted or stale.
```

Bounty proof:

```text
Accept proof when verdict == supported.
Allow one challenge with stronger evidence.
Escalate low-confidence results.
```

DAO proposal evidence:

```text
Display oracle result next to proposal evidence.
Warn voters when evidence is stale or unverifiable.
```

## Deployment Checklist

1. Run `genvm-lint check contracts/credibility_bonded_evidence_oracle.py`.
2. Deploy with a nonzero `minimum_bond_atto`.
3. Submit one supported test claim.
4. Submit one unverifiable test claim.
5. Challenge one resolved claim and verify old verdict fields clear.
6. Document deployed address and transaction hash in this file if publishing live evidence.

## Suggested Constructor

```text
minimum_bond_atto = 1000000000000000000
```

That value is a declared commitment floor. It does not transfer funds by itself.

## Suggested Demo Evidence

Use stable sources that validators can fetch repeatedly:

- official release pages
- GitHub release tags
- documentation pages
- project blog announcements
- governance proposal pages

Avoid:

- login-only pages
- social feeds that change rapidly
- screenshots without source URLs
- pages that block automated fetches
