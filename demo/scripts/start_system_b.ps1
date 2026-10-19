param([string]$StateDirectory = "$env:USERPROFILE/.apishield/cinema/providers", [string]$ClientRepository = '', [string]$DeploymentConfig = '', [int]$ClientPort = 8100, [int]$TheatrePort = 8101, [int]$PaymentPort = 8102)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$Python = Join-Path $ProjectRoot 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Install the project Python environment first; see docs/demo/setup.md.' }
$StateDirectory = [IO.Path]::GetFullPath($StateDirectory)
New-Item -ItemType Directory -Force -Path $StateDirectory | Out-Null
$Arguments = @('-m', 'demo.runtime', '--client-port', $ClientPort, '--theatre-port', $TheatrePort, '--payment-port', $PaymentPort, '--state', ('"{0}"' -f $StateDirectory))
if ($ClientRepository) { $Arguments += @('--client-repository', ('"{0}"' -f [IO.Path]::GetFullPath($ClientRepository))) }
if ($DeploymentConfig) { $Arguments += @('--deployment-config', ('"{0}"' -f [IO.Path]::GetFullPath($DeploymentConfig))) }
$Process = Start-Process -FilePath $Python -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $StateDirectory 'runtime.stdout.log') -RedirectStandardError (Join-Path $StateDirectory 'runtime.stderr.log')
Write-Host "CinemaFlow starting (PID $($Process.Id)). Client port defaults to 8100; deployment mode uses its config. Logs: $StateDirectory"
