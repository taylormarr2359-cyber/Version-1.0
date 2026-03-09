# run_atlas.ps1 — Launch ATLAS CLI on Windows
# Usage: .\scripts\run_atlas.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$Venv = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $Venv) {
    & $Venv
} else {
    Write-Warning ".venv not found — using system Python. Run: python -m venv .venv && pip install -e ."
}

Set-Location $ProjectRoot
python -m projrvt.main
