import json
from dataclasses import replace
from test_dashboard_jobs import api


def test_v1_check_v2_ai_shape_apply_and_current_graph_without_commit(api, monkeypatch):
    import dashboard_api
    from apishield.banking import demo, FIXTURE
    from apishield.configuration import load_config
    from apishield.engine import run_job
    from apishield.current_api import capture_api_context, current_overview
    from apishield.local_apply import apply_local_repair
    from test_local_engine import git
    api.post('/api/banking/reset')
    api.post('/api/examples/banking')
    jobs = dashboard_api.app.state.local_jobs
    from apishield.model_access import disabled_connection
    jobs.model_connection = disabled_connection()
    config = load_config(jobs.integrations['banking-example'])
    head = git(config.repository, 'rev-parse', 'HEAD')
    v1 = capture_api_context(jobs, 'banking-example')
    original = run_job(replace(config, source_mode='working', base_spec=v1['base_spec'], target_spec=v1['target_spec'], requirements=[]), 'compare', jobs.store)
    assert original['comparison']['changed_operations'] == []
    api.post('/api/banking/controls', json={'version': 'v2'})
    v2 = capture_api_context(jobs, 'banking-example')
    config = replace(config, source_mode='working', base_spec=v2['base_spec'], target_spec=v2['target_spec'], requirements=[])
    broken = run_job(config, 'compare', jobs.store)
    assert len(broken['impacted_sites']) == 3
    # Regression fixture stands in for model output here; production has no fixture fallback.
    monkeypatch.setattr('apishield.engine.generate_candidate', lambda *a, **k: json.loads((FIXTURE / 'candidate.json').read_text()))
    job = jobs.store.create(config, 'repair')
    job._initial.update(integration='banking-example', api_context={k: str(v) if hasattr(v, 'read_bytes') else v for k, v in v2.items()})
    repaired = run_job(config, 'repair', jobs.store, job=job)
    assert repaired['status'] == 'validated', repaired.get('error')
    before_apply = api.get(f'/api/jobs/{job.id}').json()
    assert any(n.get('impact') for n in before_apply['semantic_graph']['nodes'])
    assert 'current_graph_report' not in before_apply
    assert apply_local_repair(jobs, 'banking-example', job.id)['status'] == 'applied'
    reopened = api.get(f'/api/jobs/{job.id}')
    assert reopened.status_code == 200, reopened.text
    current_graph = reopened.json()['current_graph_report']
    assert current_graph['source_hash'] != repaired['source_hash']
    assert not any(n.get('impact') for n in current_graph['semantic_graph']['nodes'])
    assert any(n.get('endpoint') == '/refunds/create' for n in current_graph['semantic_graph']['nodes'])
    # Historical comparison/patch evidence stays intact on disk.
    assert any(n.get('impact') for n in jobs.store.get(job.id)['semantic_graph']['nodes'])
    assert git(config.repository, 'rev-parse', 'HEAD') == head
    assert api.get('/api/banking/accounts').status_code == 200
    transfer = api.post('/api/banking/transfer', json={'source':'checking','destination':'savings','amount_cents':1234})
    assert transfer.status_code == 200, transfer.text
    overview = jobs.store.get(current_overview(jobs, 'banking-example'))
    assert not any(n.get('impact') for n in overview['semantic_graph']['nodes'])
    updated = capture_api_context(jobs, 'banking-example')
    assert updated['accepted_hash'] == updated['observed_hash']
    same = run_job(replace(config, base_spec=updated['base_spec'], target_spec=updated['target_spec']), 'compare', jobs.store)
    assert same['comparison']['changed_operations'] == []
    api.post('/api/banking/reset')
