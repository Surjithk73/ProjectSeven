param([Parameter(Mandatory=$true)][string]$ClientRepository, [Parameter(Mandatory=$true)][string]$ProviderHost, [string]$Model = 'gemini-2.5-flash')
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $ProjectRoot
try {
    & './venv/Scripts/python.exe' -m demo.setup system-a --repository $ClientRepository --provider-host $ProviderHost --model $Model
    if ($LASTEXITCODE) { throw 'System A setup failed; existing project settings were preserved.' }
    Write-Host 'CinemaFlow registered in manual mode. Start APIShield using start_app.bat and select CinemaFlow Integration.'
} finally { Pop-Location }
