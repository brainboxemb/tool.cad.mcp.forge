param([string]$ForgeSource)
$ErrorActionPreference = "Stop"
$Known = conda env list --json
if ($LASTEXITCODE -ne 0) { throw "Conda is required." }
$Envs = ($Known | ConvertFrom-Json).envs
if (-not ($Envs | Where-Object { (Split-Path $_ -Leaf) -eq "forge-mcp-dev" })) {
    conda create -n forge-mcp-dev python=3.12 pip -y
    if ($LASTEXITCODE -ne 0) { throw "Conda environment creation failed." }
}
& (Join-Path $PSScriptRoot "update.ps1") -ForgeSource $ForgeSource
