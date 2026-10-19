import json
from dataclasses import replace
from test_local_engine import shipment
from apishield.configuration import load_config
from apishield.engine import run_job


def test_browser_repair_runs_generated_checks_before_and_after_model_patch(shipment, monkeypatch):
    repo, path, candidate, store, raw = shipment
    check = '''import httpx
from src.client import ship
def test_generated_route(monkeypatch):
    def post(url, *, json):
        assert url.endswith('/shipments/create')
        return httpx.Response(200, json={'ok': True})
    monkeypatch.setattr(httpx, 'post', post)
    assert ship('a', 42) == {'ok': True}
'''
    intent_calls = []
    def infer(context, connection, **kwargs):
        intent_calls.append((context, kwargs))
        return {'rules': [], 'checks': [
            {'file': 'tests/apishield_generated/test_route.py', 'code': check}], 'model': 'gemini-3.8-flash'}
    monkeypatch.setattr('apishield.intent.infer_intent', infer)
    monkeypatch.setattr('apishield.engine.generate_candidate', lambda *a, **k: json.loads(candidate.read_text()))
    config = replace(load_config(path), source_mode='working')
    job = store.create(config, 'repair')
    job._initial['browser_ai'] = True
    result = run_job(config, 'repair', store, job=job)
    assert result['status'] == 'validated', result.get('error')
    context, callbacks = intent_calls[0]
    assert 0 < context['request_timeout_seconds'] <= config.budgets.command_timeout_seconds
    assert context['request_timeout_seconds'] <= context['intent_timeout_seconds'] <= config.budgets.job_timeout_seconds
    assert callable(callbacks['check']) and callable(callbacks['on_activity'])
    assert result['ai_intent']['model'] == 'gemini-3.8-flash'
    assert result['generated_baseline']['exit_code'] != 0
    assert result['generated_validation']['passed'] is True
    assert (job.path / 'applied-files/src/client.py').is_file()
    assert not (repo / 'tests/apishield_generated').exists()
    events = [json.loads(line) for line in (job.path / 'events.jsonl').read_text().splitlines()]
    stages = [e['stage'] for e in events if e['kind'] == 'activity']
    assert stages == ['prepare', 'analyze', 'analyze', 'intent', 'intent', 'repair', 'repair', 'validate', 'review']
