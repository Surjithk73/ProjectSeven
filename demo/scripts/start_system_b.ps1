param([string]$StateDirectory = '', [string]$ClientRepository = '', [string]$DeploymentConfig = '', [int]$ClientPort = 8100, [int]$TheatrePort = 8101, [int]$PaymentPort = 8102)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$Python = Join-Path $ProjectRoot 'venv/Scripts/python.exe'
$env:PYTHONPATH = $ProjectRoot
if (-not (Test-Path -LiteralPath $Python)) { throw 'Install the project Python environment first; see docs/demo/setup.md.' }
if (-not $StateDirectory) { $StateDirectory = Join-Path $ProjectRoot '.apishield/cinema/providers' }
$StateDirectory = & $Python -B -m demo.setup validate-path --path $StateDirectory
if ($LASTEXITCODE) { throw 'The state directory must be inside ProjectSeven.' }
if ($ClientRepository) {
    $ClientRepository = & $Python -B -m demo.setup validate-path --path $ClientRepository
    if ($LASTEXITCODE) { throw 'Keep the client folder inside ProjectSeven.' }
}
if ($DeploymentConfig) {
    $DeploymentConfig = & $Python -B -m demo.setup validate-path --path $DeploymentConfig
    if ($LASTEXITCODE) { throw 'Keep the config file inside ProjectSeven.' }
}
New-Item -ItemType Directory -Force -Path $StateDirectory | Out-Null
$env:TEMP = Join-Path $ProjectRoot '.apishield/cinema/temp'
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
$env:TMP = $env:TEMP
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PIP_CACHE_DIR = Join-Path $ProjectRoot '.apishield/cinema/cache/pip'
if ($DeploymentConfig) {
    $PrivateConfig = Get-Content -LiteralPath $DeploymentConfig -Raw | ConvertFrom-Json
    if ($PrivateConfig.client_port) { $ClientPort = [int]$PrivateConfig.client_port }
    $TheatrePort = ([uri]$PrivateConfig.providers.theatre).Port
    $PaymentPort = ([uri]$PrivateConfig.providers.payment).Port
}
$Arguments = @('-B', '-m', 'demo.runtime', '--client-port', $ClientPort, '--theatre-port', $TheatrePort, '--payment-port', $PaymentPort, '--state', ('"{0}"' -f $StateDirectory))
if ($ClientRepository) { $Arguments += @('--client-repository', ('"{0}"' -f [IO.Path]::GetFullPath($ClientRepository))) }
if ($DeploymentConfig) { $Arguments += @('--deployment-config', ('"{0}"' -f [IO.Path]::GetFullPath($DeploymentConfig))) }
$Process = Start-Process -FilePath $Python -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $StateDirectory 'runtime.stdout.log') -RedirectStandardError (Join-Path $StateDirectory 'runtime.stderr.log')
Write-Host "CinemaFlow starting (PID $($Process.Id)). Logs: $StateDirectory"
Write-Host "On this computer: http://127.0.0.1:$ClientPort"
Write-Host "From System A on the same Wi-Fi: http://$($env:COMPUTERNAME):$ClientPort"
Write-Host 'Copy that link into start_system_a.ps1 when prompted. Open it after startup completes.'
Write-Host "If the computer-name link does not resolve, run: & '$Python' -B -m demo.setup connection-info --client-port $ClientPort --theatre-port $TheatrePort --payment-port $PaymentPort"
Write-Host 'LAN access depends on the Private-profile firewall rules. This is not a public internet URL.'
