import json
from apishield.configuration import load_config
from apishield.jobs import atomic_json
from test_dashboard_jobs import api, configured_source


def test_activity_returns_persisted_progress_and_redacts_output(api, tmp_path):
    import dashboard_api
    api.get('/api/workspace')
    jobs = dashboard_api.app.state.local_jobs
    job = jobs.store.create(load_config(configured_source(tmp_path)), 'repair')
    job.event('activity', stage='intent', message='Inferring behavioral checks', attempt=1)
    job.event('command_finished', label='test_1', exit_code=1, stdout='token=PRIVATE-VALUE')
    atomic_json(job.path / 'result.json', {**job._initial, 'status': 'running'})
    response = api.get(f'/api/jobs/{job.id}/activity')
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['job_id'] == job.id and data['status'] == 'running'
    assert data['events'][0]['stage'] == 'intent'
    assert data['events'][1]['exit_code'] == 1
    assert 'PRIVATE-VALUE' not in response.text
    # A concurrently appended partial line is not a completed event.
    with (job.path / 'events.jsonl').open('ab') as out:
        out.write(b'{"kind":')
    assert len(api.get(f'/api/jobs/{job.id}/activity').json()['events']) == 2


def test_activity_is_bounded_and_unknown_job_is_not_found(api, tmp_path):
    import dashboard_api
    api.get('/api/workspace')
    jobs = dashboard_api.app.state.local_jobs
    job = jobs.store.create(load_config(configured_source(tmp_path)), 'repair')
    with (job.path / 'events.jsonl').open('wb') as out:
        out.write(b'x' * (512 * 1024) + b'\n')
        for index in range(300):
            out.write((json.dumps({'kind': 'activity', 'stage': 'repair', 'message': str(index)}) + '\n').encode())
    data = api.get(f'/api/jobs/{job.id}/activity').json()
    assert data['truncated'] and len(data['events']) <= 200
    assert data['events'][-1]['message'] == '299'
    assert api.get('/api/jobs/' + '0' * 32 + '/activity').status_code == 404


def test_failed_generated_check_explains_actual_exception_and_test(api, tmp_path):
    import dashboard_api
    api.get('/api/workspace')
    jobs = dashboard_api.app.state.local_jobs
    job = jobs.store.create(load_config(configured_source(tmp_path)), 'repair')
    result = {**job._initial, 'status':'failed', 'error':'Generated checks did not execute successfully; repair is unvalidated',
        'attempts':[{'validation':[{'exit_code':1,'stdout':"E   NameError: name 'json' is not defined\nFAILED tests/apishield_generated/test_bankclient_v2.py::test_refund_v2_endpoint\n",'stderr':''}]}]}
    atomic_json(job.path / 'result.json', result)
    response = api.get(f'/api/jobs/{job.id}/activity')
    assert response.status_code == 200
    explanation = response.json()['failure_explanation']
    assert explanation['category'] == 'generated_check_error'
    assert 'NameError' in explanation['detail']
    assert 'test_refund_v2_endpoint' in explanation['test']
    assert 'not applied' in explanation['consequence']


def test_provider_deadline_failure_has_actionable_explanation():
    from apishield.activity import failure_explanation
    report = {'status': 'failed', 'error': "ServerError: 504 DEADLINE_EXCEEDED. {'error': {'message': 'Deadline expired before operation could complete.'}}"}
    explanation = failure_explanation(report)
    assert explanation['category'] == 'provider_timeout'
    assert 'Google' in explanation['summary']
    assert 'validation' in explanation['summary'].lower()
    assert "{'error'" not in explanation['detail']
