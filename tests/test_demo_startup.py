"""The demo launcher waits for the local app, then resets the banking fixture."""
import json
import os
from pathlib import Path
import subprocess

import pytest


@pytest.mark.skipif(os.name != 'nt', reason='Windows demo launcher')
def test_startup_reset_waits_for_readiness_and_posts_reset():
    helper = Path(__file__).resolve().parents[1] / 'tools/reset_banking_demo.ps1'
    assert helper.is_file()
    script = """
$global:calls = @()
function Start-Sleep { param($Milliseconds) }
function Invoke-RestMethod {
    param($Uri, $Method = 'GET', $TimeoutSec)
    $global:calls += "$Method $Uri"
    if ($global:calls.Count -eq 1) { throw 'Starting up' }
    if ($Method -eq 'POST') { return @{version='v1'} }
    return @{}
}
& '%s'
$global:calls | ConvertTo-Json -Compress
""" % str(helper).replace("'", "''")
    result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                            capture_output=True, text=True, timeout=15, check=True)
    calls = json.loads(result.stdout.strip().splitlines()[-1])
    assert calls == ['GET http://127.0.0.1:8002/api/workspace',
                     'GET http://127.0.0.1:8002/api/workspace',
                     'POST http://127.0.0.1:8002/api/banking/reset']
    for launcher in ('start_demo.ps1', 'start_app.ps1'):
        assert 'tools/reset_banking_demo.ps1' in (helper.parents[1] / launcher).read_text()
