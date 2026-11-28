param(
    [string[]]$Tests,
    [switch]$All,
    [switch]$Runtime,
    [string]$ForgeSource
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $ForgeSource) { $ForgeSource = Join-Path (Split-Path -Parent $Root) "forge-release" }
$OldForge = $env:FORGE_SOURCE_ROOT
$OldPython = $env:PYTHONPATH
Push-Location $Root
try {
    $env:FORGE_SOURCE_ROOT = (Resolve-Path -LiteralPath $ForgeSource).Path
    if ($Runtime) {
        $env:PYTHONPATH = Join-Path $Root "modules/ci/src"
        conda run --no-capture-output -n forge-mcp-dev python -m forge_mcp_ci acceptance
        if ($LASTEXITCODE -ne 0) { throw "Released-stack acceptance failed." }
    } else {
        if ($All -and $Tests) { throw "Choose -All or -Tests." }
        if ($All) { $Tests = @("tests") }
        if (-not $Tests) {
            $Tests = @("tests/test_knowledge.py","tests/test_compiler.py","tests/test_live.py","tests/test_protocol.py","tests/test_operator_scripts.py")
        }
        conda run --no-capture-output -n forge-mcp-dev python -m pytest -q @Tests
        if ($LASTEXITCODE -ne 0) { throw "MCP tests failed." }
        foreach ($Module in @("ci","merge-policy","branch-cleanup","release")) {
            $env:PYTHONPATH = Join-Path $Root "modules/$Module/src"
            conda run --no-capture-output -n forge-mcp-dev python -m unittest discover -s "modules/$Module/tests"
            if ($LASTEXITCODE -ne 0) { throw "$Module tests failed." }
        }
    }
} finally {
    $env:FORGE_SOURCE_ROOT = $OldForge
    $env:PYTHONPATH = $OldPython
    Pop-Location
}
