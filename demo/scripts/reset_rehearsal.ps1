param([string]$StateDirectory = "$env:USERPROFILE/.apishield/cinema/providers")
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $ProjectRoot
try { & './venv/Scripts/python.exe' -m demo.setup reset --state $StateDirectory; if ($LASTEXITCODE) { throw 'Rehearsal reset failed.' } }
finally { Pop-Location }
