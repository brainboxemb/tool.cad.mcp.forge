param(
    [Parameter(Mandatory=$true)][string]$Workspace,
    [Parameter(Mandatory=$true)][string]$SolidCraftCli,
    [string]$ForgeSource
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $ForgeSource) { $ForgeSource = Join-Path (Split-Path -Parent $Root) "forge-release" }
conda run --no-capture-output -n forge-mcp-dev python -m forge_mcp.server doctor --workspace (Resolve-Path -LiteralPath $Workspace).Path --forge-source (Resolve-Path -LiteralPath $ForgeSource).Path --solidcraft-cli $SolidCraftCli
if ($LASTEXITCODE -ne 0) { throw "Doctor failed; inspect the JSON report." }
