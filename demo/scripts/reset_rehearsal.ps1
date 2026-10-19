param([string]$StateDirectory = '')
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (-not $StateDirectory) { $StateDirectory = Join-Path $ProjectRoot '.apishield/cinema/providers' }
Push-Location $ProjectRoot
try { & './venv/Scripts/python.exe' -B -m demo.setup reset --state $StateDirectory; if ($LASTEXITCODE) { throw 'Rehearsal reset failed.' } }
finally { Pop-Location }
