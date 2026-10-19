param([ValidateRange(1,65535)][int]$Port = 8002)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$Python = Join-Path $ProjectRoot 'venv/Scripts/python.exe'
$env:APISHIELD_JOBS_DIR = Join-Path $ProjectRoot '.apishield/cinema/jobs'
if (-not (Test-Path -LiteralPath (Join-Path $env:APISHIELD_JOBS_DIR '_projects/cinemaflow/state.json'))) { throw 'Run start_system_a.ps1 to register CinemaFlow first.' }
if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot 'frontend/dist/index.html'))) { throw 'Build the frontend first: npm --prefix frontend run build' }
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) { throw "Port $Port is in use. Stop that instance yourself, or select another -Port." }
$env:PYTHONPATH = $ProjectRoot
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TEMP = Join-Path $ProjectRoot '.apishield/cinema/temp'
$env:TMP = $env:TEMP
$Logs = Join-Path $ProjectRoot '.apishield/cinema/logs'
New-Item -ItemType Directory -Force -Path $env:TEMP,$Logs | Out-Null
if (Test-Path -LiteralPath (Join-Path $ProjectRoot 'tools/oasdiff.exe')) { $env:OASDIFF_BIN = Join-Path $ProjectRoot 'tools/oasdiff.exe' }
$Process = Start-Process -FilePath $Python -ArgumentList @('-B','-m','uvicorn','dashboard_api:app','--host','127.0.0.1','--port',$Port) -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Logs 'system-a.stdout.log') -RedirectStandardError (Join-Path $Logs 'system-a.stderr.log')
$Process.Id | Set-Content -LiteralPath (Join-Path $Logs 'system-a.pid')
Write-Host "APIShield starting at http://127.0.0.1:$Port/?project=cinemaflow (PID $($Process.Id)). Logs: $Logs"
