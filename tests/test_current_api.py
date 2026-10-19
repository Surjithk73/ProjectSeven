import json

from apishield.dashboard_jobs import LocalJobs
from apishield.configuration import load_config
from test_dashboard_jobs import api


def test_banking_documentation_tracks_active_provider_without_repair(api):
    api.post('/api/banking/reset')
    before = api.get('/api/banking/openapi')
    assert before.status_code == 200
    assert before.json()['info']['version'] == '1.0.0'
    api.post('/api/banking/controls', json={'version': 'v2', 'adapter': 'original'})
    after = api.get('/api/banking/openapi').json()
    assert after['info']['version'] == '2.0.0'
    assert '/refunds/create' in after['paths']
    api.post('/api/banking/reset')


def test_banking_checks_active_docs_not_fixed_v2_target(api):
    import dashboard_api
    from apishield.current_api import capture_api_context
    from apishield.banking import demo
    api.post('/api/examples/banking')
    jobs = dashboard_api.app.state.local_jobs
    demo.version = 'v1'
    first = capture_api_context(jobs, 'banking-example')
    assert first['accepted_hash'] == first['observed_hash']
    demo.version = 'v2'
    second = capture_api_context(jobs, 'banking-example')
    assert second['accepted_hash'] == first['accepted_hash']
    assert second['observed_hash'] != first['observed_hash']
    assert json.loads(second['target_spec'].read_text())['info']['version'] == '2.0.0'
    demo.version = 'v1'
    assert capture_api_context(jobs, 'banking-example')['accepted_hash'] == first['accepted_hash']
