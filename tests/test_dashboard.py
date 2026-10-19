import json
import subprocess

import httpx
import pytest
from fastapi.testclient import TestClient

import dashboard_api as dashboard


@pytest.fixture
def api(monkeypatch, tmp_path):
    import threading
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'client_app').mkdir()
    (tmp_path / 'client_app/payment_service.py').write_text('before\n')
    (tmp_path / 'agent').mkdir()
    monkeypatch.setattr(dashboard, 'state', dashboard.AppState())
    monkeypatch.setattr(dashboard, 'agent_lock', threading.Lock())
    # No lifespan: automatic monitor must not call real providers/models in tests.
    return TestClient(dashboard.app)


def test_missing_provider_cannot_fake_a_version_switch(api, monkeypatch):
    def unavailable(*args, **kwargs):
        raise httpx.ConnectError('offline')
    monkeypatch.setattr(httpx, 'post', unavailable)
    response = api.post('/api/provider/switch', json={'version': 'v2'})
    assert response.status_code == 503
    assert dashboard.state.provider_version == 'v1'


def test_version_switch_uses_actual_provider_result(api, monkeypatch):
    def switch(url, **kwargs):
        assert url.endswith('/api/version')
        assert kwargs['json'] == {'version': 'v3'}
        return httpx.Response(200, json={'version': 'v3'}, request=httpx.Request('POST', url))
    monkeypatch.setattr(httpx, 'post', switch)
    result = api.post('/api/provider/switch', json={'version': 'v3'})
    assert result.status_code == 200
    assert result.json()['active_version'] == 'v3'
    assert dashboard.state.agent_status == 'upgrade_available'


def test_success_text_without_validation_evidence_is_failure(api, monkeypatch):
    monkeypatch.setattr(dashboard, 'run_agent_process', lambda *args, **kwargs: subprocess.CompletedProcess([], 0, b'Self-Healing Cycle Complete!', b''))
    dashboard._run_agent_subprocess()
    assert dashboard.state.agent_status == 'failed'


def test_failed_result_overrules_success_stdout(api, monkeypatch):
    def run(*args, **kwargs):
        with open('agent/result.json', 'w') as stream:
            json.dump({'final_status': 'failed', 'validation': {'tests_passed': False}, 'ips_score': None}, stream)
        return subprocess.CompletedProcess([], 1, b'Self-Healing Cycle Complete!', b'')
    monkeypatch.setattr(dashboard, 'run_agent_process', run)
    dashboard._run_agent_subprocess()
    assert dashboard.state.agent_status == 'failed'
    assert dashboard.state.ips_score is None


def test_validated_result_requires_passed_tests(api, monkeypatch):
    def run(*args, **kwargs):
        with open('agent/result.json', 'w') as stream:
            json.dump({'final_status': 'validated', 'validation': {'tests_passed': False}}, stream)
        return subprocess.CompletedProcess([], 0, b'', b'')
    monkeypatch.setattr(dashboard, 'run_agent_process', run)
    dashboard._run_agent_subprocess()
    assert dashboard.state.agent_status == 'failed'


def test_settings_cannot_enable_automatic_merge(api):
    response = api.post('/api/settings/auto-merge', json={'enabled': True})
    assert response.status_code == 400


def test_dashboard_switch_and_sync_use_real_provider_contract(api, monkeypatch):
    from mock_provider import main as provider
    monkeypatch.setattr(provider, 'ACTIVE_VERSION', 'v1')
    with TestClient(provider.app) as upstream:
        monkeypatch.setattr(httpx, 'post', lambda url, **kw: upstream.post('/api/version', json=kw['json']))
        monkeypatch.setattr(httpx, 'get', lambda url, **kw: upstream.get('/api/version'))
        switched = api.post('/api/provider/switch', json={'version': 'v2'})
        assert switched.status_code == 200, switched.text
        assert switched.json()['active_version'] == 'v2'
        assert dashboard.sync_provider_version() == 'v2'


def test_timeout_after_edit_restores_parent_snapshot(api, monkeypatch):
    from pathlib import Path
    original = Path('client_app/payment_service.py').read_bytes()
    def run(*args, **kw):
        Path('client_app/payment_service.py').write_bytes(b'unvalidated candidate')
        Path('client_app/created.py').write_bytes(b'new side effect')
        raise subprocess.TimeoutExpired(args[0], 300)
    monkeypatch.setattr(dashboard, 'run_agent_process', run)
    dashboard._run_agent_subprocess()
    assert dashboard.state.agent_status == 'failed'
    assert Path('client_app/payment_service.py').read_bytes() == original
    assert not Path('client_app/created.py').exists()


def test_cleanup_failure_blocks_further_edits(api, monkeypatch):
    def run(*args, **kw):
        raise dashboard.ProcessCleanupError('process still owns files')
    monkeypatch.setattr(dashboard, 'run_agent_process', run)
    dashboard._run_agent_subprocess()
    assert dashboard.state.agent_status == 'needs_input'
    assert dashboard.agent_lock.locked()
    assert api.post('/api/provider/switch', json={'version': 'v2'}).status_code == 409
