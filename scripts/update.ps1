param([string]$ForgeSource)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $ForgeSource) { $ForgeSource = Join-Path (Split-Path -Parent $Root) "forge-release" }
$ForgeSource = [IO.Path]::GetFullPath($ForgeSource)
$RefLine = Select-String -Path (Join-Path $Root "src/forge_mcp/knowledge.py") -Pattern '^FORGE_REF = "(v[0-9.]+)"$'
if (-not $RefLine) { throw "Cannot determine supported Forge ref." }
$Ref = $RefLine.Matches[0].Groups[1].Value
if (-not (Test-Path -LiteralPath $ForgeSource)) {
    git clone --depth 1 --branch $Ref https://github.com/brainboxemb/lib.py.solidcraft.forge.git $ForgeSource
    if ($LASTEXITCODE -ne 0) { throw "Forge clone failed." }
}
function ForgeGit([string[]]$Arguments) {
    $Value = & git -C $ForgeSource @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Forge checkout validation failed: $Arguments" }
    return $Value
}
$Head = ForgeGit @("rev-parse","HEAD")
$Tag = ForgeGit @("rev-list","-n","1",$Ref)
if ($Head -ne $Tag -or (ForgeGit @("status","--porcelain","--untracked-files=no"))) {
    throw "Select the exact clean Forge tag $Ref explicitly; update never resets the checkout."
}
conda run --no-capture-output -n forge-mcp-dev python -m pip install -e "${Root}[test]" (Join-Path $ForgeSource "cadlib")
if ($LASTEXITCODE -ne 0) { throw "Developer package install failed." }
Write-Host "Developer environment updated. Select forge-mcp-dev in VS Code."
