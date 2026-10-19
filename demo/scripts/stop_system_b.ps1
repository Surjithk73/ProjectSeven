param([string]$StateDirectory = "$env:USERPROFILE/.apishield/cinema/providers")
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $ProjectRoot
try { & './venv/Scripts/python.exe' -m demo.runtime --state $StateDirectory --stop; if ($LASTEXITCODE) { throw 'Stop request failed.' } }
finally { Pop-Location }
