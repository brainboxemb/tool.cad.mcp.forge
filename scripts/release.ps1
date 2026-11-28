param(
    [Parameter(Mandatory=$true,Position=0)][ValidateSet("prepare","request")][string]$Action,
    [Parameter(Mandatory=$true)][ValidatePattern('^v[0-9]+\.[0-9]+\.[0-9]+$')][string]$Version,
    [int]$Issue
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
function Git([string[]]$Arguments) {
    $value = & git -C $Root @Arguments
    if ($LASTEXITCODE -ne 0) { throw "git failed: $Arguments" }
    return $value
}
if (Git @("status","--porcelain")) { throw "Commit or explicitly stash local changes first." }
Git @("fetch","origin","main") | Out-Host
$Sha = Git @("rev-parse","FETCH_HEAD")
if ($Action -eq "prepare") {
    Git @("switch","-c","release/$Version",$Sha) | Out-Host
    Write-Host "Edit only pyproject.toml project.version and CHANGELOG.md; test, commit and use pr.ps1."
} else {
    if ($Issue -le 0) { throw "Supply the normal release tracking issue." }
    if ((Git @("branch","--show-current")) -ne "main" -or (Git @("rev-parse","HEAD")) -ne $Sha) {
        throw "Request release from the exact current stable main checkout."
    }
    $Expected = $Version.Substring(1)
    $ProjectVersion = conda run --no-capture-output -n forge-mcp-dev python -c "import tomllib,sys; print(tomllib.load(open(sys.argv[1],'rb'))['project']['version'])" (Join-Path $Root "pyproject.toml")
    if ($LASTEXITCODE -ne 0 -or $ProjectVersion -ne $Expected) { throw "Release metadata version does not match." }
    Push-Location $Root
    try {
        gh issue comment $Issue --body "/release $Version $Sha"
        if ($LASTEXITCODE -ne 0) { throw "Release request failed." }
        Write-Host "Requested governed release; check Actions and the issue for the result."
    } finally { Pop-Location }
}
