from test_model_access import credential, fake_credentials
"""Offline transactions against an independent shipment client and real tests."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import signal
import sys
import threading
import time
from types import SimpleNamespace
import stat

import pytest

from apishield.configuration import load_config
from apishield.jobs import JobStore
from apishield.jobs import atomic_json

SOURCE = '''import httpx
BASE = "https://ship.example.test"
def ship(parcel, grams):
    """Business Intent: Preserve shipment identity and exact gram weight."""
    return httpx.post(f"{BASE}/shipments", json={"parcel": parcel, "grams": grams}).json()
def health():
    return httpx.get(BASE + "/health")
'''
TEST = '''import httpx
from src.client import ship
def test_exact_shipment(monkeypatch):
    def post(url, *, json):
        assert url == "https://ship.example.test/shipments/create"
        assert json == {"parcel": "parcel-7", "grams": 2501}
        return httpx.Response(200, json={"shipment": "s-7"})
    monkeypatch.setattr(httpx, "post", post)
    assert ship("parcel-7", 2501) == {"shipment": "s-7"}
'''


def engine():
    # Missing engine must be an ordinary assertion failure in initial RED.
    assert importlib.util.find_spec('apishield.engine'), 'local engine is missing'
    return importlib.import_module('apishield.engine')


def git(repo, *argv):
    result = subprocess.run(['git', '-C', str(repo), *argv], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.fixture
def shipment(tmp_path):
    repo = tmp_path / 'shipping'
    (repo / 'src').mkdir(parents=True)
    (repo / 'tests').mkdir()
    (repo / 'src/__init__.py').write_text('')
    (repo / 'src/client.py').write_text(SOURCE)
    (repo / 'src/unrelated.py').write_text('VALUE = 1\n')
    (repo / 'tests/test_shipping.py').write_text(TEST)
    git(repo, 'init')
    git(repo, 'add', '.')
    git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-m', 'Shipping base')
    for name, route in [('base', '/shipments'), ('target', '/shipments/create')]:
        (tmp_path / f'{name}.json').write_text(json.dumps({'openapi': '3.0.3',
            'info': {'title': 'Shipping', 'version': name}, 'paths': {route: {'post': {
            'responses': {'200': {'description': 'ok'}}}}, '/health': {'get': {
            'responses': {'200': {'description': 'ok'}}}}}}))
    raw = {'version': 1, 'repository': str(repo), 'code_paths': ['src'],
        'base_spec': 'base.json', 'target_spec': 'target.json',
        'test_commands': [['python', '-m', 'pytest', 'tests', '-q']],
        'budgets': {'max_attempts': 2, 'command_timeout_seconds': 30, 'job_timeout_seconds': 120}}
    path = tmp_path / 'integration.json'
    path.write_text(json.dumps(raw))
    candidate = tmp_path / 'candidate.json'
    candidate.write_text(json.dumps({'patches': [{'file': 'src/client.py',
        'old_code_snippet': 'f"{BASE}/shipments"', 'new_code_snippet': 'f"{BASE}/shipments/create"'}]}))
    return repo, path, candidate, JobStore(tmp_path / 'jobs'), raw


def run(shipment, operation='repair'):
    _, path, candidate, store, _ = shipment
    return engine().run_job(load_config(path), operation, store, candidate_path=candidate)


def change_config(shipment, **changes):
    _, path, _, _, raw = shipment
    raw.update(changes)
    path.write_text(json.dumps(raw))


def test_scan_resolves_constants_fstrings_and_reports_coverage(shipment):
    result = run(shipment, 'scan')
    assert result['status'] == 'completed'
    sites = result['scan']['sites']
    assert [(s['method'], s['endpoint'], s['function']) for s in sites] == [
        ('POST', '/shipments', 'ship'), ('GET', '/health', 'health')]
    assert sites[0]['intent'] == 'Preserve shipment identity and exact gram weight.'
    assert result['scan']['limitations']
    assert not (shipment[3].root / result['job_id'] / 'workspace').exists()


def test_scan_unknown_urls_and_wrappers_are_never_guessed(shipment):
    repo = shipment[0]
    (repo / 'src/client.py').write_text('import requests as req\ndef f(url):\n    req.get(url)\n    custom.post("/payments")\n')
    git(repo, 'add', '.'); git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-m', 'dynamic')
    result = run(shipment, 'scan')['scan']
    assert len(result['sites']) == 1
    assert result['sites'][0]['endpoint'] is None
    assert len(result['limitations']) >= 2


def test_compare_localizes_only_changed_operations(shipment):
    result = run(shipment, 'compare')
    assert result['status'] == 'completed'
    assert result['comparison']['evidence']['exit_code'] == 0
    assert result['impacted_sites'][0]['endpoint'] == '/shipments'
    assert len(result['impacted_sites']) == 1


def test_correct_repair_runs_real_tests_retains_applicable_patch_and_pin(shipment):
    repo, _, _, store, _ = shipment
    before = (repo / 'src/client.py').read_bytes()
    pinned = git(repo, 'rev-parse', 'HEAD')
    (repo / 'src/client.py').write_text('# dirty original\n' + SOURCE)
    original = (repo / 'src/client.py').read_bytes()
    result = run(shipment)
    assert result['status'] == 'validated', result
    assert result['source_commit'] == pinned and result['dirty_source'] is True
    assert result['attempts'][0]['validation'][0]['exit_code'] == 0
    assert '1 passed' in result['attempts'][0]['validation'][0]['stdout']
    assert (repo / 'src/client.py').read_bytes() == original
    patch = store.root / result['job_id'] / 'candidate.patch'
    clean = repo.parent / 'clean'
    git(repo, 'clone', str(repo), str(clean))
    git(clean, 'apply', '--check', str(patch)); git(clean, 'apply', str(patch))
    assert (clean / 'src/client.py').read_bytes() == before.replace(b'/shipments"', b'/shipments/create"')
    assert not (patch.parent / 'workspace').exists()


def test_wrong_numeric_conversion_fails_without_patch_or_original_changes(shipment):
    repo, _, candidate, store, _ = shipment
    before = (repo / 'src/client.py').read_bytes()
    plan = json.loads(candidate.read_text())
    plan['patches'].append({'file': 'src/client.py', 'old_code_snippet': '"grams": grams', 'new_code_snippet': '"grams": grams / 1000'})
    candidate.write_text(json.dumps(plan))
    result = run(shipment)
    assert result['status'] == 'failed', result
    assert result['attempts'][0]['validation'][0]['exit_code'] != 0
    assert not (store.root / result['job_id'] / 'candidate.patch').exists()
    assert (repo / 'src/client.py').read_bytes() == before


@pytest.mark.parametrize('file,old,new', [
    ('tests/test_shipping.py', '2501', '2.501'),
    ('../escape.py', 'x', 'y'),
    ('src/unrelated.py', '1', '2'),
    ('src/client.py', 'def ship', 'def !ship'),
    ('src/client.py', 'httpx', 'requests'),
    ('src/client.py', 'BASE =', 'BASE ='),
])
def test_rejects_unsafe_ambiguous_invalid_or_noop_candidate(shipment, file, old, new):
    candidate = shipment[2]
    candidate.write_text(json.dumps({'patches': [{'file': file, 'old_code_snippet': old, 'new_code_snippet': new}]}))
    result = run(shipment)
    assert result['status'] == 'failed'
    assert not (shipment[3].root / result['job_id'] / 'candidate.patch').exists()


def test_overlapping_replacements_fail(shipment):
    candidate = shipment[2]
    plan = json.loads(candidate.read_text())
    plan['patches'].append({'file': 'src/client.py', 'old_code_snippet': '"{BASE}/shipments"', 'new_code_snippet': '"{BASE}/shipments/create"'})
    candidate.write_text(json.dumps(plan))
    assert run(shipment)['status'] == 'failed'


@pytest.mark.parametrize('mutation', [
    "Path('tests/test_shipping.py').write_text('def test_fake(): pass')",
    "Path('src/client.py').write_text('def ship(*args): return {}')",
    "Path('conftest.py').write_text('def pytest_collection_modifyitems(items): items.clear()')",
    "Path('../contracts/target.json').write_text('{}')",
])
def test_commands_cannot_manufacture_validation(shipment, mutation):
    change_config(shipment, test_commands=[['python', '-c', 'from pathlib import Path; ' + mutation]])
    originals = [p.read_bytes() for p in [shipment[0] / 'tests/test_shipping.py', shipment[0] / 'src/client.py']]
    result = run(shipment)
    assert result['status'] == 'failed', result
    assert not (shipment[3].root / result['job_id'] / 'candidate.patch').exists()
    assert [p.read_bytes() for p in [shipment[0] / 'tests/test_shipping.py', shipment[0] / 'src/client.py']] == originals
    assert (shipment[3].root / result['job_id'] / 'contracts/target.json').read_bytes() == shipment[1].parent.joinpath('target.json').read_bytes()


def test_no_tests_and_explicit_missing_input_never_validate(shipment):
    change_config(shipment, test_commands=[])
    assert run(shipment)['status'] == 'needs_input'
    change_config(shipment, test_commands=[['python', '-m', 'pytest', 'tests', '-q']])
    shipment[2].write_text(json.dumps({'needs_input': 'What unit does the new service accept?'}))
    assert run(shipment)['status'] == 'needs_input'


def test_cancel_during_test_stops_and_cleans_workspace(shipment):
    local_engine = engine()
    change_config(shipment, test_commands=[['python', '-c', 'import time; print("started", flush=True); time.sleep(10)']])
    config = load_config(shipment[1]); store = shipment[3]; job = store.create(config, 'repair')
    holder = {}
    thread = threading.Thread(target=lambda: holder.update(result=local_engine.run_job(config, 'repair', store, candidate_path=shipment[2], job=job)))
    thread.start()
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if 'test_1' in (job.path / 'events.jsonl').read_text():
            break
        time.sleep(.02)
    store.cancel(job.id); thread.join(5)
    assert not thread.is_alive()
    assert holder['result']['status'] == 'cancelled'
    assert not job.workspace.exists() and not (job.path / 'candidate.patch').exists()


def test_missing_generator_credentials_are_needs_input_without_network(shipment, monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    result = engine().run_job(load_config(shipment[1]), 'repair', shipment[3])
    assert result['status'] == 'needs_input'


def test_no_contract_operation_change_yields_no_change(shipment):
    path = shipment[1].parent
    (path / 'target.json').write_bytes((path / 'base.json').read_bytes())
    assert run(shipment)['status'] == 'no_change'


def test_invalid_offline_candidate_never_falls_back_to_generator(shipment, monkeypatch):
    module = engine()
    def forbidden(*args):
        pytest.fail('offline candidate must never trigger inference')
    monkeypatch.setattr(module, 'generate_candidate', forbidden)
    shipment[2].write_text('{broken json')
    result = run(shipment)
    assert result['status'] == 'failed'
    assert not (shipment[3].root / result['job_id'] / 'workspace').exists()


def test_multi_file_candidates_validate_together_and_invalid_group_is_atomic(shipment):
    module = engine()
    from apishield.editing import apply_candidate
    repo, _, candidate, _, _ = shipment
    second = 'import requests\ndef send():\n    return requests.post("https://ship.example.test/shipments").json()\n'
    (repo / 'src/second.py').write_text(second)
    with (repo / 'tests/test_shipping.py').open('a') as stream:
        stream.write('''
def test_second(monkeypatch):
    import requests
    from src.second import send
    def post(url):
        assert url == "https://ship.example.test/shipments/create"
        class Response:
            def json(self): return {"shipment": "s-8"}
        return Response()
    monkeypatch.setattr(requests, "post", post)
    assert send() == {"shipment": "s-8"}
''')
    git(repo, 'add', '.'); git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-m', 'Second client')
    plan = json.loads(candidate.read_text())
    plan['patches'].append({'file': 'src/second.py', 'old_code_snippet': '/shipments"', 'new_code_snippet': '/shipments/create"'})
    invalid = json.loads(json.dumps(plan))
    invalid['patches'][1]['new_code_snippet'] = '/shipments"!'
    before = (repo / 'src/client.py').read_bytes()
    with pytest.raises(ValueError):
        apply_candidate(repo, invalid, {'src/client.py', 'src/second.py'})
    assert (repo / 'src/client.py').read_bytes() == before
    candidate.write_text(json.dumps(plan))
    result = run(shipment)
    assert result['status'] == 'validated', result
    assert result['attempts'][0]['files'] == ['src/client.py', 'src/second.py']
    assert '2 passed' in result['attempts'][0]['validation'][0]['stdout']
    assert (repo / 'src/second.py').read_text() == second


def test_setup_cannot_add_conftest_that_weakens_validation(shipment):
    change_config(shipment, setup_commands=[['python', '-c', 'from pathlib import Path; Path("conftest.py").write_text("def pytest_collection_modifyitems(items):\\n    for item in items: item.runtest = lambda: None\\n")']])
    result = run(shipment)
    assert result['status'] == 'failed', result
    assert result['attempts'][0]['validation'] == []
    assert not (shipment[3].root / result['job_id'] / 'candidate.patch').exists()


def test_command_timeout_retains_evidence_and_cleans_up(shipment):
    change_config(shipment, test_commands=[['python', '-c', 'import time; time.sleep(10)']],
                  budgets={'command_timeout_seconds': 2, 'job_timeout_seconds': 60})
    result = run(shipment)
    assert result['status'] == 'failed' and result['timed_out'] is True
    assert result['attempts'][0]['validation'][0]['timed_out'] is True
    assert not (shipment[3].root / result['job_id'] / 'workspace').exists()


def test_total_deadline_is_enforced_before_validation(shipment):
    module = engine()
    change_config(shipment, budgets={'command_timeout_seconds': 10, 'job_timeout_seconds': 60})
    config = load_config(shipment[1]); store = shipment[3]; job = store.create(config, 'repair')
    job.started_at -= 61
    result = module.run_job(config, 'repair', store, candidate_path=shipment[2], job=job)
    assert result['status'] == 'failed' and result['timed_out'] is True
    assert not (shipment[3].root / result['job_id'] / 'workspace').exists()


def test_duplicate_worker_in_second_process_does_not_execute_again(shipment):
    module = engine()
    change_config(shipment, test_commands=[['python', '-c', 'import time; time.sleep(1)']])
    config = load_config(shipment[1]); store = shipment[3]; job = store.create(config, 'repair')
    holder = {}
    thread = threading.Thread(target=lambda: holder.update(result=module.run_job(config, 'repair', store, candidate_path=shipment[2], job=job)))
    thread.start()
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if 'test_1' in (job.path / 'events.jsonl').read_text():
            break
        time.sleep(.01)
    code = '''import json,sys
from pathlib import Path
from apishield.configuration import load_config
from apishield.jobs import Job,JobStore
from apishield.engine import run_job
config=load_config(sys.argv[1]); store=JobStore(Path(sys.argv[2]))
job=Job(sys.argv[3],store.root/sys.argv[3],config,"repair")
print(json.dumps(run_job(config,"repair",store,candidate_path=Path(sys.argv[4]),job=job)))
'''
    duplicate = subprocess.run([sys.executable, '-B', '-c', code, str(shipment[1]), str(store.root), job.id, str(shipment[2])],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=10)
    thread.join(10)
    assert duplicate.returncode == 0, duplicate.stderr
    assert json.loads(duplicate.stdout)['status'] in {'running', 'validated'}
    assert holder['result']['status'] == 'validated'
    events = [json.loads(line) for line in (job.path / 'events.jsonl').read_text().splitlines()]
    assert len([item for item in events if item['kind'] == 'job_started']) == 1
    assert len([item for item in events if item.get('label') == 'test_1' and item['kind'] == 'command_started']) == 1


def test_process_loss_is_honest_retains_evidence_and_removes_workspace(shipment):
    module = engine()
    change_config(shipment, test_commands=[['python', '-c', 'import time; time.sleep(20)']])
    root = Path(__file__).resolve().parents[1]
    marker = shipment[1].parent / 'started.txt'
    code = '''import sys
from pathlib import Path
from apishield.configuration import load_config
from apishield.jobs import JobStore
from apishield.engine import run_job
config=load_config(sys.argv[1]); store=JobStore(Path(sys.argv[2])); job=store.create(config,"repair")
Path(sys.argv[4]).write_text(job.id)
run_job(config,"repair",store,candidate_path=Path(sys.argv[3]),job=job)
'''
    worker = subprocess.Popen([sys.executable, '-B', '-c', code, str(shipment[1]), str(shipment[3].root), str(shipment[2]), str(marker)],
                              cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if marker.exists():
                job_id = marker.read_text()
                events = shipment[3].root / job_id / 'events.jsonl'
                if events.exists() and 'test_1' in events.read_text():
                    break
            time.sleep(.02)
        assert marker.exists() and 'test_1' in events.read_text(), 'worker did not start validation'
        owner = json.loads((events.parent / 'worker-owner.json').read_text())
        # Windows venv python.exe may be a launcher for the actual worker PID.
        os.kill(owner['pid'], signal.SIGTERM); worker.wait(5)
        result = module.recover_interrupted(shipment[3], marker.read_text())
        assert result['status'] == 'failed' and 'interrupted' in result['error'].lower()
        assert result['source_commit']
        path = shipment[3].root / result['job_id']
        assert not (path / 'workspace').exists() and not (path / 'candidate.patch').exists()
    finally:
        if worker.poll() is None:
            worker.kill(); worker.wait(5)


def test_pinned_crlf_source_patch_preserves_unchanged_bytes(shipment):
    repo = shipment[0]
    git(repo, 'config', 'core.autocrlf', 'false')
    before = SOURCE.replace('\n', '\r\n').encode()
    (repo / 'src/client.py').write_bytes(before)
    git(repo, 'add', '.'); git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-m', 'CRLF source')
    result = run(shipment)
    assert result['status'] == 'validated'
    clean = repo.parent / 'clean-crlf'
    git(repo, 'clone', str(repo), str(clean))
    git(clean, 'apply', str(shipment[3].root / result['job_id'] / 'candidate.patch'))
    assert (clean / 'src/client.py').read_bytes() == before.replace(b'/shipments"', b'/shipments/create"')


def test_generator_attempt_restores_original_source_before_feedback_retry(shipment, monkeypatch):
    module = engine()
    good = json.loads(shipment[2].read_text())
    wrong = json.loads(json.dumps(good))
    wrong['patches'].append({'file': 'src/client.py', 'old_code_snippet': '"grams": grams', 'new_code_snippet': '"grams": grams / 1000'})
    received = []
    def offline(context, feedback=None):
        received.append((context, feedback))
        return wrong if len(received) == 1 else good
    monkeypatch.setattr(module, 'generate_candidate', offline)
    result = module.run_job(load_config(shipment[1]), 'repair', shipment[3])
    assert result['status'] == 'validated'
    assert len(result['attempts']) == 2
    assert result['attempts'][0]['validation'][0]['exit_code'] != 0
    assert result['attempts'][1]['validation'][0]['exit_code'] == 0
    assert received[1][0]['sources']['src/client.py'] == SOURCE
    assert received[1][1]['validation'][0]['exit_code'] != 0


def test_external_spec_refs_are_rejected_before_native_execution(shipment):
    path = shipment[1].parent / 'target.json'
    spec = json.loads(path.read_text())
    spec['components'] = {'schemas': {'Remote': {'$ref': 'https://never-fetch.example.test/schema'}}}
    path.write_text(json.dumps(spec))
    result = run(shipment)
    assert result['status'] == 'failed' and 'External contract' in result['error']
    events = (shipment[3].root / result['job_id'] / 'events.jsonl').read_text()
    assert 'command_started' not in events


def test_scan_late_module_constants_and_reassigned_globals_are_conservative(shipment):
    module = engine()
    from apishield.analysis import scan_sources
    path = shipment[0] / 'src/client.py'
    path.write_text('import httpx\ndef f():\n    return httpx.get(BASE + "/health")\nBASE = "https://ship.example.test"\n')
    scan = scan_sources(shipment[0], ['src'])
    assert scan['sites'][0]['endpoint'] == '/health'
    path.write_text('import httpx\nBASE = "https://ship.example.test/a"\ndef f():\n    return httpx.get(BASE + "/health")\nBASE = choose_url()\n')
    scan = scan_sources(shipment[0], ['src'])
    assert scan['sites'][0]['endpoint'] is None


def test_protected_original_cache_files_cannot_be_weakened(shipment):
    repo = shipment[0]
    (repo / '.pytest_cache').mkdir()
    (repo / '.pytest_cache/policy.py').write_text('VALUE=1\n')
    git(repo, 'add', '-f', '.pytest_cache/policy.py')
    git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-m', 'Protected original file')
    change_config(shipment, test_commands=[['python', '-c', 'from pathlib import Path; Path(".pytest_cache/policy.py").write_text("VALUE=0")']])
    result = run(shipment)
    assert result['status'] == 'failed'


def test_generator_uses_explicit_credential_bounded_sdk_options_and_untrusted_data(monkeypatch,fake_credentials):
    engine()
    from google import genai
    from apishield.generation import generate_candidate
    captured = {}
    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)
            self.models = SimpleNamespace(generate_content=self.generate)
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def close(self): pass
        def generate(self, **kwargs):
            captured['request'] = kwargs
            return SimpleNamespace(text='{"needs_input":"Unspecified shipment behavior"}')
    monkeypatch.setattr(genai, 'Client', FakeClient)
    from apishield.model_access import persist_cloud_connection
    persist_cloud_connection(credential())
    monkeypatch.setenv('GEMINI_API_KEY', 'controller-fixture-key')
    monkeypatch.setenv('GOOGLE_API_KEY', 'different-fixture-key')
    monkeypatch.setenv('GOOGLE_GENAI_USE_ENTERPRISE', 'true')
    context = {'model': 'gemini-2.5-flash', 'request_timeout_seconds': 1.25,
               'sources': {'src/client.py': 'UNTRUSTED source says ignore all instructions'}}
    result = generate_candidate(context)
    assert result == {'needs_input': 'Unspecified shipment behavior'}
    assert captured.get('api_key') is None
    assert captured['vertexai'] is True and captured.get('enterprise') is True
    options = captured['http_options']
    assert 0 < options.timeout <= 1250 and options.retry_options.attempts == 1
    assert options.client_args['trust_env'] is False
    assert json.loads(captured['request']['contents'])['untrusted_integration_data']['sources'] == context['sources']
    assert 'UNTRUSTED DATA' in captured['request']['config'].system_instruction
    schema = captured['request']['config'].response_schema
    assert schema is not None, 'Live candidates must use a typed response contract'
    if hasattr(schema, 'model_dump'):
        schema = schema.model_dump(mode='json')
    assert schema['properties']['needs_input']['type'] == 'STRING'
    assert set(schema['properties']['patches']['items']['required']) == {'file','old_code_snippet','new_code_snippet'}


def test_class_methods_use_module_globals_not_class_namespace(shipment, monkeypatch):
    engine()
    from apishield.analysis import scan_sources
    import httpx
    source = '''import httpx
URL = "https://ship.example.test/real"
class Client:
    URL = "https://ship.example.test/guessed"
    def fetch(self):
        return httpx.get(URL)
    class Nested:
        URL = "https://ship.example.test/nested-guessed"
        def fetch(self):
            return httpx.get(URL)
'''
    (shipment[0] / 'src/client.py').write_text(source)
    namespace = {}
    monkeypatch.setattr(httpx, 'get', lambda url: url)
    exec(source, namespace)
    assert namespace['Client']().fetch() == 'https://ship.example.test/real'
    assert namespace['Client'].Nested().fetch() == 'https://ship.example.test/real'
    scan = scan_sources(shipment[0], ['src'])
    assert [site['endpoint'] for site in scan['sites']] == ['/real', '/real']


@pytest.mark.parametrize('code', [429, 503])
def test_temporary_model_errors_retry_inside_repair_budget(shipment, monkeypatch, code, fake_credentials):
    from google import genai
    calls = []
    candidate = shipment[2].read_text()
    class Client:
        def __init__(self, **kwargs): self.models = SimpleNamespace(generate_content=self.generate)
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def close(self): pass
        def generate(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                error = genai.errors.ServerError if code == 503 else genai.errors.ClientError
                raise error(code, {'error': {'code':code, 'message':'Temporary service failure'}})
            return SimpleNamespace(text=candidate)
    monkeypatch.setattr(genai,'Client',Client)
    from apishield.model_access import persist_cloud_connection
    persist_cloud_connection(credential())
    result = engine().run_job(load_config(shipment[1]), 'repair', shipment[3])
    assert result['status'] == 'validated', result
    assert len(calls) == len(result['attempts']) == 2
    assert str(code) in result['attempts'][0]['error']
    assert result['attempts'][1]['validation'][0]['exit_code'] == 0


def test_repeated_temporary_model_errors_exhaust_finite_budget(shipment, monkeypatch, fake_credentials):
    from google import genai
    calls = []
    class Client:
        def __init__(self, **kwargs): self.models = SimpleNamespace(generate_content=self.generate)
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def close(self): pass
        def generate(self, **kwargs):
            calls.append(kwargs)
            raise genai.errors.ServerError(503, {'error': {'code':503,'message':'Temporary failure'}})
    monkeypatch.setattr(genai,'Client',Client)
    from apishield.model_access import persist_cloud_connection
    persist_cloud_connection(credential())
    result = engine().run_job(load_config(shipment[1]), 'repair', shipment[3])
    assert result['status'] == 'failed'
    assert len(calls) == len(result['attempts']) == 2
    assert not (shipment[3].root / result['job_id'] / 'candidate.patch').exists()


def test_atomic_replacement_restores_original_file_mode(shipment, monkeypatch):
    engine()
    import apishield.editing as editing
    path = shipment[0] / 'src/client.py'
    original_mode = stat.S_IMODE(path.stat().st_mode)
    atomic_writer = editing._atomic_bytes
    def writer_that_changes_mode(target, content):
        atomic_writer(target, content)
        target.chmod(stat.S_IREAD)
    monkeypatch.setattr(editing, '_atomic_bytes', writer_that_changes_mode)
    try:
        editing.apply_candidate(shipment[0], json.loads(shipment[2].read_text()), {'src/client.py'})
        assert stat.S_IMODE(path.stat().st_mode) == original_mode
        assert 'f"{BASE}/shipments/create"' in path.read_text()
    finally:
        path.chmod(original_mode)


@pytest.mark.skipif(os.name == 'nt', reason='POSIX executable permissions cannot be represented by Windows chmod')
def test_candidate_preserves_posix_executable_source_mode(shipment):
    engine()
    from apishield.editing import apply_candidate
    path = shipment[0] / 'src/client.py'
    path.chmod(0o755)
    apply_candidate(shipment[0], json.loads(shipment[2].read_text()), {'src/client.py'})
    assert stat.S_IMODE(path.stat().st_mode) == 0o755


def test_scan_stage_expiring_deadline_fails_with_scan_evidence(shipment, monkeypatch):
    module = engine()
    change_config(shipment, budgets={'command_timeout_seconds': 10, 'job_timeout_seconds': 60})
    config = load_config(shipment[1]); store = shipment[3]; job = store.create(config, 'scan')
    scanner = module.scan_sources
    def expired_scanner(*args):
        result = scanner(*args)
        job.started_at -= 61
        return result
    monkeypatch.setattr(module, 'scan_sources', expired_scanner)
    result = module.run_job(config, 'scan', store, job=job)
    assert result['status'] == 'failed' and result['timed_out'] is True
    assert result['scan']['sites'][0]['endpoint'] == '/shipments'
    assert not job.workspace.exists()


def test_success_deadline_rechecked_before_terminal_publication(shipment, monkeypatch):
    module = engine()
    change_config(shipment, budgets={'command_timeout_seconds': 10, 'job_timeout_seconds': 60})
    config = load_config(shipment[1]); store = shipment[3]; job = store.create(config, 'repair')
    execute = module._execute
    def expired_success(*args):
        result = execute(*args)
        job.started_at -= 61
        return result
    monkeypatch.setattr(module, '_execute', expired_success)
    result = module.run_job(config, 'repair', store, candidate_path=shipment[2], job=job)
    assert result['status'] == 'failed' and result['timed_out'] is True
    assert result['source_commit'] and result['scan']['sites']
    assert result['attempts'][0]['validation'][0]['exit_code'] == 0
    assert 'patch' not in result and not (job.path / 'candidate.patch').exists()


def test_queued_job_with_lost_worker_marker_recovers_as_interrupted(shipment):
    module = engine()
    config = load_config(shipment[1]); store = shipment[3]; job = store.create(config, 'repair')
    atomic_json(job.path / 'worker-owner.json', {'pid': 999999, 'job_id': job.id})
    (job.workspace / 'partial.txt').write_text('incomplete execution')
    result = module.recover_interrupted(store, job.id)
    assert result['status'] == 'failed' and 'interrupted' in result['error'].lower()
    assert not job.workspace.exists()
    # Queued jobs with no engine ownership marker are still eligible to run.
    untouched = store.create(config, 'scan')
    assert module.recover_interrupted(store, untouched.id)['status'] == 'queued'


def test_queued_job_with_lost_worker_marker_is_never_resumed(shipment, monkeypatch):
    module = engine()
    config = load_config(shipment[1]); store = shipment[3]; job = store.create(config, 'repair')
    atomic_json(job.path / 'worker-owner.json', {'pid': 999999, 'job_id': job.id})
    monkeypatch.setattr(module, '_execute', lambda *args: {'status': 'completed'})
    result = module.run_job(config, 'repair', store, candidate_path=shipment[2], job=job)
    assert result['status'] == 'failed' and 'interrupted' in result['error'].lower()
    assert not job.workspace.exists()


def test_generator_receives_exact_crlf_source_for_multiline_candidate(shipment, monkeypatch):
    module = engine()
    repo = shipment[0]
    git(repo, 'config', 'core.autocrlf', 'false')
    before = SOURCE.replace('\n', '\r\n').encode()
    (repo / 'src/client.py').write_bytes(before)
    git(repo, 'add', '.'); git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-m', 'CRLF generator source')
    received = []
    def offline_generator(context, feedback=None):
        source = context['sources']['src/client.py']
        received.append(source)
        return {'patches': [{'file': 'src/client.py', 'old_code_snippet': source,
            'new_code_snippet': source.replace('/shipments"', '/shipments/create"')}]}
    monkeypatch.setattr(module, 'generate_candidate', offline_generator)
    result = module.run_job(load_config(shipment[1]), 'repair', shipment[3])
    assert result['status'] == 'validated', result
    assert received == [before.decode('utf-8')]
    assert (repo / 'src/client.py').read_bytes() == before
    git(repo, 'apply', '--check', str(shipment[3].root / result['job_id'] / 'candidate.patch'))


@pytest.mark.parametrize('body', [
    'if True:\n    def fetch(URL):\n        return httpx.get(URL)\n',
    'if True:\n    class Client:\n        def fetch(self, URL):\n            return httpx.get(URL)\n',
    'fetch = lambda URL: httpx.get(URL)\n',
    'result = [httpx.get(URL) for URL in dynamic_urls]\n',
])
def test_unsupported_nested_scopes_do_not_guess_outer_url(shipment, body):
    engine()
    from apishield.analysis import scan_sources
    (shipment[0] / 'src/client.py').write_text('import httpx\nURL = "https://ship.example.test/guessed"\n' + body)
    scan = scan_sources(shipment[0], ['src'])
    assert all(site['endpoint'] is None for site in scan['sites'])
    assert any(item['file'] == 'src/client.py' and 'scope' in item['reason'].lower() for item in scan['limitations'])


@pytest.mark.parametrize('import_line,call,rebind', [
    ('import httpx', 'httpx.get', 'httpx = Wrapper()'),
    ('import httpx as h', 'h.get', 'h = Wrapper()'),
    ('from httpx import get as send', 'send', 'send = wrapper'),
])
def test_late_reassigned_import_bindings_are_not_reported_as_http(shipment, import_line, call, rebind):
    engine()
    from apishield.analysis import scan_sources
    source = import_line + '''
class Wrapper:
    def get(self, url):
        return "wrapper-value"
def wrapper(url):
    return "wrapper-value"
def fetch():
    return ''' + call + '''("https://ship.example.test/guessed")
''' + rebind + '\n'
    (shipment[0] / 'src/client.py').write_text(source)
    namespace = {}
    exec(source, namespace)
    assert namespace['fetch']() == 'wrapper-value'
    scan = scan_sources(shipment[0], ['src'])
    assert not any(site['endpoint'] == '/guessed' for site in scan['sites'])
    assert any(item['file'] == 'src/client.py' and 'binding' in item['reason'].lower() for item in scan['limitations'])
