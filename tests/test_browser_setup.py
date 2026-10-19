import json
import subprocess
import time

from test_dashboard_jobs import api, configured_source
from test_requirements import RULE


def registration(tmp_path):
    config = json.loads(configured_source(tmp_path).read_text())
    return dict(name='parcel', repository=config['repository'], code_paths=['src'], test_path='tests',
                base_spec={'openapi': '3.0.3', 'info': {'title': 'Parcel', 'version': '1'}, 'paths': {}},
                target_spec={'openapi': '3.0.3', 'info': {'title': 'Parcel', 'version': '2'}, 'paths': {}})


def test_browser_requirement_versions_confirmation_and_stale_save(api, tmp_path):
    body=registration(tmp_path)
    assert api.post('/api/integrations',json=body).status_code==201
    endpoint='/api/integrations/parcel/requirements'
    initial=api.get(endpoint)
    assert initial.status_code==200
    assert initial.json()['requirements']==[]
    saved=api.put(endpoint,json={'requirements':[RULE],'expected_hash':initial.json()['edit_token']})
    assert saved.status_code==200,saved.text
    assert saved.json()['requirements'][0]['confirmed'] is False
    assert api.put(endpoint,json={'requirements':[],'expected_hash':initial.json()['edit_token']}).status_code==409
    confirmed=api.put(endpoint,json={'requirements':[RULE],'expected_hash':saved.json()['edit_token']})
    assert confirmed.status_code==200
    assert confirmed.json()['requirements'][0]['confirmed'] is True
    edited=api.put(endpoint,json={'requirements':[{**RULE,'description':'Changed rule'}],
                                'expected_hash':confirmed.json()['edit_token']})
    assert edited.json()['requirements'][0]['confirmed'] is False
    assert api.get('/api/integrations/parcel/config').json()['requirements'][0]['description']=='Changed rule'
    # Full integration edits preserve declarations rather than silently removing them.
    assert api.put('/api/integrations/parcel',json=body).status_code==200
    assert api.get(endpoint).json()['requirements'][0]['description']=='Changed rule'
    import dashboard_api
    dashboard_api.app.state.local_jobs.close()
    del dashboard_api.app.state.local_jobs
    assert api.get(endpoint).json()['requirements'][0]['description']=='Changed rule'


def test_requirement_update_boundaries_and_failed_save_integrity(api,tmp_path):
    assert api.post('/api/integrations',json=registration(tmp_path)).status_code==201
    endpoint='/api/integrations/parcel/requirements'
    before=api.get(endpoint).json()
    payload={'requirements':[RULE],'expected_hash':before['edit_token']}
    assert api.put(endpoint,json=payload,headers={'Origin':'https://evil.test'}).status_code==403
    assert api.put(endpoint,json={**payload,'requirements':[{**RULE,'checks':['--help']}]}).status_code==422
    assert api.get(endpoint).json()==before
    import dashboard_api
    jobs=dashboard_api.app.state.local_jobs
    jobs.integrations['managed']=str(configured_source(tmp_path/'managed'))
    info=api.get('/api/integrations/managed/requirements')
    assert info.status_code==200
    assert info.json()['editable'] is False
    assert api.put('/api/integrations/managed/requirements',json=payload).status_code==403


def test_example_requirement_and_historical_snapshot(api):
    assert api.post('/api/examples/shipping').status_code==201
    endpoint='/api/integrations/shipping-example/requirements'
    rules=api.get(endpoint)
    assert rules.status_code==200
    assert rules.json()['requirements'][0]['confirmed'] is True
    assert rules.json()['editable'] is False
    response=api.put(endpoint,json={'requirements':[],'expected_hash':rules.json()['edit_token']})
    assert response.status_code==403


def test_requirement_edit_preserves_job_snapshot(api,tmp_path):
    assert api.post('/api/integrations',json=registration(tmp_path)).status_code==201
    endpoint='/api/integrations/parcel/requirements'
    before=api.get(endpoint).json()
    saved=api.put(endpoint,json={'requirements':[RULE],'expected_hash':before['edit_token']}).json()
    api.put(endpoint,json={'requirements':[RULE],'expected_hash':saved['edit_token']})
    import dashboard_api
    from apishield.configuration import load_config
    from apishield.engine import run_job
    jobs=dashboard_api.app.state.local_jobs
    config=load_config(jobs.integrations['parcel'])
    result=run_job(config,'scan',jobs.store)
    path=jobs.store._path(result['job_id'])
    retained={name:(path/name).read_bytes() for name in ['config.json','result.json','source.json']}
    now=api.get(endpoint).json()
    api.put(endpoint,json={'requirements':[],'expected_hash':now['edit_token']})
    assert result['requirements'][0]['confirmed'] is True
    assert all((path/name).read_bytes()==data for name,data in retained.items())


def test_old_example_rules_refresh_without_rewriting_original_version(api):
    assert api.post('/api/examples/shipping').status_code==201
    import dashboard_api
    from pathlib import Path
    jobs=dashboard_api.app.state.local_jobs
    old=Path(jobs.integrations['shipping-example'])
    raw=json.loads(old.read_text())
    raw.pop('requirements')
    old.write_text(json.dumps(raw))
    original=old.read_bytes()
    repo=Path(raw['repository'])
    source=(repo/'src/parcel.py').read_bytes()
    assert api.get('/api/integrations/shipping-example/requirements').json()['requirements'][0]['confirmed'] is True
    assert jobs.integrations['shipping-example'] != str(old)
    assert old.read_bytes()==original
    assert (repo/'src/parcel.py').read_bytes()==source


def test_repository_changes_clear_confirmation_and_invalidate_even_draft_editors(api,tmp_path):
    body=registration(tmp_path)
    assert api.post('/api/integrations',json=body).status_code==201
    endpoint='/api/integrations/parcel/requirements'
    data=api.get(endpoint).json()
    saved=api.put(endpoint,json={'requirements':[RULE],'expected_hash':data['edit_token']}).json()
    confirmed=api.put(endpoint,json={'requirements':[RULE],'expected_hash':saved['edit_token']}).json()
    second=registration(tmp_path/'second')
    assert api.put('/api/integrations/parcel',json={**second,'name':'parcel'}).status_code==200
    current=api.get(endpoint).json()
    assert current['requirements'][0]['confirmed'] is False
    assert api.put(endpoint,json={'requirements':[RULE],'expected_hash':confirmed['edit_token']}).status_code==409
    # Even an unconfirmed editor must become stale after changing source context.
    assert api.put('/api/integrations/parcel',json=body).status_code==200
    assert api.put(endpoint,json={'requirements':current['requirements'],
                                  'expected_hash':current['edit_token']}).status_code==409


def test_browser_registration_persists_and_does_not_accept_commands(api, tmp_path):
    body = registration(tmp_path)
    assert api.post('/api/integrations', json={**body, 'test_commands': [['cmd']]}).status_code == 422
    response = api.post('/api/integrations', json=body)
    assert response.status_code == 201, response.text
    assert 'parcel' in api.get('/api/integrations').json()['integrations']
    import dashboard_api
    dashboard_api.app.state.local_jobs.close()
    del dashboard_api.app.state.local_jobs
    workspace = api.get('/api/workspace').json()
    assert workspace['integrations'][0]['name'] == 'parcel'
    assert workspace['integrations'][0]['repository'] == body['repository']


def test_browser_setup_rejects_foreign_origin(api, tmp_path):
    body = registration(tmp_path)
    assert api.post('/api/integrations', json=body, headers={'Origin': 'https://evil.example'}).status_code == 403
    assert api.post('/api/integrations', json=body, headers={'Host': 'evil.example'}).status_code == 403


def test_browser_setup_rejects_storage_inside_source(api, tmp_path):
    body = registration(tmp_path)
    subprocess.run(['git', 'init', str(tmp_path)], check=True, capture_output=True)
    body['repository'] = str(tmp_path)
    response = api.post('/api/integrations', json=body)
    assert response.status_code == 422, response.text


def test_shipping_example_has_real_validated_patch(api):
    response = api.post('/api/examples/shipping')
    assert response.status_code == 201, response.text
    integration = response.json()['name']
    workspace = api.get('/api/workspace').json()
    detail = next(item for item in workspace['integrations'] if item['name'] == integration)
    from pathlib import Path
    source = Path(detail['repository']) / 'src/parcel.py'
    before = source.read_bytes()
    response = api.post('/api/jobs', json={'integration': integration, 'operation': 'repair', 'proposal': 'example'})
    assert response.status_code == 422, response.text
    import dashboard_api
    from apishield.configuration import load_config
    from apishield.engine import run_job
    jobs = dashboard_api.app.state.local_jobs
    result = run_job(load_config(jobs.integrations[integration]), 'repair', jobs.store,
                     candidate_path=jobs.example_candidates[integration])
    job_id = result['job_id']
    assert result['status'] == 'validated', result
    assert result['attempts'][0]['validation'][0]['exit_code'] == 0
    assert '/labels/create' in api.get(f'/api/jobs/{job_id}/patch').text
    assert source.read_bytes() == before


def test_example_proposal_cannot_be_used_on_user_integration(api, tmp_path):
    assert api.post('/api/integrations', json=registration(tmp_path)).status_code == 201
    response = api.post('/api/jobs', json={'integration': 'parcel', 'operation': 'repair', 'proposal': 'example'})
    assert response.status_code == 422, response.text


def test_reading_untouched_queue_does_not_take_worker_lock(tmp_path, monkeypatch):
    from apishield import engine
    from apishield.configuration import load_config
    from apishield.jobs import JobStore
    store = JobStore(tmp_path / 'jobs')
    job = store.create(load_config(configured_source(tmp_path)), 'scan')
    def lock_must_not_be_taken(*args):
        raise AssertionError('Report reader competed with starting worker')
    monkeypatch.setattr(engine, '_execution_lock', lock_must_not_be_taken)
    assert engine.recover_interrupted(store, job.id)['status'] == 'queued'


def test_retired_api_key_route_never_accepts_or_echoes_credentials(api):
    key = 'sensitive-test-key-' + 'x' * 1024
    response = api.post('/api/settings/model', json={'key': key})
    assert response.status_code in {404, 405, 410}
    assert key not in response.text
    assert api.get('/api/workspace').json()['model_available'] is False


def test_browser_can_update_contracts_without_losing_valid_configuration(api, tmp_path):
    body = registration(tmp_path)
    assert api.post('/api/integrations', json=body).status_code == 201
    edited = {**body, 'target_spec': {**body['target_spec'], 'info': {'title':'Parcel','version':'3'}}}
    assert api.put('/api/integrations/parcel', json=edited).status_code == 200
    assert api.get('/api/integrations/parcel/config').json()['target_spec']['info']['version'] == '3'
    assert api.put('/api/integrations/parcel', json={**edited,'repository':str(tmp_path/'missing')}).status_code == 422
    assert api.get('/api/integrations/parcel/config').json()['target_spec']['info']['version'] == '3'
