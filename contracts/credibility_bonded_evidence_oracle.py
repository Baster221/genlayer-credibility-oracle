# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


ERROR_EXPECTED = "[EXPECTED]"
ERROR_EXTERNAL = "[EXTERNAL]"
ERROR_TRANSIENT = "[TRANSIENT]"
ERROR_LLM = "[LLM_ERROR]"

STATUS_SUBMITTED = "submitted"
STATUS_RESOLVED = "resolved"
STATUS_CHALLENGED = "challenged"
STATUS_ARCHIVED = "archived"

VERDICT_SUPPORTED = "supported"
VERDICT_CONTRADICTED = "contradicted"
VERDICT_UNVERIFIABLE = "unverifiable"
VERDICT_STALE = "stale"

CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"


@allow_storage
@dataclass
class ClaimRecord:
    submitter: Address
    claim_text: str
    evidence_url: str
    declared_bond_atto: u256
    status: str
    verdict: str
    confidence: str
    summary: str
    material_facts_json: str
    submitted_at: str
    resolved_at: str
    review_count: u256
    challenged_by: Address


def _clean_text(value: str, max_len: int) -> str:
    text = str(value or "").strip()
    if len(text) > max_len:
        return text[:max_len].strip()
    return text


def _normalize_verdict(value: str) -> str:
    raw = str(value or "").strip().lower().replace("-", "_")
    if raw in ("support", "supported", "true", "valid", "verified"):
        return VERDICT_SUPPORTED
    if raw in ("contradict", "contradicted", "false", "invalid", "refuted"):
        return VERDICT_CONTRADICTED
    if raw in ("stale", "outdated", "expired", "old"):
        return VERDICT_STALE
    if raw in ("unverifiable", "unknown", "unclear", "insufficient", "not_enough_evidence"):
        return VERDICT_UNVERIFIABLE
    raise gl.vm.UserError(f"{ERROR_LLM} Unsupported verdict: {value}")


def _normalize_confidence(value: str) -> str:
    raw = str(value or "").strip().lower()
    if raw in ("high", "strong", "certain", "0.8", "0.9", "1.0"):
        return CONFIDENCE_HIGH
    if raw in ("medium", "moderate", "mixed", "0.5", "0.6", "0.7"):
        return CONFIDENCE_MEDIUM
    if raw in ("low", "weak", "uncertain", "0.1", "0.2", "0.3", "0.4"):
        return CONFIDENCE_LOW

    try:
        score = int(str(raw).strip())
        if score >= 75:
            return CONFIDENCE_HIGH
        if score >= 45:
            return CONFIDENCE_MEDIUM
        return CONFIDENCE_LOW
    except Exception:
        raise gl.vm.UserError(f"{ERROR_LLM} Unsupported confidence: {value}")


def _confidence_distance(left: str, right: str) -> int:
    ranks = {
        CONFIDENCE_LOW: 0,
        CONFIDENCE_MEDIUM: 1,
        CONFIDENCE_HIGH: 2,
    }
    return abs(ranks[_normalize_confidence(left)] - ranks[_normalize_confidence(right)])


def _tokenize_fact(fact: str) -> set[str]:
    normalized = ""
    for char in str(fact or "").lower():
        if char.isalnum() or char == " ":
            normalized += char
        else:
            normalized += " "
    return set(part for part in normalized.split(" ") if len(part) >= 4)


def _facts_overlap_enough(left_facts: list[str], right_facts: list[str]) -> bool:
    if len(left_facts) < 2 or len(right_facts) < 2:
        return False

    matched = 0
    for left in left_facts:
        left_tokens = _tokenize_fact(left)
        if len(left_tokens) == 0:
            continue
        for right in right_facts:
            right_tokens = _tokenize_fact(right)
            if len(right_tokens) == 0:
                continue
            overlap = left_tokens.intersection(right_tokens)
            smaller = min(len(left_tokens), len(right_tokens))
            if smaller > 0 and len(overlap) * 2 >= smaller:
                matched += 1
                break

    required = 2
    return matched >= required


def _results_equivalent(leader: dict, validator: dict) -> bool:
    leader_verdict = _normalize_verdict(str(leader.get("verdict", "")))
    validator_verdict = _normalize_verdict(str(validator.get("verdict", "")))
    if leader_verdict != validator_verdict:
        return False

    leader_confidence = _normalize_confidence(str(leader.get("confidence", "")))
    validator_confidence = _normalize_confidence(str(validator.get("confidence", "")))
    if leader_confidence == CONFIDENCE_LOW or validator_confidence == CONFIDENCE_LOW:
        if leader_confidence != validator_confidence:
            return False
    elif _confidence_distance(leader_confidence, validator_confidence) > 1:
        return False

    leader_facts = leader.get("material_facts", [])
    validator_facts = validator.get("material_facts", [])
    if not isinstance(leader_facts, list) or not isinstance(validator_facts, list):
        return False
    return _facts_overlap_enough(leader_facts, validator_facts)


def _parse_analysis(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise gl.vm.UserError(f"{ERROR_LLM} LLM returned non-object analysis")

    verdict = _normalize_verdict(str(raw.get("verdict", raw.get("decision", ""))))
    confidence = _normalize_confidence(str(raw.get("confidence", raw.get("confidence_bucket", ""))))
    summary = _clean_text(str(raw.get("summary", raw.get("rationale", ""))), 700)
    if len(summary) == 0:
        raise gl.vm.UserError(f"{ERROR_LLM} Missing summary")

    facts_raw = raw.get("material_facts", raw.get("facts", []))
    if not isinstance(facts_raw, list):
        raise gl.vm.UserError(f"{ERROR_LLM} material_facts must be a list")

    facts: list[str] = []
    for fact in facts_raw:
        clean = _clean_text(str(fact), 220)
        if len(clean) > 0:
            facts.append(clean)
        if len(facts) == 5:
            break

    if len(facts) < 2:
        raise gl.vm.UserError(f"{ERROR_LLM} At least two material facts are required")

    return {
        "verdict": verdict,
        "confidence": confidence,
        "summary": summary,
        "material_facts": facts,
    }


def _handle_leader_error(leaders_res: gl.vm.Result, leader_fn) -> bool:
    leader_msg = leaders_res.message if hasattr(leaders_res, "message") else ""
    try:
        leader_fn()
        return False
    except gl.vm.UserError as err:
        validator_msg = err.message if hasattr(err, "message") else str(err)
        if validator_msg.startswith(ERROR_EXPECTED) or validator_msg.startswith(ERROR_EXTERNAL):
            return validator_msg == leader_msg
        if validator_msg.startswith(ERROR_TRANSIENT) and leader_msg.startswith(ERROR_TRANSIENT):
            return True
        return False
    except Exception:
        return False


class CredibilityBondedEvidenceOracle(gl.Contract):
    owner: Address
    minimum_bond_atto: u256
    claim_count: u256
    claims: TreeMap[str, ClaimRecord]
    claim_ids: DynArray[str]

    def __init__(self, minimum_bond_atto: u256):
        self.owner = gl.message.sender_account
        self.minimum_bond_atto = minimum_bond_atto
        self.claim_count = u256(0)

    @gl.public.write
    def submit_claim(
        self,
        claim_id: str,
        claim_text: str,
        evidence_url: str,
        declared_bond_atto: u256,
        submitted_at: str,
    ) -> None:
        clean_id = _clean_text(claim_id, 80)
        clean_claim = _clean_text(claim_text, 1200)
        clean_url = _clean_text(evidence_url, 500)

        if len(clean_id) == 0:
            raise gl.UserError(f"{ERROR_EXPECTED} Claim id is required")
        if len(clean_claim) < 20:
            raise gl.UserError(f"{ERROR_EXPECTED} Claim text must be at least 20 characters")
        if not clean_url.startswith("https://") and not clean_url.startswith("http://"):
            raise gl.UserError(f"{ERROR_EXPECTED} Evidence URL must start with http:// or https://")
        if declared_bond_atto < self.minimum_bond_atto:
            raise gl.UserError(f"{ERROR_EXPECTED} Bond below minimum")
        if clean_id in self.claims:
            raise gl.UserError(f"{ERROR_EXPECTED} Claim already exists")

        self.claims[clean_id] = ClaimRecord(
            submitter=gl.message.sender_account,
            claim_text=clean_claim,
            evidence_url=clean_url,
            declared_bond_atto=declared_bond_atto,
            status=STATUS_SUBMITTED,
            verdict="",
            confidence="",
            summary="",
            material_facts_json="[]",
            submitted_at=_clean_text(submitted_at, 80),
            resolved_at="",
            review_count=u256(0),
            challenged_by=Address("0x0000000000000000000000000000000000000000"),
        )
        self.claim_ids.append(clean_id)
        self.claim_count += u256(1)

    @gl.public.write
    def resolve_claim(self, claim_id: str, resolved_at: str) -> None:
        if claim_id not in self.claims:
            raise gl.UserError(f"{ERROR_EXPECTED} Unknown claim")

        claim = self.claims[claim_id]
        if claim.status != STATUS_SUBMITTED and claim.status != STATUS_CHALLENGED:
            raise gl.UserError(f"{ERROR_EXPECTED} Claim is not resolvable")

        def analyze_evidence() -> dict:
            response = gl.nondet.web.get(claim.evidence_url)
            if response.status >= 400 and response.status < 500:
                raise gl.vm.UserError(f"{ERROR_EXTERNAL} Evidence returned {response.status}")
            if response.status >= 500:
                raise gl.vm.UserError(f"{ERROR_TRANSIENT} Evidence temporarily unavailable")

            evidence_text = response.body.decode("utf-8")
            prompt = f"""
You are a validator for a GenLayer evidence oracle.

Claim:
{claim.claim_text}

Evidence text:
{evidence_text[:12000]}

Classify whether the evidence supports the claim.
Return JSON with:
- verdict: one of "supported", "contradicted", "unverifiable", "stale"
- confidence: one of "high", "medium", "low"
- material_facts: 2 to 5 short facts copied or tightly paraphrased from the evidence
- summary: concise rationale for builders and reviewers

Rules:
- Use "supported" only when the evidence directly supports the claim.
- Use "contradicted" when the evidence materially conflicts with the claim.
- Use "unverifiable" when the evidence is missing, ambiguous, or unrelated.
- Use "stale" when the evidence is outdated for a time-sensitive claim.
"""
            analysis = gl.nondet.exec_prompt(prompt, response_format="json")
            return _parse_analysis(analysis)

        def validator_fn(leaders_res: gl.vm.Result) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return _handle_leader_error(leaders_res, analyze_evidence)

            validator_result = analyze_evidence()
            return _results_equivalent(leaders_res.calldata, validator_result)

        result = gl.vm.run_nondet_unsafe(analyze_evidence, validator_fn)
        claim.status = STATUS_RESOLVED
        claim.verdict = result["verdict"]
        claim.confidence = result["confidence"]
        claim.summary = result["summary"]
        claim.material_facts_json = json.dumps(result["material_facts"])
        claim.resolved_at = _clean_text(resolved_at, 80)
        claim.review_count += u256(1)
        self.claims[claim_id] = claim

    @gl.public.write
    def challenge_claim(self, claim_id: str, new_evidence_url: str) -> None:
        if claim_id not in self.claims:
            raise gl.UserError(f"{ERROR_EXPECTED} Unknown claim")

        claim = self.claims[claim_id]
        if claim.status != STATUS_RESOLVED:
            raise gl.UserError(f"{ERROR_EXPECTED} Only resolved claims can be challenged")
        if gl.message.sender_account != claim.submitter and gl.message.sender_account != self.owner:
            raise gl.UserError(f"{ERROR_EXPECTED} Only submitter or owner can challenge")

        clean_url = _clean_text(new_evidence_url, 500)
        if not clean_url.startswith("https://") and not clean_url.startswith("http://"):
            raise gl.UserError(f"{ERROR_EXPECTED} Evidence URL must start with http:// or https://")

        claim.evidence_url = clean_url
        claim.status = STATUS_CHALLENGED
        claim.verdict = ""
        claim.confidence = ""
        claim.summary = ""
        claim.material_facts_json = "[]"
        claim.resolved_at = ""
        claim.challenged_by = gl.message.sender_account
        self.claims[claim_id] = claim

    @gl.public.write
    def archive_claim(self, claim_id: str) -> None:
        if gl.message.sender_account != self.owner:
            raise gl.UserError(f"{ERROR_EXPECTED} Only owner can archive")
        if claim_id not in self.claims:
            raise gl.UserError(f"{ERROR_EXPECTED} Unknown claim")

        claim = self.claims[claim_id]
        claim.status = STATUS_ARCHIVED
        self.claims[claim_id] = claim

    @gl.public.view
    def get_claim(self, claim_id: str) -> dict:
        if claim_id not in self.claims:
            raise gl.UserError(f"{ERROR_EXPECTED} Unknown claim")

        claim = self.claims[claim_id]
        return {
            "id": claim_id,
            "submitter": str(claim.submitter),
            "claim_text": claim.claim_text,
            "evidence_url": claim.evidence_url,
            "declared_bond_atto": claim.declared_bond_atto,
            "status": claim.status,
            "verdict": claim.verdict,
            "confidence": claim.confidence,
            "summary": claim.summary,
            "material_facts": claim.material_facts_json,
            "submitted_at": claim.submitted_at,
            "resolved_at": claim.resolved_at,
            "review_count": claim.review_count,
            "challenged_by": str(claim.challenged_by),
        }

    @gl.public.view
    def get_claim_count(self) -> u256:
        return self.claim_count
