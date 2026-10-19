import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from mcp_server.process_runner import run_agent_process


def test_runner_captures_output_and_exit(tmp_path):
    result = run_agent_process([sys.executable, '-c', 'print("evidence")'],
                               env=os.environ.copy(), cwd=str(tmp_path), timeout=5)
    assert result.returncode == 0
    assert b'evidence' in result.stdout


def test_timeout_stops_descendant_before_it_can_write(tmp_path):
    marker, ready = tmp_path / 'descendant-write', tmp_path / 'ready'
    child = f'import time; from pathlib import Path; time.sleep(2); Path({str(marker)!r}).write_text("late mutation")'
    parent = f'import subprocess, sys, time; from pathlib import Path; subprocess.Popen([sys.executable, "-c", {child!r}]); Path({str(ready)!r}).write_text("spawned"); time.sleep(20)'
    with pytest.raises(subprocess.TimeoutExpired):
        run_agent_process([sys.executable, '-c', parent], env=os.environ.copy(),
                          cwd=str(tmp_path), timeout=1)
    assert ready.exists(), 'The test must exercise a spawned descendant'
    time.sleep(1.5)
    assert not marker.exists()
