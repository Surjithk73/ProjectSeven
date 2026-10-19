param([string]$StateDirectory = "$env:USERPROFILE/.apishield/cinema/providers", [string]$ClientRepository = '', [string]$DeploymentConfig = '')
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$Python = Join-Path $ProjectRoot 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Install the project Python environment first; see docs/demo/setup.md.' }
$StateDirectory = [IO.Path]::GetFullPath($StateDirectory)
New-Item -ItemType Directory -Force -Path $StateDirectory | Out-Null
$Arguments = @('-m', 'demo.runtime', '--state', ('"{0}"' -f $StateDirectory))
if ($ClientRepository) { $Arguments += @('--client-repository', ('"{0}"' -f [IO.Path]::GetFullPath($ClientRepository))) }
if ($DeploymentConfig) { $Arguments += @('--deployment-config', ('"{0}"' -f [IO.Path]::GetFullPath($DeploymentConfig))) }
$Process = Start-Process -FilePath $Python -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $StateDirectory 'runtime.stdout.log') -RedirectStandardError (Join-Path $StateDirectory 'runtime.stderr.log')
Write-Host "CinemaFlow starting (PID $($Process.Id)). Open http://127.0.0.1:8100. Logs: $StateDirectory"
