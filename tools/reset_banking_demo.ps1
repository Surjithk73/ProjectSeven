$ErrorActionPreference = 'Stop'
$ready = $false
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    try {
        $null = Invoke-RestMethod -Uri 'http://127.0.0.1:8002/api/workspace' -TimeoutSec 2
        $ready = $true
        break
    } catch {
        Start-Sleep -Milliseconds 500
    }
}
if (-not $ready) { throw 'APIShield did not become ready; the banking demo was not reset.' }
$state = Invoke-RestMethod -Method POST -Uri 'http://127.0.0.1:8002/api/banking/reset' -TimeoutSec 20
if ($state.version -ne 'v1') { throw 'Banking demo failed to reset to V1.' }
Write-Host 'Banking demo reset: V1 client and provider, funded accounts, empty transaction history.'
