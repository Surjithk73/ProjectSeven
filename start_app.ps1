param([string]$Python = '', [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$logs = Join-Path $PSScriptRoot '.app-logs'
New-Item -ItemType Directory -Force -Path $logs | Out-Null
if (-not $Python) {
    $common = (& git rev-parse --git-common-dir).Trim()
    $original = Split-Path -Parent (Resolve-Path $common).Path
    $candidates = @((Join-Path $PSScriptRoot 'venv/Scripts/python.exe'), (Join-Path $original 'venv/Scripts/python.exe'))
    $Python = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $Python) {
        & python -m venv venv
        if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11+ before starting APIShield.' }
        $Python = Join-Path $PSScriptRoot 'venv/Scripts/python.exe'
    }
}
& $Python -c 'import importlib.util, sys; sys.exit(0 if all(importlib.util.find_spec(name) for name in ["fastapi", "uvicorn", "httpx", "pytest", "google"]) and importlib.util.find_spec("google.genai") else 1)'
if ($LASTEXITCODE -ne 0) {
    & $Python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
}
if (-not (Test-Path 'frontend/node_modules')) {
    Push-Location frontend
    try { & npm.cmd ci; if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' } }
    finally { Pop-Location }
}
Push-Location frontend
try { & npm.cmd run build; if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' } }
finally { Pop-Location }
if (-not $env:OASDIFF_BIN -and (Test-Path 'tools/oasdiff.exe')) { $env:OASDIFF_BIN = (Resolve-Path 'tools/oasdiff.exe').Path }
$listener = Get-NetTCPConnection -LocalPort 8002 -State Listen -ErrorAction SilentlyContinue
if ($listener) { throw 'Port 8002 is already in use. Stop the existing app before starting a new instance.' }
$process = Start-Process -FilePath $Python -ArgumentList '-B', '-m', 'uvicorn', 'dashboard_api:app', '--host', '127.0.0.1', '--port', '8002' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'server.out.log') -RedirectStandardError (Join-Path $logs 'server.err.log') -PassThru
$process.Id | Set-Content (Join-Path $logs 'server.pid')
& (Join-Path $PSScriptRoot 'tools/reset_banking_demo.ps1')
Write-Host 'APIShield is ready at http://127.0.0.1:8002'
if (-not $NoBrowser) { Start-Process 'http://127.0.0.1:8002' }
