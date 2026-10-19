import json
import subprocess
import time
import sys
import threading
import types
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

import dashboard_api
from apishield.configuration import load_config
from apishield.jobs import JobStore, atomic_json
from apishield.dashboard_jobs import LocalJobs


def configured_source(tmp_path):
    repo = tmp_path / 'integration-source'
    (repo / 'src').mkdir(parents=True)
    (repo / 'src/client.py').write_text('import httpx\ndef ping():\n    return httpx.get("https://parcel.example.test/ping")\n')
    subprocess.run(['git', 'init', str(repo)], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(repo), 'add', 'src'], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                    'commit', '-m', 'Source'], check=True, capture_output=True)
    for name in ('base.json', 'target.json'):
        (tmp_path / name).write_text('{}')
    path = tmp_path / 'configured.json'
    path.write_text(json.dumps({'version': 1, 'repository': str(repo), 'code_paths': ['src'],
        'base_spec': 'base.json', 'target_spec': 'target.json'}))
    return path


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    monkeypatch.setenv('APISHIELD_JOBS_DIR', str(tmp_path / 'jobs'))
    monkeypatch.setenv('APISHIELD_INTEGRATIONS', '{}')
    previous = getattr(dashboard_api.app.state, 'local_jobs', None)
    if previous:
        previous.close()
        del dashboard_api.app.state.local_jobs
    yield TestClient(dashboard_api.app)
    service = getattr(dashboard_api.app.state, 'local_jobs', None)
    if service:
        service.close()
        del dashboard_api.app.state.local_jobs


def test_dashboard_lists_persisted_jobs_without_demo_state(api):
    response = api.get('/api/jobs')
    assert response.status_code == 200
    assert response.json()['jobs'] == []


def test_dashboard_rejects_arbitrary_posted_commands(api):
    response = api.post('/api/jobs', json={'integration': 'parcel', 'operation': 'repair',
        'test_commands': [['python', '-c', 'print("unsafe")']]})
    assert response.status_code == 422


def test_dashboard_reads_report_created_by_cli_store(api, tmp_path):
    repo = tmp_path / 'source'
    repo.mkdir()
    subprocess.run(['git', 'init', str(repo)], check=True, capture_output=True)
    for name in ('base.json', 'target.json'):
        (tmp_path / name).write_text('{}')
    config_path = tmp_path / 'integration.json'
    config_path.write_text(json.dumps({'version': 1, 'repository': str(repo), 'code_paths': ['src'],
        'base_spec': 'base.json', 'target_spec': 'target.json'}))
    store = JobStore(tmp_path / 'jobs')
    job = store.create(load_config(config_path), 'scan')
    job.finish({'status': 'completed', 'scan': {'sites': []}})
    job.cleanup()
    response = api.get(f'/api/jobs/{job.id}')
    assert response.status_code == 200
    assert response.json()['job_id'] == job.id
    assert response.json()['status'] == 'completed'


def test_dashboard_does_not_offer_patch_without_validation(api, tmp_path):
    assert api.get('/api/jobs/' + 'f' * 32 + '/patch').status_code == 404


def test_dashboard_only_runs_server_configured_integrations(api):
    response = api.post('/api/jobs', json={'integration': 'not-configured', 'operation': 'scan'})
    assert response.status_code == 404
    assert 'integration' in response.json()['detail'].lower()


def test_dashboard_background_scan_uses_generic_engine(api, tmp_path, monkeypatch):
    path = configured_source(tmp_path)
    monkeypatch.setenv('APISHIELD_INTEGRATIONS', json.dumps({'parcel': str(path)}))
    response = api.post('/api/jobs', json={'integration': 'parcel', 'operation': 'scan'})
    assert response.status_code == 202
    job_id = response.json()['job_id']
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        report = api.get(f'/api/jobs/{job_id}').json()
        if report['status'] not in {'queued', 'running'}:
            break
        time.sleep(.05)
    assert report['status'] == 'completed', report
    assert report['source_commit']
    assert api.post(f'/api/jobs/{job_id}/cancel').json()['status'] == 'completed'
    assert api.get(f'/api/jobs/{job_id}/patch').status_code == 409


def test_dashboard_reports_interrupted_jobs_after_owner_process_loss(tmp_path):
    path = configured_source(tmp_path)
    store = JobStore(tmp_path / 'jobs')
    job = store.create(load_config(path), 'scan')
    atomic_json(job.path / 'owner.json', {'owner': 'dashboard', 'pid': 2147483647})
    service = LocalJobs(store.root, {'parcel': str(path)})
    try:
        report = service.store.get(job.id)
        assert report['status'] == 'failed'
        assert 'interrupted' in report['error'].lower()
        assert report['cancellation_requested']
        assert not job.workspace.exists()
    finally:
        service.close()


def test_dashboard_invalid_server_configuration_is_explicit(api, monkeypatch):
    monkeypatch.setenv('APISHIELD_INTEGRATIONS', '["not a mapping"]')
    response = api.get('/api/integrations')
    assert response.status_code == 503
    assert 'configuration invalid' in response.json()['detail'].lower()


def test_dashboard_cancellation_reaches_background_worker(api, tmp_path, monkeypatch):
    path = configured_source(tmp_path)
    monkeypatch.setenv('APISHIELD_INTEGRATIONS', json.dumps({'parcel': str(path)}))
    started = threading.Event()
    finished = threading.Event()
    fake_engine = types.ModuleType('apishield.engine')

    def cooperative_worker(config, operation, store, *, job):
        started.set()
        deadline = time.monotonic() + 5
        while not job.cancelled() and time.monotonic() < deadline:
            time.sleep(.02)
        job.finish({'status': 'cancelled' if job.cancelled() else 'failed'})
        job.cleanup()
        finished.set()

    fake_engine.run_job = cooperative_worker
    fake_engine.recover_interrupted = lambda store, job_id: store.get(job_id)
    monkeypatch.setitem(sys.modules, 'apishield.engine', fake_engine)
    response = api.post('/api/jobs', json={'integration': 'parcel', 'operation': 'scan'})
    job_id = response.json()['job_id']
    assert started.wait(3)
    response = api.post(f'/api/jobs/{job_id}/cancel')
    assert response.status_code == 200
    assert response.json()['cancellation_requested']
    assert finished.wait(3)
    assert api.get(f'/api/jobs/{job_id}').json()['status'] == 'cancelled'
