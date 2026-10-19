$ErrorActionPreference = 'Stop'
$path = Join-Path $PSScriptRoot '.app-logs/server.pid'
if (Test-Path -LiteralPath $path) {
    $serverId = [int](Get-Content -LiteralPath $path)
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$serverId"
    if ($process -and $process.CommandLine -match 'uvicorn.*dashboard_api:app') {
        & taskkill.exe /PID $serverId /T /F
    } else { Write-Host 'No matching APIShield process is running.' }
}
