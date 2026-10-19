param([Parameter(Mandatory=$true)][string]$ClientRepository, [Parameter(Mandatory=$true)][string]$ProviderHost, [string]$Model = 'gemini-3.8-flash', [int]$ClientPort = 8100, [int]$TheatrePort = 8101, [int]$PaymentPort = 8102)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $ProjectRoot
try {
    & './venv/Scripts/python.exe' -m demo.setup system-a --repository $ClientRepository --provider-host $ProviderHost --model $Model --client-port $ClientPort --theatre-port $TheatrePort --payment-port $PaymentPort
    if ($LASTEXITCODE) { throw 'System A setup failed; existing project settings were preserved.' }
    Write-Host 'CinemaFlow registered in manual mode. Start APIShield using start_app.bat and select CinemaFlow Integration.'
} finally { Pop-Location }
