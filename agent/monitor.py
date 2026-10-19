"""Contract comparison; errors must never become a no-change finding."""
import json
from pathlib import Path
import shutil
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_api_diff(base_spec: str = 'mock_provider/specs/v1_spec.json', revised_spec: str = 'mock_provider/specs/v2_spec.json', mode: str = 'breaking') -> str:
    from config import get_setting
    if mode not in ('breaking', 'diff'):
        raise ValueError('Unsupported contract comparison mode')
    binary = get_setting('OASDIFF_BIN') or shutil.which('oasdiff')
    if not binary:
        bundled = PROJECT_ROOT / 'tools' / 'oasdiff.exe'
        if not bundled.is_file():
            raise FileNotFoundError('oasdiff unavailable; install it or set OASDIFF_BIN')
        binary = str(bundled)
    result = subprocess.run([binary, mode, base_spec, revised_spec, '--format', 'json'], capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30)
    allowed = (0, 1) if mode == 'breaking' else (0,)
    if result.returncode not in allowed:
        raise RuntimeError(f'oasdiff failed ({result.returncode}): {result.stderr}')
    output = result.stdout.strip()
    if not output:
        if result.returncode != 0:
            raise RuntimeError('oasdiff reported changes without JSON evidence')
        return '[]' if mode == 'breaking' else '{}'
    data = json.loads(output)
    if not isinstance(data, list if mode == 'breaking' else dict):
        raise ValueError('Unexpected oasdiff JSON structure')
    return output


def is_breaking_change(diff_json_str: str) -> bool:
    data = json.loads(diff_json_str)
    if not isinstance(data, list):
        raise ValueError('Breaking diff must be a JSON array')
    return bool(data)


def get_schema_context(base_spec: str, revised_spec: str) -> str:
    return json.dumps({'base': json.loads((PROJECT_ROOT / base_spec).read_text(encoding='utf-8')), 'target': json.loads((PROJECT_ROOT / revised_spec).read_text(encoding='utf-8'))})


if __name__ == '__main__':
    print(get_api_diff())
