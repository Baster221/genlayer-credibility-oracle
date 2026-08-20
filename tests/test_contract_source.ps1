$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ContractPath = Join-Path $Root "contracts\credibility_bonded_evidence_oracle.py"
$ExpectedHeader = '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }'

function Assert-True {
    param(
        [bool] $Condition,
        [string] $Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Assert-Contains {
    param(
        [string] $Haystack,
        [string] $Needle,
        [string] $Message
    )

    Assert-True -Condition $Haystack.Contains($Needle) -Message $Message
}

Assert-True -Condition (Test-Path -LiteralPath $ContractPath) -Message "Missing contract file: $ContractPath"

$Source = Get-Content -LiteralPath $ContractPath -Raw
$FirstLine = (Get-Content -LiteralPath $ContractPath -TotalCount 1)

Assert-True -Condition ($FirstLine -eq $ExpectedHeader) -Message "Contract must start with the pinned py-genlayer runner header."
Assert-True -Condition (-not $Source.Contains("py-genlayer:test")) -Message "Contract must not use py-genlayer:test."
Assert-True -Condition (-not $Source.Contains("py-genlayer:latest")) -Message "Contract must not use py-genlayer:latest."
Assert-Contains -Haystack $Source -Needle "class CredibilityBondedEvidenceOracle(gl.Contract):" -Message "Missing contract class."
Assert-Contains -Haystack $Source -Needle "gl.vm.run_nondet_unsafe" -Message "Resolution must use run_nondet_unsafe."
Assert-Contains -Haystack $Source -Needle "validator_fn" -Message "Resolution must define an independent validator function."
Assert-Contains -Haystack $Source -Needle "validator_result = analyze_evidence()" -Message "Validator must rerun analysis independently."
Assert-Contains -Haystack $Source -Needle "declared_bond_atto" -Message "Bond semantics must be explicit as a declared stake commitment."
Assert-Contains -Haystack $Source -Needle "claim.verdict = `"`"" -Message "Challenge flow must clear stale verdict."
Assert-Contains -Haystack $Source -Needle "claim.confidence = `"`"" -Message "Challenge flow must clear stale confidence."
Assert-Contains -Haystack $Source -Needle "claim.summary = `"`"" -Message "Challenge flow must clear stale summary."
Assert-Contains -Haystack $Source -Needle "claim.material_facts_json = `"[]`"" -Message "Challenge flow must clear stale material facts."
Assert-Contains -Haystack $Source -Needle "if len(facts) < 2:" -Message "Analysis parser must require at least two material facts."
Assert-Contains -Haystack $Source -Needle "required = 2" -Message "Fact overlap should require two matches for substantive agreement."

$ExpectedFunctions = @(
    "def _normalize_verdict(",
    "def _normalize_confidence(",
    "def _confidence_distance(",
    "def _facts_overlap_enough(",
    "def _results_equivalent(",
    "def _parse_analysis(",
    "def _handle_leader_error("
)

foreach ($Function in $ExpectedFunctions) {
    Assert-Contains -Haystack $Source -Needle $Function -Message "Missing helper: $Function"
}

$ExpectedMethods = @(
    "def submit_claim(",
    "def resolve_claim(",
    "def challenge_claim(",
    "def archive_claim(",
    "def get_claim(",
    "def get_claim_count("
)

foreach ($Method in $ExpectedMethods) {
    Assert-Contains -Haystack $Source -Needle $Method -Message "Missing public method: $Method"
}

$Verdicts = @('"supported"', '"contradicted"', '"unverifiable"', '"stale"')
foreach ($Verdict in $Verdicts) {
    Assert-Contains -Haystack $Source -Needle $Verdict -Message "Missing verdict value: $Verdict"
}

$ConfidenceBuckets = @('"high"', '"medium"', '"low"')
foreach ($Bucket in $ConfidenceBuckets) {
    Assert-Contains -Haystack $Source -Needle $Bucket -Message "Missing confidence bucket: $Bucket"
}

Write-Host "Contract source checks passed."
