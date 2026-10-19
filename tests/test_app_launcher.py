import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.skipif(os.name != 'nt', reason='Windows PowerShell launcher')
def test_missing_dependencies_reach_installation_without_stderr_abort(tmp_path):
    import venv
    venv.EnvBuilder(with_pip=False).create(tmp_path / 'empty-venv')
    python = tmp_path / 'empty-venv/Scripts/python.exe'
    launcher = Path(__file__).resolve().parents[1] / 'start_app.ps1'
    # Empty environment also lacks pip: the intended installation error proves
    # the missing-dependency probe reached the install branch, before any server starts.
    result = subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(launcher),
                             '-Python',str(python),'-NoBrowser'], capture_output=True, text=True, timeout=30)
    assert 'Python dependency installation failed' in result.stderr, result.stdout + result.stderr
    assert 'NativeCommandError' not in result.stderr.split('Python dependency installation failed')[0]
