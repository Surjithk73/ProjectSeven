$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $ProjectRoot
try { & './venv/Scripts/python.exe' -m demo.setup check-environment; if ($LASTEXITCODE) { throw 'Environment check failed.' } }
finally { Pop-Location }
