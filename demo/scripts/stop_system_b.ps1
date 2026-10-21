param([string]$StateDirectory = '')
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (-not $StateDirectory) { $StateDirectory = Join-Path $ProjectRoot '.apishield/cinema/providers' }
Push-Location $ProjectRoot
try { & './venv/Scripts/python.exe' -B -m demo.runtime --state $StateDirectory --stop; if ($LASTEXITCODE) { throw 'Stop request failed.' } }
finally { Pop-Location }
