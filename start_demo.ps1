param([string]$Python = (Join-Path $PSScriptRoot 'venv\Scripts\python.exe'))
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Create venv and install requirements.txt first, or pass -Python with your interpreter path.'
}
$Python = (Resolve-Path -LiteralPath $Python).Path
$npm = (Get-Command npm.cmd -ErrorAction Stop).Source
foreach ($port in 8001, 8002, 8003, 5173, 5174) {
    if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
        throw "Port $port is already in use. Stop the existing demo before starting another."
    }
}
foreach ($directory in 'frontend', 'swiftpay_frontend') {
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "$directory\node_modules"))) {
        throw "Run npm ci in $directory first."
    }
}
$env:API_VERSION = 'v1'
$env:API_BASE = 'http://127.0.0.1:8001'
$env:PROVIDER_URL = 'http://127.0.0.1:8001'
$env:BFF_URL = 'http://127.0.0.1:8003'
& $Python reset.py --no-provider-switch
if ($LASTEXITCODE -ne 0) { throw 'Offline V1 reset failed.' }
$logDirectory = Join-Path $PSScriptRoot '.demo-logs'
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$started = [System.Collections.Generic.List[System.Diagnostics.Process]]::new()
function Start-DemoService($name, $executable, $arguments, $directory) {
    $process = Start-Process -FilePath $executable -ArgumentList $arguments `
        -WorkingDirectory $directory -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $logDirectory "$name.log") `
        -RedirectStandardError (Join-Path $logDirectory "$name.error.log")
    $started.Add($process)
}
try {
    Start-DemoService 'provider' $Python @('-m', 'uvicorn', 'mock_provider.main:app', '--host', '127.0.0.1', '--port', '8001') $PSScriptRoot
    Start-DemoService 'dashboard' $Python @('-m', 'uvicorn', 'dashboard_api:app', '--host', '127.0.0.1', '--port', '8002') $PSScriptRoot
    & (Join-Path $PSScriptRoot 'tools/reset_banking_demo.ps1')
    Start-DemoService 'bff' $Python @('-m', 'uvicorn', 'client_app.server:app', '--host', '127.0.0.1', '--port', '8003') $PSScriptRoot
    # cmd.exe /c launches npm.cmd through Start-Process.
    Start-DemoService 'apishield-ui' $env:ComSpec @('/d', '/s', '/c', ('""{0}" run dev -- --host 127.0.0.1 --port 5173 --strictPort"' -f $npm)) (Join-Path $PSScriptRoot 'frontend')
    Start-DemoService 'swiftpay-ui' $env:ComSpec @('/d', '/s', '/c', ('""{0}" run dev -- --host 127.0.0.1 --port 5174 --strictPort"' -f $npm)) (Join-Path $PSScriptRoot 'swiftpay_frontend')
    $started.Id | Set-Content -LiteralPath (Join-Path $logDirectory 'process-ids.txt')
    Write-Host 'Services launched; check .demo-logs for startup errors.'
    Write-Host 'APIShield: http://localhost:5173   SwiftPay: http://localhost:5174'
} catch {
    $started | Stop-Process -ErrorAction SilentlyContinue
    throw
}
