param([string]$ClientRepository = '', [string]$ProviderHost = '', [string]$Model = 'gemini-3.8-flash', [int]$ClientPort = 8100, [int]$TheatrePort = 8101, [int]$PaymentPort = 8102, [switch]$SetupOnly)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (-not $ClientRepository) { $ClientRepository = Join-Path $ProjectRoot '.apishield/cinema/client-source' }
if (-not $ProviderHost) { $ProviderHost = Read-Host 'Paste the CinemaFlow HTTP link shown on System B' }
$env:APISHIELD_JOBS_DIR = Join-Path $ProjectRoot '.apishield/cinema/jobs'
$env:TEMP = Join-Path $ProjectRoot '.apishield/cinema/temp'
$env:TMP = $env:TEMP
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PIP_CACHE_DIR = Join-Path $ProjectRoot '.apishield/cinema/cache/pip'
$env:npm_config_cache = Join-Path $ProjectRoot '.apishield/cinema/cache/npm'
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
Push-Location $ProjectRoot
try {
    & './venv/Scripts/python.exe' -B -m demo.setup system-a --repository $ClientRepository --provider-host $ProviderHost --jobs-root $env:APISHIELD_JOBS_DIR --model $Model --client-port $ClientPort --theatre-port $TheatrePort --payment-port $PaymentPort
    if ($LASTEXITCODE) { throw 'System A setup failed; existing project settings were preserved.' }
    Write-Host 'CinemaFlow registered in manual mode. Its jobs and settings stay inside ProjectSeven.'
    if (-not $SetupOnly) { & (Join-Path $PSScriptRoot 'open_system_a.ps1') }
    else { Write-Host 'Setup complete. Start or reopen APIShield with ./demo/scripts/open_system_a.ps1 (optionally -Port 8005).' }
} finally { Pop-Location }
