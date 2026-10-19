from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def api(tmp_path):
    from apishield.dashboard_jobs import LocalJobs
    from apishield.project_api import router
    from apishield.projects import ClientProject, ProviderBinding
    jobs = LocalJobs(tmp_path / 'jobs', {})
    jobs.automation.projects.save(ClientProject('cinema', str(tmp_path), [ProviderBinding('payment', 'pay', 'http://localhost:8102')]).to_dict(), 0)
    app = FastAPI()
    app.state.local_jobs = jobs
    app.include_router(router)
    yield TestClient(app), jobs
    jobs.close()


def test_project_snapshot_and_mode_are_server_persisted(api):
    client, jobs = api
    response = client.get('/api/projects/cinema')
    assert response.status_code == 200
    assert response.json()['project']['automation_mode'] == 'manual'
    assert response.json()['providers'][0]['monitoring']['configured'] is False
    assert client.patch('/api/projects/cinema/automation', json={'mode': 'automatic_edit', 'expected_revision': 1}).status_code == 422
    assert client.patch('/api/projects/cinema/automation', json={'mode': 'manual', 'expected_revision': 1}).status_code == 200
    assert jobs.automation.projects.load_project('cinema').revision == 2
    assert client.patch('/api/projects/cinema/automation', json={'mode': 'manual', 'expected_revision': 1}).status_code == 422


def test_project_mutations_reject_remote_and_cross_origin(api):
    client, jobs = api
    assert client.patch('/api/projects/cinema/automation', headers={'Origin': 'https://evil.test'}, json={'mode': 'manual', 'expected_revision': 1}).status_code == 403
    remote = TestClient(client.app, client=('192.168.1.55', 1234))
    assert remote.get('/api/projects/cinema').status_code == 403


def test_workflow_retains_failed_state_and_live_evidence(api):
    client, jobs = api
    record = jobs.automation.observe('cinema', {'payment': {'observed_hash': 'a'*64}}, 'b'*40)
    jobs.automation.update('cinema', record['workflow_id'], state='failed', error='Provider unavailable')
    rows = client.get('/api/projects/cinema/workflows').json()['workflows']
    assert rows[0]['state'] == 'failed' and rows[0]['error'] == 'Provider unavailable'
