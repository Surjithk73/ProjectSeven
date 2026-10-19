"""Module CLI acceptance checks run in separate processes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import pytest

ROOT = Path(__file__).resolve().parents[1]

PARCEL_SOURCE = '''import httpx
API_URL = "https://parcel.example.test"
def create_label(package_id, weight_grams):
    """Business Intent: Create a label preserving package and gram weight."""
    response = httpx.post(f"{API_URL}/labels", json={"package_id": package_id, "weight_grams": weight_grams})
    response.raise_for_status()
    return response.json()
'''


@pytest.fixture
def parcel(tmp_path):
    repo = tmp_path / 'parcel'
    (repo / 'src').mkdir(parents=True)
    (repo / 'tests').mkdir()
    (repo / 'src/__init__.py').write_text('')
    (repo / 'src/parcel.py').write_text(PARCEL_SOURCE)
    (repo / 'tests/test_parcel.py').write_text('''import httpx
from src.parcel import create_label
def test_shipping_preserves_package_and_weight(monkeypatch):
    def post(url, *, json):
        assert url == "https://parcel.example.test/labels/create"
        assert json == {"package_id": "p-1", "weight_grams": 2501}
        return httpx.Response(200, json={"label_id": "label-1"}, request=httpx.Request("POST", url))
    monkeypatch.setattr(httpx, "post", post)
    assert create_label("p-1", 2501) == {"label_id": "label-1"}
''')
    subprocess.run(['git', 'init', str(repo)], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(repo), 'add', 'src', 'tests'], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                    'commit', '-m', 'shipping v1'], check=True, capture_output=True)
    for name, route in [('base', '/labels'), ('target', '/labels/create')]:
        (tmp_path / f'{name}.json').write_text(json.dumps({'openapi': '3.0.3',
            'info': {'title': 'Parcel', 'version': name}, 'paths': {route: {'post': {
            'responses': {'200': {'description': 'Label created'}}}}}}))
    config = tmp_path / 'integration.json'
    config.write_text(json.dumps({'version': 1, 'repository': str(repo), 'code_paths': ['src'],
        'base_spec': 'base.json', 'target_spec': 'target.json',
        'test_commands': [['python', '-m', 'pytest', 'tests', '-q']], 'budgets': {'max_attempts': 1}}))
    candidate = tmp_path / 'candidate.json'
    candidate.write_text(json.dumps({'patches': [{'file': 'src/parcel.py',
        'old_code_snippet': 'f"{API_URL}/labels"', 'new_code_snippet': 'f"{API_URL}/labels/create"'}]}))
    return repo, config, candidate, tmp_path / 'jobs'


def invoke(*arguments):
    env = os.environ.copy()
    env['GEMINI_API_KEY'] = ''
    env['GITHUB_TOKEN'] = ''
    return subprocess.run([sys.executable, '-B', '-m', 'apishield', *map(str, arguments)],
                          cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)


def test_cli_help_lists_local_workflow():
    result = invoke('--help')
    assert result.returncode == 0, result.stderr
    assert all(command in result.stdout for command in ['scan', 'compare', 'repair', 'report', 'cancel'])


def test_cli_invalid_config_returns_json_without_traceback(tmp_path):
    result = invoke('scan', '--config', tmp_path / 'missing.json', '--jobs-dir', tmp_path / 'jobs')
    assert result.returncode == 2, result.stderr
    assert json.loads(result.stdout)['status'] == 'error'
    assert 'Traceback' not in result.stderr


def test_cli_unknown_report_is_an_error(tmp_path):
    result = invoke('report', 'f' * 32, '--jobs-dir', tmp_path / 'jobs')
    assert result.returncode == 2, result.stderr
    assert json.loads(result.stdout)['status'] == 'error'


def test_cli_json_errors_work_with_ascii_terminal_and_unicode_paths(tmp_path):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'ascii'
    result = subprocess.run([sys.executable, '-B', '-m', 'apishield', 'scan', '--config',
        str(tmp_path / '\u8f93\u5165.json'), '--jobs-dir', str(tmp_path / 'jobs')],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding='ascii', timeout=30)
    assert result.returncode == 2, result.stderr
    assert '\u8f93\u5165.json' in json.loads(result.stdout)['error']


def test_cli_adapter_failure_finishes_allocated_job_and_cleans(parcel, monkeypatch, capsys):
    from apishield.cli import main
    from apishield.jobs import JobStore
    fake_engine = types.ModuleType('apishield.engine')
    def fail(*args, **kwargs):
        raise OSError('Worker startup failed')
    fake_engine.run_job = fail
    monkeypatch.setitem(sys.modules, 'apishield.engine', fake_engine)
    _, config, _, jobs = parcel
    assert main(['scan', '--config', str(config), '--jobs-dir', str(jobs)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result['status'] == 'failed'
    assert JobStore(jobs).get(result['job_id'])['status'] == 'failed'
    assert not (jobs / result['job_id'] / 'workspace').exists()


def test_cli_scan_report_and_cancel_are_durable(parcel):
    repo, config, _, jobs = parcel
    before = (repo / 'src/parcel.py').read_bytes()
    scan = invoke('scan', '--config', config, '--jobs-dir', jobs)
    assert scan.returncode == 0, scan.stdout + scan.stderr
    evidence = json.loads(scan.stdout)
    assert evidence['status'] == 'completed'
    report = invoke('report', evidence['job_id'], '--jobs-dir', jobs)
    assert json.loads(report.stdout)['source_commit'] == evidence['source_commit']
    cancel = invoke('cancel', evidence['job_id'], '--jobs-dir', jobs)
    assert json.loads(cancel.stdout)['status'] == 'completed'
    assert (repo / 'src/parcel.py').read_bytes() == before
    assert not (jobs / evidence['job_id'] / 'workspace').exists()


def test_cli_repair_produces_applicable_patch_without_original_edits(parcel):
    repo, config, candidate, jobs = parcel
    before = (repo / 'src/parcel.py').read_bytes()
    compared = invoke('compare', '--config', config, '--jobs-dir', jobs)
    assert compared.returncode == 0, compared.stdout + compared.stderr
    repaired = invoke('repair', '--config', config, '--candidate', candidate, '--jobs-dir', jobs)
    assert repaired.returncode == 0, repaired.stdout + repaired.stderr
    evidence = json.loads(repaired.stdout)
    assert evidence['status'] == 'validated'
    patch = jobs / evidence['job_id'] / 'candidate.patch'
    assert patch.is_file()
    applicable = subprocess.run(['git', '-C', str(repo), 'apply', '--check', str(patch)], capture_output=True, text=True)
    assert applicable.returncode == 0, applicable.stderr
    assert (repo / 'src/parcel.py').read_bytes() == before
    assert not (jobs / evidence['job_id'] / 'workspace').exists()
