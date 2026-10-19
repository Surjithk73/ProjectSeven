"""Explicit test evidence and optional model judgment (disabled by default)."""
import os
from pathlib import Path
import re
import subprocess
import sys

try:
    from fastmcp import FastMCP
    mcp = FastMCP('Test Runner & IPS Validator')
except ImportError:
    mcp = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _text(value):
    return value.decode(errors='replace') if isinstance(value, bytes) else (value or '')


def run_tests_and_score_ips(test_path: str = 'client_app/tests', original_intent: str = '', api_version: str | None = None) -> dict:
    from config import get_setting, get_model, get_genai_client
    results = {'tests_passed': False, 'test_output': '', 'ips_score': None, 'ips_error': None}
    env = os.environ.copy()
    env['API_VERSION'] = api_version or get_setting('API_VERSION', 'v2')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    try:
        timeout = float(get_setting('TEST_TIMEOUT_SECONDS', '120'))
        if timeout <= 0:
            raise ValueError('TEST_TIMEOUT_SECONDS must be positive')
        cmd = [sys.executable, '-B', '-m', 'pytest', test_path, '-v']
        process = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, env=env, timeout=timeout)
        results['tests_passed'] = process.returncode == 0
        results['test_output'] = process.stdout + '\n' + process.stderr
    except subprocess.TimeoutExpired as exc:
        results['test_output'] = f'Tests timed out after {exc.timeout} seconds\n{_text(exc.stdout)}\n{_text(exc.stderr)}'
    except Exception as exc:
        results['test_output'] = f'Test execution failed: {exc}'

    if get_setting('ENABLE_IPS_SCORING', '0') != '1':
        results['ips_error'] = 'IPS scoring disabled'
        return results
    try:
        code = '\n'.join(f'--- {path.name} ---\n{path.read_text(encoding="utf-8")}' for path in sorted((PROJECT_ROOT / 'client_app').glob('*_service.py')))
        response = get_genai_client().models.generate_content(
            model=get_model(),
            contents=f'Judge preservation of this business intent: {original_intent}\nCode:\n{code}\nReturn ONLY one integer from 0 to 100.',
        )
        text = response.text.strip()
        if not re.fullmatch(r'[0-9]{1,3}', text) or not 0 <= int(text) <= 100:
            raise ValueError('IPS response must be a single integer from 0 to 100')
        results['ips_score'] = int(text)
    except Exception as exc:
        results['ips_error'] = str(exc)
    return results


if mcp is not None:
    mcp.tool()(run_tests_and_score_ips)

if __name__ == '__main__' and mcp is not None:
    mcp.run()
