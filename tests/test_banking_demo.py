import pytest
from apishield.banking import BankingDemo
from test_dashboard_jobs import api


def test_breaking_provider_does_not_move_money_and_supplied_adapter_preserves_cents():
    demo = BankingDemo()
    initial = demo.snapshot()['accounts'][0]['balance_cents']
    demo.version = 'v2'
    with pytest.raises(Exception):
        demo.transfer('checking', 'savings', 1234)
    assert demo.snapshot()['accounts'][0]['balance_cents'] == initial
    demo.repaired = True
    transfer = demo.transfer('checking', 'savings', 1234)
    assert transfer['amount_cents'] == 1234
    assert demo.snapshot()['accounts'][0]['balance_cents'] == initial - 1234
    demo.refund(transfer['id'])
    assert demo.snapshot()['accounts'][0]['balance_cents'] == initial
    with pytest.raises(Exception):
        demo.refund(transfer['id'])
    assert demo.snapshot()['accounts'][0]['balance_cents'] == initial


def test_invalid_transfer_is_atomic_and_history_is_real():
    demo = BankingDemo()
    original = demo.snapshot()
    for value in (0, -1, 999999999):
        with pytest.raises(Exception):
            demo.transfer('checking', 'savings', value)
    assert demo.snapshot() == original
    demo.transfer('checking', 'savings', 2500)
    assert len(demo.snapshot()['transactions']) == 1


def test_banking_api_is_local_and_rejects_fractional_cents(api):
    assert api.post('/api/banking/reset').status_code == 200
    assert api.post('/api/banking/transfer', json={'source':'checking','destination':'savings','amount_cents':12.3}).status_code == 422
    assert api.post('/api/banking/transfer', json={'source':'checking','destination':'savings','amount_cents':1234}, headers={'Origin':'https://evil.test'}).status_code == 403
    assert api.post('/api/banking/controls',json={'version':'v2','adapter':'original'}).status_code == 200
    assert api.get('/api/banking/accounts').status_code == 422
    assert api.post('/api/banking/controls',json={'version':'v2','adapter':'supplied_v2'}).status_code == 422
    assert api.get('/api/banking/accounts').status_code == 422
    assert api.post('/api/banking/reset').status_code == 200


def test_banking_example_registers_real_graph_and_validates_supplied_repair(api):
    from apishield.configuration import load_config
    from apishield.engine import run_job
    import dashboard_api
    response = api.post('/api/examples/banking')
    assert response.status_code == 201, response.text
    jobs = dashboard_api.app.state.local_jobs
    config = load_config(jobs.integrations['banking-example'])
    comparison = run_job(config, 'compare', jobs.store)
    assert comparison['status'] == 'completed', comparison.get('error')
    assert len(comparison['impacted_sites']) == 3
    nodes = comparison['semantic_graph']['nodes']
    assert any(n.get('function') == 'sendMoney' and n.get('impact') == 'potential' for n in nodes)
    assert any(n.get('function') == 'accounts' and not n.get('impact') for n in nodes)
    repaired = run_job(config, 'repair', jobs.store, candidate_path=jobs.example_candidates['banking-example'])
    assert repaired['status'] == 'validated', repaired.get('error')


def test_banking_page_opens_directly_without_hiding_missing_api_routes(api):
    response = api.get('/banking')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/html')
    assert '<div id="root">' in response.text
    assert api.get('/api/banking/not-a-route').status_code == 404


def test_reset_restores_working_v1_code_funds_and_accepted_contract(api):
    import dashboard_api
    from apishield.banking import FIXTURE
    from apishield.configuration import load_config
    from apishield.current_api import capture_api_context
    from apishield.jobs import atomic_json
    api.post('/api/banking/reset').raise_for_status()
    api.post('/api/examples/banking').raise_for_status()
    jobs = dashboard_api.app.state.local_jobs
    root = load_config(jobs.integrations['banking-example']).repository
    api.post('/api/banking/transfer', json={'source': 'checking', 'destination': 'savings', 'amount_cents': 2500}).raise_for_status()
    api.post('/api/banking/controls', json={'version': 'v2'}).raise_for_status()
    context = capture_api_context(jobs, 'banking-example')
    atomic_json(jobs.store.root / '_current_api/banking-example/state.json',
                {'config_identity': context['config_identity'], 'accepted_hash': context['observed_hash']})
    source = root / 'src/bankclient.py'
    source.write_text(source.read_text() + '\n# Previously applied migration\n')
    for _ in range(2):
        result = api.post('/api/banking/reset')
        result.raise_for_status()
        state = result.json()
        assert state['version'] == 'v1' and not state['repaired']
        assert [a['balance_cents'] for a in state['accounts']] == [125000, 300000]
        assert state['transactions'] == []
        assert source.read_bytes() == (FIXTURE / 'src/bankclient.py').read_bytes()
        reset_context = capture_api_context(jobs, 'banking-example')
        assert reset_context['accepted_hash'] == reset_context['observed_hash']
        assert api.get('/api/banking/accounts').status_code == 200
