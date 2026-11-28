param(
    [Parameter(Mandatory=$true)][ValidateRange(1,2147483647)][int]$Issue,
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9]+(-[a-z0-9]+)*$')][string]$Name,
    [ValidateSet("main")][string]$Base = "main",
    [string]$Path = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = "Stop"
function Git([string[]]$Arguments) {
    $result = & git -C $Path @Arguments
    if ($LASTEXITCODE -ne 0) { throw "git failed: $Arguments" }
    return $result
}
if (Git @("status","--porcelain")) { throw "Commit or explicitly stash local changes first." }
Git @("fetch","origin",$Base) | Out-Host
Git @("switch","-c","issue/$Issue-$Name","FETCH_HEAD") | Out-Host
